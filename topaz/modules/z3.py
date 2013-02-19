from topaz.module import Module, ModuleDef, ClassDef
from topaz.objects.objectobject import W_Object
from topaz.utils import rz3


class Z3(Module):
    moduledef = ModuleDef("Z3", filepath=__file__)
    enabled_constraints = []

    def make_solver(self, ctx):
        return rz3.z3_mk_solver(ctx)

    def make_context(self):
        cfg = rz3.z3_mk_config()
        rz3.z3_set_param_value(cfg, "MODEL", "true")
        ctx = rz3.z3_mk_context(cfg)
        rz3.z3_del_config(cfg)
        return ctx

    def make_variable(self, ctx, name, ty):
        s = rz3.z3_mk_string_symbol(ctx, name)
        return rz3.z3_mk_const(ctx, s, ty)

    def make_int_variable(self, ctx, name):
        ty = rz3.z3_mk_int_sort(ctx)
        return self.make_variable(ctx, name, ty)

    def make_int(self, ctx, value):
        ty = rz3.z3_mk_int_sort(ctx)
        return rz3.z3_mk_int(ctx, value, ty)

    @moduledef.function("add_constraint", other="z3ast")
    def method_enable(self, space, other):
        self.enabled_constraints.append(other)
        return other

    @moduledef.function("remove_constraint", other="z3ast")
    def method_enable(self, space, other):
        try:
            self.enabled_constraints.remove(other)
            return other
        except ValueError:
            return space.w_nil

    @moduledef.function("solve")
    def method_solve(self, space):
        self.is_solved = True
        self.ctx = self.make_context()
        self.solver = self.make_solver(ctx)
        for constraint in self.enabled_constraints:
            rz3.z3_solver_assert(ctx, solver, constraint)
        solve_result = rz3.z3_solver_check(ctx, solver)
        if solve_result < 0:
            raise space.error(space.w_RuntimeError, "unsatisfiable constraint system")
        elif solve_result == 0:
            raise space.error(space.w_RuntimeError, "the solver cannot solve this constraint system")
        self.model = rz3.z3_solver_get_model(ctx, solver)

    @moduledef.function("get_interpretation", other="z3ast")
    def method_get_interpretation(self, space, other):
        if not self.is_solved:
            return space.w_nil
        else:
            interp_ast = rz3.z3_model_get_const_interp(self.ctx, self.model, other.getast())
            kind = rz3.z3_get_ast_kind(self.ctx, interp_ast)
            if kind == 0: # Z3_NUMERAL_AST
                numstr = rz3.z3_get_numeral_string(self.ctx, interp_ast)
            else:
                raise NotImplementedError("only numeral asts implemented")

class W_Z3AstObject(W_Object):
    classdef = ClassDef("Z3Expression", filepath=__file__)

    def __init__(self, space, ctx, ast):
        W_Object.__init__(self, space)
        self.ctx = ctx
        self.ast = ast

    def getast(self):
        return self.ast

    @classdef.method("<", other="z3ast")
    def method_lt(self, space, other):
        rz3.z3_mk_lt(self.ctx, self, other)

    @classdef.method("enable")
    def method_enable(self, space):
        space.send(
            space.getmoduleobject(Z3.moduledef),
            space.newsymbol("add_constraint")
            [self]
        )
        return self

    @classdef.method("disable")
    def method_enable(self, space):
        space.send(
            space.getmoduleobject(Z3.moduledef),
            space.newsymbol("remove_constraint")
            [self]
        )
        return self
