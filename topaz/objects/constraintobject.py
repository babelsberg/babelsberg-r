from rpython.rlib import jit

from topaz.module import ClassDef, ModuleDef
from topaz.objects.hashobject import W_HashObject
from topaz.objects.objectobject import W_Object, W_RootObject
from topaz.objects.procobject import W_ProcObject
from topaz.utils.cache import Cache


# Marker class for constraint solver objects
class W_ConstraintMarkerObject(W_Object):
    classdef = ClassDef("ConstraintObject", W_Object.classdef)

    @classdef.singleton_method("allocate")
    def singleton_method_allocate(self, space):
        return W_ConstraintMarkerObject(space, self)


class W_ConstraintObject(W_ConstraintMarkerObject):
    classdef = ClassDef("Constraint", W_ConstraintMarkerObject.classdef)

    def __init__(self, space, constraints_w, w_strength, block):
        W_Object.__init__(self, space)
        self.constraints_w = constraints_w
        self.w_strength = w_strength
        self.block = block
        block.enable_constraint()
        self.enabled = True

    @classdef.method("enable")
    def method_enable(self, space):
        if not self.enabled:
            for w_constraint in self.constraints_w:
                space.send(w_constraint, "enable", [self.w_strength])
            self.block.enable_constraint()
            self.enabled = True
            return space.w_true
        else:
            return space.w_nil

    @classdef.method("disable")
    def method_disable(self, space):
        if self.enabled:
            for w_constraint in self.constraints_w:
                space.send(w_constraint, "disable")
            self.block.disable_constraint()
            self.enabled = False
            return space.w_true
        else:
            return space.w_nil

    @classdef.method("solver_constraints")
    def method_solver_constraints(self, space):
        return space.newarray(self.constraints_w[:])

    @classdef.method("constraint_block")
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
