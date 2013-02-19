from topaz.module import ClassDef, Module, ModuleDef
from topaz.objects.hashobject import W_HashObject
from topaz.objects.objectobject import W_Object
from topaz.objects.procobject import W_ProcObject
from topaz.utils.cache import Cache


# Marker class for constraint solver objects
class W_ConstraintObject(W_Object):
    classdef = ClassDef("ConstraintObject", W_Object.classdef, filepath=__file__)


class W_ConstraintVariableObject(W_ConstraintObject):
    classdef = ClassDef("ConstraintVariable", W_ConstraintObject.classdef, filepath=__file__)

    def __init__(self, space, cell=None, w_owner=None, ivar=None, cvar=None):
        W_Object.__init__(self, space)
        self.cell = None
        self.w_owner = None
        self.ivar = None
        self.cvar = None
        if cell:
            self.cell = cell
        elif w_owner and ivar:
            self.w_owner = w_owner
            self.ivar = ivar
        elif w_owner and cvar:
            self.w_owner = w_owner
            self.cvar = cvar
        else:
            raise RuntimeError("Invalid ConstraintVariableObject initialization")
        self.w_external_variable = None

    def __del__(self):
        # TODO: remove external variable from solver
        pass

    def load_value(self, space):
        if self.cell:
            return self.cell.get(space, None, 0) or space.w_nil
        elif self.ivar is not None:
            return self.w_owner.find_instance_var(space, self.ivar) or space.w_nil
        elif self.cvar is not None:
            return self.w_owner.find_class_var(space, self.cvar) or space.w_nil
        else:
            raise NotImplementedError("inconsistent constraint variable")

    def store_value(self, space, w_value):
        if self.cell:
            self.cell.set(space, None, 0, w_value)
        elif self.ivar is not None:
            self.w_owner.set_instance_var(space, self.ivar, w_value)
        elif self.cvar is not None:
            self.w_owner.set_class_var(space, self.cvar, w_value)
        else:
            raise NotImplementedError("inconsistent constraint variable")

    def get_external_variable(self, space):
        if self.w_external_variable is None:
            w_proc = None
            w_value = self.load_value(space)
            w_hash = space.find_instance_var(space.w_constraints, "@variable_handlers")
            if not isinstance(w_hash, W_HashObject):
                return None
            for w_mod in space.getclass(w_value).ancestors(include_singleton=False):
                try:
                    w_proc = w_hash.contents[w_mod]
                except KeyError:
                    pass
                if w_proc:
                    break
            if w_proc:
                if not isinstance(w_proc, W_ProcObject):
                    raise space.error(
                        space.w_TypeError,
                        "non-proc in constraint variable handlers"
                    )
                else:
                    with space.normal_execution():
                        self.w_external_variable = space.invoke_block(
                            w_proc.block,
                            [self.get_name(space), w_value]
                        )
        return self.w_external_variable

    def get_name(self, space):
        clsname = space.getclass(self.load_value(space)).name
        if self.cell:
            return space.newstr_fromstr("local-%s" % clsname)
        elif self.ivar is not None:
            return space.newstr_fromstr("ivar-%s" % clsname)
        elif self.cvar is not None:
            return space.newstr_fromstr("cvar-%s" % clsname)
        return space.w_nil

    @classdef.method("value")
    def method_value(self, space):
        return self.load_value(space)

    @classdef.method("name")
    def method_name(self, space):
        return self.get_name(space)

    @classdef.method("variable")
    def method_variable(self, space):
        return self.get_external_variable(space)

    @classdef.method("set!")
    def method_set_i(self, space):
        w_evar = self.get_external_variable(space)
        w_value = space.send(w_evar, space.newsymbol("value"))
        self.store_value(space, w_value)
        return w_value


class Constraints(Module):
    moduledef = ModuleDef("Constraints", filepath=__file__)

    @moduledef.function("register_solver")
    def method_register_solver(self, space, w_solver):
        return space.newbool(space.add_constraint_solver(w_solver))

    @moduledef.function("deregister_solver")
    def method_deregister_solver(self, space, w_solver):
        return space.newbool(space.remove_constraint_solver(w_solver))
