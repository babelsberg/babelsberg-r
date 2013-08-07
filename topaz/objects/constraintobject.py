from rpython.rlib import jit

from topaz.celldict import CellDict, VersionTag
from topaz.module import ClassDef, ModuleDef
from topaz.objects.hashobject import W_HashObject
from topaz.objects.objectobject import W_Object, W_RootObject
from topaz.objects.procobject import W_ProcObject
from topaz.utils.cache import Cache


# Marker class for constraint solver objects
class W_ConstraintMarkerObject(W_Object):
    _attrs_ = []
    classdef = ClassDef("ConstraintObject", W_Object.classdef)

    @classdef.singleton_method("allocate")
    def singleton_method_allocate(self, space):
        return W_ConstraintMarkerObject(space, self)

    @classdef.method("and")
    def method_and(self, space, w_rhs):
        if space.is_constructing_constraint():
            w_constraint = space.current_constraint()
            w_constraint.add_constraint_object(self)
            return w_rhs
        else:
            return space.send(
                self,
                "method_missing",
                [space.newstr_fromstr("and"), w_rhs]
            )

class W_ConstraintObject(W_ConstraintMarkerObject):
    _attrs_ = ["w_strength", "block", "enabled",
               "constraint_objects_w", "constraint_variables_w"]
    classdef = ClassDef("Constraint", W_ConstraintMarkerObject.classdef)

    def __init__(self, space):
        W_Object.__init__(self, space)
        self.w_strength = None
        self.block = None
        self.enabled = False
        self.constraint_objects_w = []
        self.constraint_variables_w = []
        self.assignments_w = CellDict()

    def get_constraint_objects(self):
        return self.constraint_objects_w

    def add_constraint_object(self, w_value):
        self.constraint_objects_w.append(w_value)

    def remove_constraint_objects(self):
        del self.constraint_objects_w[:]

    def has_constraint_objects(self):
        return len(self.constraint_objects_w) > 0

    def add_constraint_variable(self, w_value):
        if w_value not in self.constraint_variables_w:
            self.constraint_variables_w.append(w_value)

    def add_assignment(self, space, c_var, w_constraint):
        if self.assignments_w.get(c_var):
            raise space.error(
                space.w_RuntimeError,
                "multiply assigned variable in constraint execution"
            )
        self.assignments_w.set(c_var, w_constraint)

    @classdef.method("enable")
    def method_enable(self, space):
        if not self.enabled:
            for w_constraint_object in self.constraint_objects_w:
                self.enable_constraint_object(space, w_constraint_object)
            self.enabled = True
            return space.w_true
        else:
            return space.w_nil

    def enable_constraint_object(self, space, w_constraint_object):
        if w_constraint_object is space.w_true:
            w_stderr = space.find_const(space.w_object, "STDERR")
            assert isinstance(w_stderr, W_RootObject)
            space.send(
                w_stderr,
                "puts",
                [space.newstr_fromstr("Warning: Constraint expression returned true, re-running it whenever the value changes")]
            )
        elif w_constraint_object is space.w_false or w_constraint_object is space.w_nil:
            raise space.error(
                space.w_ArgumentError,
                "constraint block returned false-y, cannot assert that (did you `require' your solver?)"
            )
        elif not space.respond_to(w_constraint_object, "enable"):
            raise space.error(
                space.w_TypeError,
                ("constraint block did an object (%s:%s) that doesn't respond to #enable " +
                 "(did you `require' your solver?)") % (
                     space.any_to_s(w_constraint_object),
                     space.getclass(w_constraint_object).name
                 )
            )
        else:
            arg_w = [] if self.w_strength is None else [self.w_strength]
            space.send(w_constraint_object, "enable", arg_w)

    @classdef.method("disable")
    def method_disable(self, space):
        if self.enabled:
            for w_constraint_object in self.constraint_objects_w:
                if space.respond_to(w_constraint_object, "disable"):
                    space.send(w_constraint_object, "disable")
            self.enabled = False
            return space.w_true
        else:
            return space.w_nil

    @classdef.method("recalculate")
    def method_recalculate(self, space):
        if self.enabled:
            space.send(self, "disable")
            del self.constraint_objects_w[:]
            self.run_predicate(space)
            space.send(self, "enable")

    def run_predicate(self, space):
        with space.constraint_construction(self):
            w_constraint_object = space.invoke_block(self.block, [])
            self.add_constraint_object(w_constraint_object)

    @classdef.method("primitive_constraints")
    def method_solver_constraints(self, space):
        return space.newarray(self.constraint_objects_w[:])

    @classdef.method("constraint_variables")
    def method_solver_constraints(self, space):
        vars_w = []
        for w_var in self.constraint_variables_w:
            if w_var.is_solveable():
                vars_w.append(w_var.w_external_variable)
        return space.newarray(vars_w)

    @classdef.method("predicate")
    def method_constraint_block(self, space):
        return self.block

    @classdef.method("strength")
    def method_strength(self, space):
        return self.w_strength

    @classdef.method("strength=")
    def method_strength(self, space, w_strength):
        enabled = self.enabled
        if enabled:
            space.send(self, "disable")
        self.w_strength = w_strength
        if enabled:
            space.send(self, "enable")
        return self.w_strength

    @classdef.method("initialize")
    def method_initialize(self, space, w_strength=None, block=None):
        if not block:
            raise space.error(space.w_ArgumentError, "no constraint predicate given")
        if self.block:
            raise space.error(space.w_ArgumentError, "cannot re-initialize Constraint")
        self.w_strength = w_strength
        self.block = block
        self.run_predicate(space)
        return self

    @classdef.singleton_method("allocate")
    def singleton_method_allocate(self, space):
        return W_ConstraintObject(space)

    @classdef.method("value")
    def method_return_value(self, space):
        # last added constraint object is the return value
        return self.constraint_objects_w[-1]
