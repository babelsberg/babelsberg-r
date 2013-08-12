from rpython.rlib import jit

from topaz.interpreter import Interpreter
from topaz.objects.objectobject import W_Root
from topaz.objects.moduleobject import W_ModuleObject


class ConstraintInterpreter(Interpreter):
    def LOAD_DEREF(self, space, bytecode, frame, pc, idx):
        # This must be normal LOAD_DEREF for the arguments of frames
        # below the primitive call to __constraint__. If the arguments
        # are derived from variables, they are already wrapped with
        # constraintvariables, otherwise they are constant
        w_res = None
        if frame.backref().get_code_name() == "__constraint__" or idx not in frame.bytecode.arg_pos:
            frame.cells[idx].upgrade_to_closure(space, frame, idx)
            c_var = space.newconstraintvariable(cell=frame.cells[idx])
            if c_var and c_var.is_solveable():
                w_res = c_var.w_external_variable
        if not w_res:
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
        if space.is_kind_of(w_lhs, space.w_constraintobject):
            space.send(w_lhs, "and", [frame.pop()])
            return pc
        else:
            return Interpreter.JUMP_AND(self, space, bytecode, frame, pc, target_pc)


class ConstrainedVariable(W_Root):
    CONSTRAINT_IVAR = "__constrained_variable__"
    _immutable_fields_ = ["cell", "w_owner", "ivar", "cvar", "idx", "w_key",
                          "w_external_variable"]

    def __init__(self, space, cell=None, w_owner=None, ivar=None, cvar=None, idx=-1, w_key=None):
        self.w_external_variable = None
        self.cell = cell
        self.w_owner = w_owner
        self.ivar = ivar
        self.cvar = cvar
        self.idx = idx
        self.w_key = w_key
        self.constraints_w = []
        self.is_readonly = False
        self.w_readonly_constraint = None
        self.w_remembered_value = None

        if cell:
            from topaz.closure import ClosureCell
            assert isinstance(cell, ClosureCell)

        if not cell and not (w_owner and (ivar or cvar or idx >= 0 or w_key)):
            raise RuntimeError("Invalid ConstraintVariableObject initialization")

        w_value = self.load_value(space)
        if space.respond_to(w_value, "for_constraint"):
            with space.normal_execution():
                w_external_variable = space.send(
                    w_value,
                    "for_constraint",
                    [self.get_name(space)]
                )
                if w_external_variable is not space.w_nil:
                    self.w_external_variable = w_external_variable
                    space.set_instance_var(self.w_external_variable, self.CONSTRAINT_IVAR, self)

    def __del__(self):
        # TODO: remove external variable from solver
        pass

    # XXX: remove once we find another way to store the ConstrainedVariable object
    def is_kind_of(self, space, w_cls):
        return False

    def make_readonly(self, space):
        if not self.w_readonly_constraint:
            self.w_readonly_constraint = space.send(self.w_external_variable, "==", [self.get_i(space)])
            space.send(self.w_readonly_constraint, "enable")
        self.is_readonly = True

    def make_assignable(self, space):
        if self.w_readonly_constraint:
            space.send(self.w_readonly_constraint, "disable")
            self.w_readonly_constraint = None

    def make_writable(self, space):
        self.make_assignable(space)
        self.is_readonly = False

    def is_solveable(self):
        return self.w_external_variable is not None

    def add_to_constraint(self, w_constraint):
        if w_constraint not in self.constraints_w:
            self.constraints_w.append(w_constraint)
            w_constraint.add_constraint_variable(self)

    def load_value(self, space):
        if self.cell:
            return self.cell.get(space, None, 0) or space.w_nil
        elif self.ivar is not None:
            return self.w_owner.find_instance_var(space, self.ivar) or space.w_nil
        elif self.cvar is not None:
            return self.w_owner.find_class_var(space, self.cvar) or space.w_nil
        elif self.idx >= 0:
            return space.listview(self.w_owner)[self.idx] or space.w_nil
        else:
            raise NotImplementedError("inconsistent constraint variable")

    def store_value(self, space, w_value):
        if self.cell:
            self.cell.set(space, None, 0, w_value)
        elif self.ivar is not None:
            self.w_owner.set_instance_var(space, self.ivar, w_value)
        elif self.cvar is not None:
            self.w_owner.set_class_var(space, self.cvar, w_value)
        elif self.idx >= 0:
            space.listview(self.w_owner)[self.idx] = w_value
        else:
            raise NotImplementedError("inconsistent constraint variable")

    def get_name(self, space):
        inspectstr = space.any_to_s(self.load_value(space))
        if self.cell:
            storagestr = "local"
        elif self.ivar is not None:
            storagestr = "ivar(%s)" % self.ivar
        elif self.cvar is not None:
            storagestr = "cvar(%s)" % self.cvar
        elif self.idx > 0:
            storagestr = "item(%d)" % self.idx
        else:
            storagestr = "unknown"
        return space.newstr_fromstr("%s-%s" % (storagestr, inspectstr))

    def begin_assign(self, space, w_value):
        if self.is_solveable():
            if self.is_readonly:
                self.make_writable(space)
            with space.constraint_execution():
                space.send(self.w_external_variable, "begin_assign", [w_value])
        else:
            self.store_value(space, w_value)
            self.w_remembered_value = w_value

    def assign(self, space):
        if self.is_solveable():
            with space.constraint_execution():
                space.send(self.w_external_variable, "assign")
        else:
            self.recalculate_path(space, self.w_remembered_value)

    def end_assign(self, space):
        if self.is_solveable():
            with space.constraint_execution():
                space.send(self.w_external_variable, "end_assign")
            if self.is_readonly:
                self.make_readonly(space)
        else:
            self.w_remembered_value = None

    def assign_value(self, space, w_value):
        self.begin_assign(space, w_value)
        self.assign(space)
        self.end_assign(space)

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
        for w_constraint in self.constraints_w:
            space.send(w_constraint, "recalculate")
