import os
import time

from pypy.module.rctime.interp_time import c_localtime, c_mktime, cConfig
from pypy.rpython.lltypesystem import rffi
from pypy.rpython.lltypesystem import lltype

from rupypy.module import ClassDef
from rupypy.objects.objectobject import W_Object
from rupypy.objects.floatobject import W_FloatObject
from rupypy.objects.intobject import W_FixnumObject

def _tm_to_ary(t):
    return [
        rffi.getintfield(t, 'c_tm_year') + 1900,
        rffi.getintfield(t, 'c_tm_mon') + 1, # want january == 1
        rffi.getintfield(t, 'c_tm_mday'),
        rffi.getintfield(t, 'c_tm_hour'),
        rffi.getintfield(t, 'c_tm_min'),
        rffi.getintfield(t, 'c_tm_sec'),
        (rffi.getintfield(t, 'c_tm_wday') + 6) % 7, # want monday == 0
        rffi.getintfield(t, 'c_tm_yday') + 1, # want january, 1 == 1
        rffi.getintfield(t, 'c_tm_isdst')
    ]

def _localtime(seconds):
    t = rffi.r_time_t(seconds)
    t_ref = lltype.malloc(rffi.TIME_TP.TO, 1, flavor='raw')
    t_ref[0] = seconds
    p = c_localtime(t_ref)
    lltype.free(t_ref, flavor='raw')
    return _tm_to_ary(p)

def _mktime(year, month, mday, hour, minute, second):
    tm_buf = lltype.malloc(cConfig.tm, flavor='raw', zero=True)
    rffi.setintfield(tm_buf, 'c_tm_year', year)
    rffi.setintfield(tm_buf, 'c_tm_mon', month)
    rffi.setintfield(tm_buf, 'c_tm_mday', mday)
    rffi.setintfield(tm_buf, 'c_tm_hour', hour)
    rffi.setintfield(tm_buf, 'c_tm_min', minute)
    rffi.setintfield(tm_buf, 'c_tm_sec', second)
    tt = c_mktime(tm_buf)
    lltype.free(tm_buf, flavor='raw')
    return float(tt)


class W_TimeObject(W_Object):
    classdef = ClassDef("Time", W_Object.classdef)

    @classdef.singleton_method("allocate")
    def method_allocate(self, space, args_w):
        return W_TimeObject(space)

    @classdef.singleton_method("now")
    def singleton_method_now(self, space):
        return space.send(space.getclassfor(W_TimeObject), space.newsymbol("new"))

    @classdef.singleton_method("at")
    def singleton_method(self, space, w_sec, w_usec=None):
        if isinstance(w_sec, W_TimeObject):
            args = w_sec.time_struct[:5]
            epoch = int(w_sec.epoch) % 60
        else:
            if w_usec:
                usec = space.float_w(w_usec) / 1000
            else:
                usec = 0.0
            sec = int(space.float_w(w_sec))
            args = _localtime(sec)[:5]
            epoch = int(sec + usec) % 60
        args_w = [space.newint(i) for i in args]
        args_w.append(space.newfloat(epoch))
        return space.send(space.getclassfor(W_TimeObject), space.newsymbol("new"), args_w)

    @classdef.method("initialize")
    def method_initialize(self, space, args_w):
        if not args_w:
            self.epoch = time.time()
            self.time_struct = _localtime(int(self.epoch))
        else:
            if len(args_w) > 6:
                raise NotImplementedError("Time.new with utc_offset")
            args = [space.float_w(i) for i in args_w]
            args += [0] * (6 - len(args))
            self.epoch = _mktime(
                args[0], args[1], args[2], args[3], args[4], args[5]
            ) + (args[5] % 1)
            self.time_struct = _localtime(self.epoch)

    @classdef.method("to_s")
    def method_to_s(self, space):
        return space.newstr_fromstr("%d-%d-%d %d:%d:%d" % self.time_struct[:6])

    @classdef.method("to_f")
    def method_to_f(self, space):
        return space.newfloat(self.epoch)

    @classdef.method("-")
    def method_minus(self, space, w_other):
        assert isinstance(w_other, W_TimeObject)
        return space.send(
            space.getclassfor(W_TimeObject),
            space.newsymbol("at"),
            [space.newfloat(self.epoch - w_other.epoch)]
        )
