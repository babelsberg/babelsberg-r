from rupypy.module import ClassDef
from rupypy.objects.objectobject import W_Object
from rupypy.objects.arrayobject import W_ArrayObject


class W_SexprObject(W_ArrayObject):
    classdef = ClassDef("Sexpr", W_ArrayObject.classdef, filepath=__file__)

    @classdef.singleton_method("new")
    def method_new(self, space, args_w):
        raise space.error(space.w_TypeError, "Sexpr cannot be initialized from user code")

    @classdef.singleton_method("allocate")
    def method_allocate(self, space):
        raise space.error(space.w_TypeError, "no allocator for Sexpr")

    classdef.app_method("""
    def to_s
      result = "("
      self.each_with_index do |obj, i|
        if i > 0
          result << ", "
        end
        result << obj.to_s
      end
      result << ")"
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
        pass
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
