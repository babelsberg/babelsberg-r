from rupypy.module import ClassDef
from rupypy.objects.objectobject import W_BaseObject


class W_RegexpObject(W_BaseObject):
    classdef = ClassDef("Regexp", W_BaseObject.classdef)

    def __init__(self, regexp):
        self.regexp = regexp
