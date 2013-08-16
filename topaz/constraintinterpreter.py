from rpython.rlib import jit

from topaz.celldict import CellDict
from topaz.coerce import Coerce
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
            if c_var and c_var.is_solveable(space):
                w_res = c_var.get_external_variable(space)
        if not w_res:
            w_res = frame.cells[idx].get(space, frame, idx) or space.w_nil
        frame.push(w_res)

    def LOAD_INSTANCE_VAR(self, space, bytecode, frame, pc, idx):
        name = space.symbol_w(bytecode.consts_w[idx])
        w_obj = frame.pop()
        c_var = space.newconstraintvariable(w_owner=w_obj, ivar=name)
        if c_var and c_var.is_solveable(space):
            w_res = c_var.get_external_variable(space)
        else:
            w_res = space.find_instance_var(w_obj, name)
        frame.push(w_res)

    def LOAD_CLASS_VAR(self, space, bytecode, frame, pc, idx):
        name = space.symbol_w(bytecode.consts_w[idx])
        w_module = frame.pop()
        assert isinstance(w_module, W_ModuleObject)
        c_var = space.newconstraintvariable(w_owner=w_module, cvar=name)
        if c_var and c_var.is_solveable(space):
            w_res = c_var.get_external_variable(space)
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
    _immutable_fields_ = ["cell", "w_owner", "ivar", "cvar", "idx", "w_key"]

    def __init__(self, space, cell=None, w_owner=None, ivar=None, cvar=None, idx=-1, w_key=None):
        self.solvers_w = []
        self.constraints_w = []
        self.external_variables_w = []
        self.readonly_constraints = []
        self.cell = cell
        self.w_owner = w_owner
        self.ivar = ivar
        self.cvar = cvar
        self.idx = idx
        self.w_key = w_key
        self.has_readonly = False

        if cell:
            from topaz.closure import ClosureCell
            assert isinstance(cell, ClosureCell)

        if not cell and not (w_owner and (ivar or cvar or idx >= 0 or w_key)):
            raise RuntimeError("Invalid ConstraintVariableObject initialization")

        self.ensure_external_variable(space, space.current_solver())

    def __del__(self):
        # TODO: remove external variable from solver
        pass

    def add_solver(self, w_solver):
        if w_solver not in self.solvers_w:
            self.solvers_w.append(w_solver)

    def solver_idx(self, w_solver):
        try:
            return self.solvers_w.index(w_solver)
        except ValueError:
            self.solvers_w.append(w_solver)
            return len(self.solvers_w) - 1

    def ensure_external_variable(self, space, w_solver):
        w_value = self.load_value(space)
        w_external_variable = space.w_nil

        if not w_solver:
            if space.respond_to(w_value, "constraint_solver"):
                with space.normal_execution():
                    w_solver = space.send(w_value, "constraint_solver")
                    space.set_current_solver(w_solver)
        self.add_solver(w_solver)

        if w_solver and not self._is_solveable(w_solver):
            with space.normal_execution():
                w_external_variable = space.send(
                    w_solver,
                    "constraint_variable_for",
                    [w_value]
                )

        if w_external_variable is space.w_nil:
            if space.respond_to(w_value, "for_constraint"):
                with space.normal_execution():
                    w_external_constraint = space.send(w_value, "for_constraint", [self.get_name(space)])
                    if w_external_constraint is not space.w_nil:
                        w_external_solver = space.send(w_external_constraint, "solver")
                        if w_solver and w_external_solver is not w_solver:
                            raise space.error(
                                space.w_RuntimeError,
                                "value %s has no interpretation in active solver %s, only in solver %s" % (
                                    space.send(w_value, "inspect"),
                                    space.send(w_solver, "inspect"),
                                    space.send(w_external_solver, "inspect")
                                )
                            )
                        elif not w_solver:
                            w_solver = w_external_solver
                            self.add_solver(w_external_solver)
                        w_external_variable = space.send(w_external_constraint, "value")

        if w_external_variable is not space.w_nil:
            self.set_external_variable(space, w_solver, w_external_variable)
            space.set_instance_var(w_external_variable, self.CONSTRAINT_IVAR, self)

    def set_external_variable(self, space, w_solver, w_external_variable):
        idx = self.solver_idx(w_solver)
        assert len(self.external_variables_w) >= idx
        if len(self.external_variables_w) == idx:
            self.external_variables_w.append(w_external_variable)
        else:
            self.external_variables_w[idx] = w_external_variable
        self.update_readonly_annotations(space, w_solver)

    def get_external_variable(self, space):
        return self._get_external_variable(space.current_solver())

    @jit.elidable
    def _get_external_variable(self, w_solver):
        idx = self.solver_idx(w_solver)
        try:
            return self.external_variables_w[idx]
        except IndexError:
            return None

    def get_solver_constraints_w(self, w_solver):
        idx = self.solver_idx(w_solver)
        try:
            if self.constraints_w[idx] is None:
                self.constraints_w[idx] = []
            return self.constraints_w[idx]
        except IndexError:
            self.constraints_w += [None] * (idx - len(self.constraints_w) + 1)
            self.constraints_w[idx] = []
            return self.constraints_w[idx]

    # XXX: remove once we find another way to store the ConstrainedVariable object
    def is_kind_of(self, space, w_cls):
        return False

    def make_readonly(self, space, w_external_variable=None):
        if not w_external_variable:
            w_external_variable = self.get_external_variable(space)
        if not self.is_readonly(w_external_variable):
            space.send(w_external_variable, "readonly!")
            self.mark_readonly(w_external_variable)

    def is_readonly(self, w_external_variable):
        idx = self.external_variables_w.index(w_external_variable)
        try:
            return self.readonly_constraints[idx]
        except IndexError:
            return False

    def mark_readonly(self, w_external_variable, flag=True):
        idx = self.external_variables_w.index(w_external_variable)
        if len(self.readonly_constraints) <= idx:
            self.readonly_constraints += [False] * (idx - len(self.readonly_constraints) + 1)
        self.readonly_constraints[idx] = flag
        self.has_readonly = True

    def make_writable(self, w_external_variable):
        if self.is_readonly(w_external_variable):
            space.send(w_external_variable, "writable!")
            self.mark_readonly(w_external_variable, False)

    def make_assignable(self, space):
        if self.has_readonly:
            for i, v in enumerate(self.readonly_constraints):
                if v:
                    space.send(self.external_variables_w[i], "writable!")

    def make_not_assignable(self, space):
        if self.has_readonly:
            for i, v in enumerate(self.readonly_constraints):
                if v:
                    space.send(self.external_variables_w[i], "readonly!")

    def is_solveable(self, space=None):
        if space:
            return self._is_solveable(space.current_solver())
        else:
            for w_var in self.external_variables_w:
                if w_var is not None:
                    return True
            return False

    @jit.elidable
    def _is_solveable(self, w_solver=None):
        return self._get_external_variable(w_solver) is not None

    def add_to_constraint(self, space, w_constraint):
        solver_constraints_w = self.get_solver_constraints_w(space.current_solver())
        if w_constraint not in solver_constraints_w:
            solver_constraints_w.append(w_constraint)
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
        self.make_assignable(space)
        self.store_value(space, w_value)
        defining_variable = self.defining_variable(space)
        if defining_variable:
            with space.constraint_execution():
                space.send(defining_variable, "begin_assign", [w_value])

    def assign(self, space):
        defining_variable = self.defining_variable(space)
        if defining_variable:
            with space.constraint_execution():
                space.send(defining_variable, "assign")
            # now update the other external variables
            new_value = self.get_i(space)
            for w_external_variable in self.external_variables_w:
                if w_external_variable and w_external_variable is not defining_variable:
                    space.send(w_external_variable, "begin_assign", [new_value])
                    space.send(w_external_variable, "assign")

    def end_assign(self, space):
        for w_external_variable in self.external_variables_w:
            if w_external_variable:
                space.send(w_external_variable, "end_assign")
        self.make_not_assignable(space)
        for i, cs_w in enumerate(self.constraints_w):
            if (len(self.external_variables_w) < i + 1 or
                self.external_variables_w[i] is None):
                self.recalculate_path(space, cs_w)

    def assign_value(self, space, w_value):
        self.begin_assign(space, w_value)
        self.assign(space)
        self.end_assign(space)

    def defining_solver(self, space):
        w_strongest_solver = None
        strongest_weight = -1000 # XXX: Magic number
        for i, w_solver in enumerate(self.solvers_w):
            if w_solver and self._is_solveable(w_solver):
                new_weight = Coerce.int(space, space.send(w_solver, "weight"))
                if new_weight > strongest_weight:
                    strongest_weight = new_weight
                    w_strongest_solver = w_solver
        return w_strongest_solver

    def defining_variable(self, space):
        return self._get_external_variable(self.defining_solver(space))

    def update_readonly_annotations(self, space, w_solver):
        defining_variable = self.defining_variable(space)
        for w_external_variable in self.external_variables_w:
            if w_external_variable is not defining_variable:
                self.make_readonly(space, w_external_variable)

    def set_i(self, space):
        if self.is_solveable():
            # This variable is part of the solver. Get the solvers
            # interpretation and store it
            w_external_variable = self.defining_variable(space)
            w_value = space.send(w_external_variable, "value")
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

    def recalculate_path(self, space, constraints_w):
        for w_constraint in constraints_w:
            space.send(w_constraint, "recalculate")
