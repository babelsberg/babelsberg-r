from rpython.rlib import jit

from topaz.celldict import CellDict, VersionTag
from topaz.constraintinterpreter import ConstrainedVariable
from topaz.module import ClassDef, ModuleDef
from topaz.objects.hashobject import W_HashObject
from topaz.objects.objectobject import W_Object, W_RootObject
from topaz.objects.procobject import W_ProcObject
from topaz.utils.cache import Cache


# Marker class for constraint solver objects
class W_ConstraintMarkerObject(W_Object):
    _attrs_ = []
    classdef = ClassDef("ConstraintObject", W_Object.classdef)

    def api(classdef, name):
        @classdef.method(name)
        def method(self, space, args_w):
            raise space.error(
                space.w_NotImplementedError,
                "%s should have implemented %s" % (
                    space.getclass(self).name,
                    name
                )
            )
    api(classdef, "begin_assign") # assert equality constraint
    api(classdef, "assign")       # run solver
    api(classdef, "end_assign")   # remove equality constraint
    api(classdef, "value")        # current value
    api(classdef, "readonly!")    # make read-only
    api(classdef, "writable!")    # make writable
    api(classdef, "finalize")     # remove from solver internal structure

    @classdef.singleton_method("allocate")
    def singleton_method_allocate(self, space):
        return W_ConstraintMarkerObject(space, self)

    @classdef.method("and")
    def method_and(self, space, w_rhs):
        w_constraint = space.current_constraint()
        if w_constraint:
            w_constraint.add_constraint_object(self)
            return w_rhs
        else:
            return space.send(
                self,
                "method_missing",
                [space.newstr_fromstr("and"), w_rhs]
            )

    @classdef.method("or")
    def method_or(self, space, w_rhs):
        w_constraint = space.current_constraint()
        if w_constraint:
            w_constraint.add_constraint_object(self)
            return self
        else:
            return space.send(
                self,
                "method_missing",
                [space.newstr_fromstr("or"), w_rhs]
            )


class W_ConstraintObject(W_ConstraintMarkerObject):
    _attrs_ = ["w_strength", "block", "enabled",
               "constraint_objects_w", "constraint_variables_w",
               "assignments_w", "w_solver", "last_cvar"]
    classdef = ClassDef("Constraint", W_ConstraintMarkerObject.classdef)

    def __init__(self, space):
        W_Object.__init__(self, space)
        self.w_strength = None
        self.block = None
        self.enabled = False
        self.constraint_objects_w = []
        self.constraint_variables_w = []
        self.assignments_w = []
        self.last_cvar = None

    def get_constraint_objects(self):
        return self.constraint_objects_w

    def add_constraint_object(self, w_value):
        self.constraint_objects_w.append(w_value)

    def remove_constraint_objects(self):
        del self.constraint_objects_w[:]

    def has_constraint_objects(self):
        return len(self.constraint_objects_w) > 0

    def add_constraint_variable(self, c_var):
        if c_var not in self.constraint_variables_w:
            self.constraint_variables_w.append(c_var)
        self.last_cvar = c_var

    def last_constraint_variable(self):
        return self.last_cvar

    def add_assignment(self, space, c_var, w_constraint):
        if c_var in self.assignments_w:
            raise space.error(
                space.w_RuntimeError,
                "multiply assigned variable in constraint execution"
            )
        self.assignments_w.append(c_var)

    @jit.elidable
    def isidentity(self):
        for w_constraint_object in self.constraint_objects_w:
            if not isinstance(w_constraint_object, W_IdentityConstraintObject):
                return False
        return True

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
    def method_recalculate(self, space, w_c_cause):
        if self.enabled:
            if self.isidentity():
                for w_constraint_object in self.constraint_objects_w:
                    assert isinstance(w_constraint_object, W_IdentityConstraintObject)
                    if (w_constraint_object.c_this is w_c_cause or
                        w_constraint_object.c_that is w_c_cause):
                        # do not recalculate if an assignment to one
                        # of the identity-constrained variables is
                        # happening
                        return
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
            if w_var._is_solveable(self.get_solver()):
                vars_w.append(w_var._get_external_variable(self.get_solver()))
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

    @classdef.method("solver")
    def method_solver(self, space):
        return self.w_solver or space.w_nil

    @classdef.method("initialize")
    def method_initialize(self, space, w_strength=None, w_options=None, block=None):
        if not block:
            raise space.error(space.w_ArgumentError, "no constraint predicate given")
        if self.block:
            raise space.error(space.w_ArgumentError, "cannot re-initialize Constraint")
        if w_strength and space.is_kind_of(w_strength, space.w_hash):
            w_options = w_strength
            w_strength = space.send(w_strength, "[]", [space.newsymbol("priority")])
            if w_strength is space.w_nil:
                w_strength = None

        self.block = block
        self.w_strength = w_strength
        self.w_solver = None
        if w_options:
            if space.is_true(space.send(w_options, "has_key?", [space.newsymbol("solver")])):
                self.set_solver(space, space.send(w_options, "[]", [space.newsymbol("solver")]))

        self.run_predicate(space)
        return self

    def set_solver(self, space, w_solver):
        assert self.w_solver is None
        self.w_solver = w_solver
        for c_var in self.constraint_variables_w:
            c_var._set_solver_for_unbound_constraint(self, w_solver)

    def get_solver(self):
        return self.w_solver

    @classdef.singleton_method("allocate")
    def singleton_method_allocate(self, space):
        return W_ConstraintObject(space)

    @classdef.method("value")
    def method_return_value(self, space):
        # last added constraint object is the return value
        return self.constraint_objects_w[-1]


class W_IdentityConstraintObject(W_ConstraintMarkerObject):
    _attrs_ = ["enabled", "c_this", "c_that"]
    classdef = ClassDef("IdentityConstraint", W_ConstraintMarkerObject.classdef)

    @classdef.method("initialize")
    def method_initialize(self, space, w_this, w_that, w_c_this, w_c_that):
        w_current_constraint = space.current_constraint()
        if not w_current_constraint:
            raise space.error(
                space.w_RuntimeError,
                "Identity constraints must be created in constraint expressions"
            )
        if w_c_this is space.w_nil or w_c_that is space.w_nil:
            raise space.error(
                space.w_ArgumentError,
                "could not find two variables with an identity to constraint. Maybe one or both sides are not calculated from variables?"
            )
        assert isinstance(w_c_this, ConstrainedVariable)
        assert isinstance(w_c_that, ConstrainedVariable)
        if ((w_c_this.is_solveable(space) and w_this is not w_c_this.get_external_variable(space)) or
            (not w_c_this.is_solveable(space) and w_this is not space.get_value(w_c_this))):
            raise space.error(
                space.w_ArgumentError,
                "the value returned from the left hand side of the identity expression cannot be identity constrained (it may be a calculated value)"
            )
        if ((w_c_that.is_solveable(space) and w_that is not w_c_that.get_external_variable(space)) or
            (not w_c_that.is_solveable(space) and w_that is not space.get_value(w_c_that))):
            raise space.error(
                space.w_ArgumentError,
                "the value returned from the right hand side of the identity expression cannot be identity constrained (it may be a calculated value)"
            )
        if not w_current_constraint.isidentity():
            raise space.error(
                space.w_RuntimeError,
                "identity constraints are not valid in combination with other constraints in the same constraint expression"
            )
        self.enabled = False
        self.c_this = w_c_this
        self.c_that = w_c_that

    @classdef.method("enable")
    def method_enable(self, space):
        if not self.enabled:
            self.c_that.constrain_identity(space, self.c_this)
            self.enabled = True

    @classdef.method("disable")
    def method_disable(self, space):
        if self.enabled:
            self.c_that.unconstrain_identity(space, self.c_this)
            self.enabled = False

    @classdef.singleton_method("allocate")
    def singleton_method_allocate(self, space):
        return W_IdentityConstraintObject(space)
