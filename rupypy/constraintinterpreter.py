from pypy.rlib import jit
from pypy.rlib.debug import check_nonneg
from pypy.rlib.objectmodel import we_are_translated, specialize

from rupypy import consts
from rupypy.error import RubyError
from rupypy.executioncontext import IntegerWrapper
from rupypy.interpreter import Interpreter
from rupypy.objects.arrayobject import W_ArrayObject
from rupypy.objects.blockobject import W_BlockObject
from rupypy.objects.classobject import W_ClassObject
from rupypy.objects.codeobject import W_CodeObject
from rupypy.objects.functionobject import W_FunctionObject
from rupypy.objects.moduleobject import W_ModuleObject
from rupypy.objects.objectobject import W_Root
from rupypy.objects.procobject import W_ProcObject
from rupypy.objects.stringobject import W_StringObject
from rupypy.scope import StaticScope


class ConstraintInterpreter(Interpreter):
    jitdriver = jit.JitDriver(
        greens=["pc", "bytecode", "block_bytecode", "w_trace_proc"],
        reds=["self", "frame"],
        virtualizables=["frame"],
        get_printable_location=get_printable_location,
    )

    def LOAD_DEREF(self, space, bytecode, frame, pc, idx):
        frame.cells[idx].upgrade_to_closure(frame, idx)
        w_obj = (frame.cells[idx].get(frame, idx) or space.w_nil)
        w_var = space.newconstraintvariable(cell=frame.cells[idx])
        frame.push(w_var)

    def LOAD_INSTANCE_VAR(self, space, bytecode, frame, pc, idx):
        name = space.symbol_w(bytecode.consts_w[idx])
        w_obj = frame.pop()
        w_var = space.newconstraintvariable(w_owner=w_obj, ivar=name)
        frame.push(w_var)

    def LOAD_CLASS_VAR(self, space, bytecode, frame, pc, idx):
        name = space.symbol_w(bytecode.consts_w[idx])
        w_obj = frame.pop()
        w_var = space.newconstraintvariable(w_owner=w_obj, cvar=name)
        frame.push(w_var)
