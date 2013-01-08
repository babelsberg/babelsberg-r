from pypy.rlib import jit

from rupypy.interpreter import Interpreter
from rupypy.objects.constraintobject import W_ConstraintObject
from rupypy.objects.moduleobject import W_ModuleObject


class ConstraintInterpreter(Interpreter):
    def LOAD_DEREF(self, space, bytecode, frame, pc, idx):
        frame.cells[idx].upgrade_to_closure(frame, idx)
        w_res = space.newconstraintvariable(cell=frame.cells[idx])
        if w_res is None:
            w_res = frame.cells[idx].get(frame, idx) or space.w_nil
        frame.push(w_res)

    def LOAD_INSTANCE_VAR(self, space, bytecode, frame, pc, idx):
        name = space.symbol_w(bytecode.consts_w[idx])
        w_obj = frame.pop()
        w_res = space.newconstraintvariable(w_owner=w_obj, ivar=name)
        if w_res is None:
            w_res = space.find_instance_var(w_obj, name)
        frame.push(w_res)

    def LOAD_CLASS_VAR(self, space, bytecode, frame, pc, idx):
        name = space.symbol_w(bytecode.consts_w[idx])
        w_obj = frame.pop()
        assert isinstance(w_obj, W_ModuleObject)
        w_res = space.newconstraintvariable(w_owner=w_obj, cvar=name)
        if w_res is None:
            w_res = space.find_class_var(w_module, name)
            if w_res is None:
                raise space.error(space.w_NameError,
                    "uninitialized class variable %s in %s" % (name, w_module.name)
                )
        frame.push(w_res)

    def SEND(self, space, bytecode, frame, pc, meth_idx, num_args):
        args_w = frame.popitemsreverse(num_args)
        w_receiver = frame.pop()
        w_res = None
        if space.is_kind_of(w_receiver, space.w_constraint):
            with space.normal_execution():
                w_res = space.send(w_receiver, bytecode.consts_w[meth_idx], args_w)
        else:
            w_res = space.send(w_receiver, bytecode.consts_w[meth_idx], args_w)
        frame.push(w_res)
