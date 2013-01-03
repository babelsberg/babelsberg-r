from rupypy.module import ClassDef
from rupypy.objects.objectobject import W_Object
from rupypy.utils.cache import Cache


class W_ConstraintVariableObject(W_Object):
    classdef = ClassDef("ConstraintVariable", W_Object.classdef, filepath=__file__)

    def __init__(self, space, cell=None, w_owner=None, ivar=None,
                 cvar=None, gvar=None):
        W_Object.__init__(self, space)
        self.cell = cell
        self.w_owner = w_owner
        self.ivar = ivar
        self.cvar = cvar
        self.gvar = gvar
        assert cell or (w_owner and (ivar or cvar )) or gvar
        self.value = self.get_value(space)

    def get_value(self, space):
        if self.cell:
            return self.cell.get(None, 0) or space.w_nil
        elif self.ivar is not None:
            return self.w_owner.find_instance_var(space, self.ivar) or space.w_nil
        elif self.cvar is not None:
            return self.w_owner.find_class_var(space, self.cvar) or space.w_nil
        elif self.gvar is not None:
            return space.globals.get(space, self.gvar) or space.w_nil
        else:
            raise NotImplementedError("inconsistent constraint variable")

    def set_value(self, space, w_value):
        if self.cell:
            self.cell.set(None, 0, w_value)
        elif self.ivar is not None:
            self.w_owner.set_instance_var(space, self.ivar, w_value)
        elif self.cvar is not None:
            self.w_owner.set_class_var(space, self.cvar, w_value)
        elif self.gvar is not None:
            space.globas.set(space, self.gvar, w_value)
        else:
            raise NotImplementedError("inconsistent constraint variable")

    @classdef.method("value")
    def method_value(self, space):
        return self.get_value(space)

    @classdef.method("name")
    def method_name(self, space):
        if self.cell:
            return space.newstr_fromstr(
                "local-%s" % space.getclass(self.value).name
            )
        elif self.ivar is not None:
            return space.newstr_fromstr(self.ivar)
        elif self.cvar is not None:
            return space.newstr_fromstr(self.cvar)
        elif self.gvar is not None:
            return space.newstr_fromstr(self.gvar)
        else:
            raise NotImplementedError("inconsistent constraint variable")

    def get_variable(self, space):
        if self.cell:
            return self.cell.get_constraint()
        else:
            raise NotImplementedError("constraints for ivars/cvars/gvars")

    def set_variable(self, space, w_constraint):
        if self.cell:
            self.cell.set_constraint(w_constraint)
        else:
            raise NotImplementedError("constraints for ivars/cvars/gvars")

    @classdef.method("variable")
    def method_variable(self, space):
        w_constraint = self.get_variable(space)
        if not w_constraint:
            w_constraint = space.send(self, space.newsymbol("create_variable"))
            self.set_variable(space, w_constraint)
        return w_constraint

    @classdef.method("set_impl")
    def method_set_impl(self, space, w_value):
        self.set_value(space, w_value)
        return w_value

    classdef.app_method("""
    def self.variable_handlers
      @variable_handlers ||= {}
    end

    def self.for_variables_of_type(klass, &block)
      variable_handlers[klass] = block
    end

    def set!
      set_impl(variable.value)
    end

    def create_variable
      block = nil
      value.class.ancestors.each do |klass|
        block = self.class.variable_handlers[klass]
        break if block
      end
      if block
        var = block[name, value]
        var.instance_variable_set("@_constraintvariable", self)
        var
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


class W_ConstraintObject(W_Object):
    classdef = ClassDef("Constraint", W_Object.classdef, filepath=__file__)

    def __init__(self, space, priority, w_test_block):
        W_Object.__init__(self, space)
        self.priority = priority
        self.w_test_block = w_test_block

    def get_priority(self):
        return self.priority

    @classdef.method("inspect")
    def method_inspect(self, space):
        return space.newstr_fromstr("#<%s:0x%x priority:%d>" % (
            space.str_w(space.send(space.getclass(self), space.newsymbol("name"))),
            space.int_w(space.send(self, space.newsymbol("__id__"))),
            self.priority
        ))

    @classdef.method("satisfied?")
    def method_satisfiedp(self, space):
        return space.invoke_block(self.w_test_block, [])

    @classdef.method("satisfy!")
    def method_satisfyb(self, space):
        return space.w_nil
        # XXX: Old code below for limited-domain solver
        # for w_value, cell in self.w_test_block.get_closure_variables():
        #     instances_w = space.listview(space.send(self, space.newsymbol("instances_for"), [w_value]))
        #     for w_obj in instances_w:
        #         # cell is closure cell, so not stored in frame, indices are meaningless
        #         cell.set(0, 0, w_obj)
        #         if space.is_true(space.invoke_block(self.w_test_block, [])):
        #             return self.w_true
        #     # cell is closure cell, so not stored in frame, indices are meaningless
        #     cell.set(0, 0, w_value)
        # raise space.error(
        #     space.w_RuntimeError,
        #     "unsatisfiable constraint %s" % space.str_w(space.send(
        #             self, space.newsymbol("inspect")
        #     ))
        # )

    classdef.app_method("""
    def instances_for(object)
      instances = []
      ObjectSpace.each_object(object.class) do |o|
        instances << o
      end
      instances
    end
    """)

    @classdef.method("priority")
    def method_priority(self, space):
        return space.newint(self.priority)

    @classdef.method("enable")
    def method_constraint(self, space):
        return space.add_constraint(self)

    @classdef.method("disable")
    def method_constraint(self, space):
        return space.remove_constraint(self)

    @classdef.singleton_method("new", priority="int")
    def method_new(self, space, priority, block):
        w_obj = W_ConstraintObject(space, priority, block)
        space.send(w_obj, space.newsymbol("initialize"))
        return w_obj

    @classdef.singleton_method("allocate")
    def method_allocate(self, space):
        raise space.error(space.w_TypeError, "no allocator for Constraints. Use .new")
