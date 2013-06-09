from rpython.rlib import jit

from topaz.module import ClassDef, ModuleDef
from topaz.objects.hashobject import W_HashObject
from topaz.objects.objectobject import W_Object, W_RootObject
from topaz.objects.procobject import W_ProcObject
from topaz.utils.cache import Cache


# Marker class for constraint solver objects
class W_ConstraintMarkerObject(W_Object):
    classdef = ClassDef("ConstraintObject", W_Object.classdef)

class W_ConstraintObject(W_ConstraintMarkerObject):
    _immutable_fields_ = ["constraints_w[*]"]
    classdef = ClassDef("Constraint", W_ConstraintMarkerObject.classdef)

    def __init__(self, space, constraints_w, w_strength, block):
        W_Object.__init__(self, space)
        self.constraints_w = constraints_w
        self.w_strength = w_strength
        self.block = block

    @classdef.method("enable")
    def method_enable(self, space):
        for w_constraint in self.constraints_w:
            space.send(w_constraint, "enable", self.w_strength)
        return self

    @classdef.method("disable")
    def method_disable(self, space):
        for w_constraint in self.constraints_w:
            space.send(w_constraint, "disable", self.w_strength)
        return self

    @classdef.method("solver_constraints")
    def method_solver_constraints(self, space):
        return space.newarray(self.constraints_w)

    @classdef.method("constraint_block")
    def method_constraint_block(self, space):
        return self.block

    @classdef.method("strength")
    def method_strength(self, space):
        return self.w_strength

