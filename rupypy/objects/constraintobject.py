from rupypy.module import ClassDef, Module, ModuleDef
from rupypy.objects.objectobject import W_Object
from rupypy.utils.cache import Cache


class W_ConstraintVariableObject(W_Object):
    classdef = ClassDef("ConstraintVariable", W_Object.classdef, filepath=__file__)

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
        self.w_external_variable = space.w_nil

    def __del__(self):
        # TODO: remove external variable from solver
        pass

    def load_value(self, space):
        if self.cell:
            return self.cell.get(None, 0) or space.w_nil
        elif self.ivar is not None:
            return self.w_owner.find_instance_var(space, self.ivar) or space.w_nil
        elif self.cvar is not None:
            return self.w_owner.find_class_var(space, self.cvar) or space.w_nil
        else:
            raise NotImplementedError("inconsistent constraint variable")

    def store_value(self, space, w_value):
        if self.cell:
            self.cell.set(None, 0, w_value)
        elif self.ivar is not None:
            self.w_owner.set_instance_var(space, self.ivar, w_value)
        elif self.cvar is not None:
            self.w_owner.set_class_var(space, self.cvar, w_value)
        else:
            raise NotImplementedError("inconsistent constraint variable")

    def get_external_variable(self, space):
        if self.w_external_variable is space.w_nil:
            self.w_external_variable = space.send(self, space.newsymbol("create_variable"))
        return self.w_external_variable

    @classdef.method("suggest_value")
    def method_suggest_value(self, space, w_value):
        space.send(self.get_external_variable(space), "suggest_value", [w_value])
        return w_value

    @classdef.method("value")
    def method_value(self, space):
        return self.load_value(space)

    @classdef.method("name")
    def method_name(self, space):
        clsname = space.getclass(self.load_value(space)).name
        if self.cell:
            return space.newstr_fromstr("local-%s" % clsname)
        elif self.ivar is not None:
            return space.newstr_fromstr("ivar-%s" % clsname)
        elif self.cvar is not None:
            return space.newstr_fromstr("cvar-%s" % clsname)
        return space.w_nil

    @classdef.method("variable")
    def method_variable(self, space):
        return get_external_variable(space)

    @classdef.method("set!")
    def method_set_i(self, space):
        w_evar = self.get_external_variable(space)
        w_value = space.send(w_evar, space.newsymbol("value"))
        self.store_value(space, w_value)
        return w_value

    classdef.app_method("""
    def create_variable
      block = nil
      value.class.ancestors.each do |klass|
        block = Constraints.variable_handlers[klass]
        break if block
      end
      if block
        return block[name, value]
      else
        raise "no solver registered for #{value.class}s"
      end
    end

    def ==(other)
      variable == (other.kind_of?(self.class) ? other.variable : other)
    end

    def method_missing(method, *args, &block)
      if variable.respond_to? method
        args = args.map do |arg|
          arg.kind_of?(self.class) ? arg.variable : arg
        end
        variable.send(method, *args, &block)
      else
        value.send(method, *args, &block)
      end
    end
    """)


class Constraints(Module):
    moduledef = ModuleDef("Constraints", filepath=__file__)

    moduledef.app_method("""
    def self.variable_handlers
      @variable_handlers ||= {}
    end

    def self.for_variables_of_type(klass, &block)
      variable_handlers[klass] = block
    end
    """)

    @moduledef.function("register_solver")
    def method_register_solver(self, space, w_solver):
        return space.newbool(space.add_constraint_solver(w_solver))

    @moduledef.function("deregister_solver")
    def method_deregister_solver(self, space, w_solver):
        return space.newbool(space.remove_constraint_solver(w_solver))
