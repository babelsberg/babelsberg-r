from rpython.rlib import jit

from topaz.interpreter import Interpreter
from topaz.objects.objectobject import W_Root
from topaz.objects.moduleobject import W_ModuleObject


class ConstraintInterpreter(Interpreter):
    def LOAD_DEREF(self, space, bytecode, frame, pc, idx):
        frame.cells[idx].upgrade_to_closure(space, frame, idx)
        w_res = space.newconstraintvariable(cell=frame.cells[idx])
        if w_res is None:
            w_res = frame.cells[idx].get(space, frame, idx) or space.w_nil
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
        w_module = frame.pop()
        assert isinstance(w_module, W_ModuleObject)
        w_res = space.newconstraintvariable(w_owner=w_module, cvar=name)
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


class ConstrainedVariable(W_Root):
    _immutable_fields_ = ["cell", "w_owner", "ivar", "cvar", "w_external_variable"]

    def __init__(self, space, cell=None, w_owner=None, ivar=None, cvar=None):
        self.w_external_variable = None
        self.cell = None
        self.w_owner = None
        self.ivar = None
        self.cvar = None
        self.constraint_blocks = []
        if cell:
            self.cell = cell
        elif w_owner and ivar:
            self.w_owner = w_owner
            self.ivar = ivar
        elif w_owner and cvar:
            self.w_owner = w_owner
            self.cvar = cvar
        else:
            raise RuntimeError("Invalid ConstraintVariableObject initialization")

        w_value = self.load_value(space)
        if space.respond_to(w_value, space.newsymbol("for_constraint")):
            with space.normal_execution():
                self.w_external_variable = space.send(
                    w_value,
                    space.newsymbol("for_constraint"),
                    [self.get_name(space)]
                )

    def __del__(self):
        # TODO: remove external variable from solver
        pass

    def is_solveable(self):
        return self.w_external_variable is not None

    def add_constraint_block(self, block, w_strength):
        self.constraint_blocks.append((block, w_strength))

    def load_value(self, space):
        if self.cell:
            return self.cell.get(space, None, 0) or space.w_nil
        elif self.ivar is not None:
            return self.w_owner.find_instance_var(space, self.ivar) or space.w_nil
        elif self.cvar is not None:
            return self.w_owner.find_class_var(space, self.cvar) or space.w_nil
        else:
            raise NotImplementedError("inconsistent constraint variable")

    def store_value(self, space, w_value):
        if self.cell:
            self.cell.set(space, None, 0, w_value)
        elif self.ivar is not None:
            self.w_owner.set_instance_var(space, self.ivar, w_value)
        elif self.cvar is not None:
            self.w_owner.set_class_var(space, self.cvar, w_value)
        else:
            raise NotImplementedError("inconsistent constraint variable")

    def get_name(self, space):
        clsname = space.getclass(self.load_value(space)).name
        if self.cell:
            return space.newstr_fromstr("local-%s" % clsname)
        elif self.ivar is not None:
            return space.newstr_fromstr("ivar-%s" % clsname)
        elif self.cvar is not None:
            return space.newstr_fromstr("cvar-%s" % clsname)
        return space.w_nil

    def suggest_value(self, space, w_value):
        assert self.w_external_variable
        with space.constraint_execution():
            space.send(self.w_external_variable, space.newsymbol("suggest_value"), [w_value])

    def set_i(self, space):
        if self.w_external_variable is not None:
            # This variable is part of the solver. Get the solvers
            # interpretation and store it
            w_value = space.send(self.w_external_variable, space.newsymbol("value"))
            if w_value != space.w_nil:
                # w_variable_value may not be the same as w_value,
                # because client code may choose to return a different
                # variables' value in #for_constraint
                w_variable_value = self.load_value(space)
                if space.respond_to(w_variable_value, space.newsymbol("assign_constraint_value")):
                    space.send(w_variable_value, space.newsymbol("assign_constraint_value"), [w_value])
                else:
                    self.store_value(space, w_value)
            return w_value
        return space.w_nil

    def get_i(self, space):
        self.set_i(space)
        return self.load_value(space)

    def recalculate_path(self, space, w_value):
        self.store_value(space, w_value)
        for block, w_strength in self.constraint_blocks:
            w_constraint = block.get_constraint()
            assert w_constraint
            space.send(w_constraint, space.newsymbol("disable"))
            block.set_constraint(None)
            args_w = [] if w_strength is None else [w_strength]
            space.send(space.w_object, space.newsymbol("always"), args_w, block=block)
