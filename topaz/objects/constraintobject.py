from rpython.rlib import jit

from topaz.module import ClassDef, ModuleDef
from topaz.objects.hashobject import W_HashObject
from topaz.objects.objectobject import W_Object, W_RootObject
from topaz.objects.procobject import W_ProcObject
from topaz.utils.cache import Cache


# Marker class for constraint solver objects
class W_ConstraintObject(W_RootObject):
    classdef = ClassDef("ConstraintObject", W_Object.classdef, filepath=__file__)
