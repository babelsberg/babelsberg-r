from rupypy.module import ClassDef
from rupypy.objects.objectobject import W_Object

class W_ConstraintObject(W_Object):
    classdef = ClassDef("Constraint", W_Object.classdef)

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
        import pdb; pdb.set_trace()
        for w_value, cell in self.w_test_block.get_closure_variables():
            instances_w = space.listview(space.send(self, space.newsymbol("instances_for"), [w_value]))
            for w_obj in instances_w:
                # cell is closure cell, so not stored in frame
                cell.set(None, None, w_obj)
                if space.istrue(space.invoke_block(self.w_test_block, [])):
                    return self.w_true
            cell.set(w_value)
        raise self.error(
            self.w_RuntimeError,
            "unsatisfiable constraint %s" % self.str_w(self.send(
                    w_constraint, self.newsymbol("inspect")
            ))
        )
        # return space.send(self.w_correct_proc, space.newsymbol("[]"))

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
