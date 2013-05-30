from rpython.rlib import jit

from topaz.interpreter import Interpreter
from topaz.objects.objectobject import W_Root
from topaz.objects.moduleobject import W_ModuleObject


class ConstraintInterpreter(Interpreter):
    def LOAD_DEREF(self, space, bytecode, frame, pc, idx):
        # This must be normal LOAD_DEREF for the arguments of frames
        # below the top-level. If the arguments are derived from
        # variables, they are already wrapped with
        # constraintvariables, otherwise they are constant
        if frame.get_code_name() != "__constraint__" and idx < frame.bytecode.arg_pos:
            w_res = frame.cells[idx].get(space, frame, idx) or space.w_nil
        else:
            frame.cells[idx].upgrade_to_closure(space, frame, idx)
            c_var = space.newconstraintvariable(cell=frame.cells[idx])
            if c_var and c_var.is_solveable():
                w_res = c_var.w_external_variable
            else:
                w_res = frame.cells[idx].get(space, frame, idx) or space.w_nil
        frame.push(w_res)

    def LOAD_INSTANCE_VAR(self, space, bytecode, frame, pc, idx):
        name = space.symbol_w(bytecode.consts_w[idx])
        w_obj = frame.pop()
        c_var = space.newconstraintvariable(w_owner=w_obj, ivar=name)
        if c_var and c_var.is_solveable():
            w_res = c_var.w_external_variable
        else:
            w_res = space.find_instance_var(w_obj, name)
        frame.push(w_res)

    def LOAD_CLASS_VAR(self, space, bytecode, frame, pc, idx):
        name = space.symbol_w(bytecode.consts_w[idx])
        w_module = frame.pop()
        assert isinstance(w_module, W_ModuleObject)
        c_var = space.newconstraintvariable(w_owner=w_module, cvar=name)
        if c_var and c_var.is_solveable():
            w_res = c_var.w_external_variable
        else:
            w_res = space.find_class_var(w_module, name)
            if w_res is None:
                raise space.error(space.w_NameError,
                    "uninitialized class variable %s in %s" % (name, w_module.name)
                )
        frame.push(w_res)

    def JUMP_AND(self, space, bytecode, frame, pc, target_pc):
        w_lhs = frame.peek()
        if space.is_kind_of(w_lhs, space.w_constraint):
            # XXX: does this need strength?
            space.enable_constraint(w_lhs)
            frame.pop()
            return pc
        else:
            return Interpreter.JUMP_AND(self, space, bytecode, frame, pc, target_pc)

    def SEND(self, space, bytecode, frame, pc, meth_idx, num_args):
        args_w = frame.popitemsreverse(num_args)
        w_receiver = frame.pop()
        w_res = None
        method = space.symbol_w(bytecode.consts_w[meth_idx])
        if space.is_kind_of(w_receiver, space.w_constraint):
            with space.normal_execution():
                w_res = space.send(w_receiver, method, args_w)
        else:
            w_res = space.send(w_receiver, method, args_w)
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
        if space.respond_to(w_value, "for_constraint"):
            with space.normal_execution():
                self.w_external_variable = space.send(
                    w_value,
                    "for_constraint",
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
        inspectstr = space.any_to_s(self.load_value(space))
        if self.cell:
            storagestr = "local"
        elif self.ivar is not None:
            storagestr = "ivar"
        elif self.cvar is not None:
            storagestr = "cvar"
        else:
            storagestr = "unknown"
        return space.newstr_fromstr("%s-%s" % (storagestr, inspectstr))

    def suggest_value(self, space, w_value):
        assert self.w_external_variable
        with space.constraint_execution():
            space.send(self.w_external_variable, "suggest_value", [w_value])

    def set_i(self, space):
        if self.w_external_variable is not None:
            # This variable is part of the solver. Get the solvers
            # interpretation and store it
            w_value = space.send(self.w_external_variable, "value")
            if w_value != space.w_nil:
                # w_variable_value may not be the same as w_value,
                # because client code may choose to return a different
                # variables' value in #for_constraint
                w_variable_value = self.load_value(space)
                if space.respond_to(w_variable_value, "assign_constraint_value"):
                    space.send(w_variable_value, "assign_constraint_value", [w_value])
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
            for w_constraint in block.get_constraints():
                space.send(w_constraint, "disable")
            block.remove_constraints()
            args_w = [] if w_strength is None else [w_strength]
            space.send(space.w_object, "always", args_w, block=block)
