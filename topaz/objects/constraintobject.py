from rpython.rlib import jit

from topaz.module import ClassDef, ModuleDef
from topaz.objects.hashobject import W_HashObject
from topaz.objects.objectobject import W_Object, W_RootObject
from topaz.objects.procobject import W_ProcObject
from topaz.utils.cache import Cache


# Marker class for constraint solver objects
class W_ConstraintObject(W_Object):
    classdef = ClassDef("ConstraintObject", W_Object.classdef, filepath=__file__)


class W_ConstraintVariableObject(W_RootObject):
    _immutable_fields_ = ["cell", "w_owner", "ivar", "cvar", "w_external_variable"]

    classdef = ClassDef("ConstraintVariable", W_ConstraintObject.classdef, filepath=__file__)

    def __init__(self, space, cell=None, w_owner=None, ivar=None, cvar=None):
        self.w_external_variable = None
        self.cell = None
        self.w_owner = None
        self.ivar = None
        self.cvar = None
        self.constraint_blocks = []
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

        w_value = self.load_value(space)
        w_class = space.getclass(w_value)
        if space.getsingletonclass(w_class).find_method(space, "for_constraint"):
            with space.normal_execution():
                self.w_external_variable = space.send(
                    w_class,
                    space.newsymbol("for_constraint"),
                    [self.get_name(space), w_value]
                )

    def __del__(self):
        # TODO: remove external variable from solver
        pass

    def is_solveable(self):
        return self.w_external_variable is not None

    def add_constraint_block(self, block):
        self.constraint_blocks.append(block)

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
        return self.w_external_variable or space.w_nil

    @classdef.method("set!")
    def method_set_i(self, space):
        if self.w_external_variable is not None:
            # This variable is part of the solver. Get the solvers
            # interpretation and store it
            w_value = space.send(self.w_external_variable, space.newsymbol("value"))
            if w_value != space.w_nil:
                self.store_value(space, w_value)
            return w_value
        return space.w_nil

    @classdef.method("get!")
    def method_get_i(self, space):
        self.method_set_i(space)
        return self.load_value(space)

    @classdef.method("recalculate_path")
    def method_recalculate_path(self, space, w_value):
        self.store_value(space, w_value)
        for block in self.constraint_blocks:
            w_constraint = block.get_constraint()
            assert w_constraint
            space.send(w_constraint, space.newsymbol("disable"))
            block.set_constraint(None)
            space.send(space.w_object, space.newsymbol("always"), block=block)
