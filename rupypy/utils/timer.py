from pypy.rlib.timer import Timer as PyPyTimer
from rupypy.module import ClassDef
from rupypy.objects.objectobject import W_Object

class W_Timer(W_Object):
    classdef = ClassDef("Timer", W_Object.classdef)

    def __init__(self, space):
        W_Object.__init__(self, space)
        self.timer = PyPyTimer()

    @classdef.singleton_method("allocate")
    def method_allocate(self, space):
        return W_Timer(space)

    @classdef.method("reset")
    def method_reset(self):
        self.timer.reset()
    
    @classdef.method("start", timer="str")
    def method_start(self, timer):
        self.timer.start(timer)

    @classdef.method("stop", timer="str")
    def method_stop(self, timer):
        self.timer.stop(timer)

    @classdef.method("dump")
    def method_dump(self):
        self.timer.dump()
        os.write(2, "\n")

