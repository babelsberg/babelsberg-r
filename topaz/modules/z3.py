from __future__ import absolute_import

from topaz.coerce import Coerce
from topaz.module import Module, ModuleDef, ClassDef
from topaz.objects.objectobject import W_Object
from topaz.utils import rz3


class Z3(Module):
    moduledef = ModuleDef("Z3", filepath=__file__)
    made_solver = False
    made_context = False
    enabled_constraints = []

    @staticmethod
    def get_solver(ctx):
        if not Z3.made_solver:
            Z3.solver = rz3.z3_mk_solver(ctx)
            Z3.made_solver = True
        return Z3.solver

    @staticmethod
    def get_context():
        if not Z3.made_context:
            cfg = rz3.z3_mk_config()
            rz3.z3_set_param_value(cfg, "MODEL", "true")
            Z3.ctx = rz3.z3_mk_context(cfg)
            rz3.z3_del_config(cfg)
            Z3.made_context = True
        return Z3.ctx

    @staticmethod
    def make_variable(id, ty):
        ctx = Z3.get_context()
        sym = rz3.z3_mk_int_symbol(ctx, id)
        return rz3.z3_mk_const(ctx, sym, ty)

    @staticmethod
    def make_int_variable(id):
        ctx = Z3.get_context()
        ty = rz3.z3_mk_int_sort(ctx)
        return Z3.make_variable(id, ty)

    @staticmethod
    def make_int(value):
        ctx = Z3.get_context()
        ty = rz3.z3_mk_int_sort(ctx)
        return rz3.z3_mk_int(ctx, value, ty)

    @staticmethod
    def make_real_variable(id):
        ctx = Z3.get_context()
        ty = rz3.z3_mk_real_sort(ctx)
        return Z3.make_variable(id, ty)

    @staticmethod
    def make_real(value):
        ctx = Z3.get_context()
        num, den = value.as_integer_ratio()
        return rz3.z3_mk_real(ctx, num, den)

    @staticmethod
    def make_bool_variable(id):
        ctx = Z3.get_context()
        ty = rz3.z3_mk_bool_sort(ctx)
        return Z3.make_variable(id, ty)

    @staticmethod
    def make_bool(value):
        ctx = Z3.get_context()
        if value:
            return rz3.mk_true(ctx)
        else:
            return rz3.mk_false(ctx)

    @moduledef.function("add_constraint")
    def method_enable(self, space, w_other):
        Z3.enabled_constraints.append(w_other)
        return w_other

    @moduledef.function("remove_constraint")
    def method_enable(self, space, w_other):
        try:
            Z3.enabled_constraints.remove(w_other)
            return w_other
        except ValueError:
            return space.w_nil

    @moduledef.function("solve")
    def method_solve(self, space):
        self.ctx = Z3.get_context()
        self.solver = Z3.get_solver(self.ctx)
        for constraint in Z3.enabled_constraints:
            rz3.z3_solver_assert(self.ctx, self.solver, constraint.getast())
        solve_result = rz3.z3_solver_check(self.ctx, self.solver)
        if solve_result < 0:
            raise space.error(space.w_RuntimeError, "unsatisfiable constraint system")
        elif solve_result == 0:
            raise space.error(space.w_RuntimeError, "the solver cannot solve this constraint system")
        self.model = rz3.z3_solver_get_model(self.ctx, self.solver)
        self.is_solved = True
        return space.w_true

    @moduledef.function("[]")
    def method_get_interpretation(self, space, w_ast):
        if not space.is_kind_of(w_ast, space.w_z3ast):
            raise space.error(space.w_ArgumentError, "Z3Expression required, got %s" % space.getclass(w_ast).name)

        if not self.is_solved:
            return space.w_nil
        else:
            interp_ast = rz3.z3_model_get_const_interp(self.ctx, self.model, w_ast.getdecl(self.ctx))
            kind = rz3.z3_get_ast_kind(self.ctx, interp_ast)
            if kind == 0: # Z3_NUMERAL_AST
                try:
                    return space.newint(rz3.z3_get_numeral_int(self.ctx, interp_ast))
                except rz3.Z3Error:
                    return space.newfloat(rz3.z3_get_numeral_real(self.ctx, interp_ast))
            else:
                raise NotImplementedError("Ast type %d" % kind)
            return space.newstr_fromstr(numstr)


class W_Z3AstObject(W_Object):
    classdef = ClassDef("Z3Expression", W_Object.classdef, filepath=__file__)

    def setast(self, ast):
        self.ast = ast

    def getast(self):
        return self.ast

    def getdecl(self, ctx):
        return rz3.z3_get_app_decl(ctx, self.getast())

    @classdef.singleton_method("allocate")
    def method_allocate(self, space, args_w):
        return W_Z3AstObject(space)

    # XXX: These should somehow also set the initial value
    @classdef.method("initialize")
    def method_initialize(self, space, w_value):
        w_int = space.convert_type(w_value, space.w_fixnum, "to_int", raise_error=False)
        if w_int is not space.w_nil and not space.is_kind_of(w_value, space.w_float):
            self.ast = Z3.make_int_variable(space.int_w(space.send(w_int, space.newsymbol("object_id"))))
            return self

        w_real = space.convert_type(w_value, space.w_float, "to_f", raise_error=False)
        if w_real is not space.w_nil:
            self.ast = Z3.make_real_variable(space.int_w(space.send(w_real, space.newsymbol("object_id"))))
            return self

        if w_value is space.w_true or w_value is space.w_false or w_value is space.w_nil:
            self.ast = Z3.make_bool_variable(space.int_w(space.send(w_real, space.newsymbol("object_id"))))
            return self

        raise space.error(space.w_TypeError, "Z3 can only use Bools, Floats, and Fixnums")

    def new_binop(classdef, name, func):
        @classdef.method(name)
        def method(self, space, w_other):
            if space.is_kind_of(w_other, space.w_z3ast):
                other = w_other.getast()
            else:
                fixnum = Coerce.int(space, w_other)
                other = Z3.make_int(fixnum)
            ast = func(Z3.get_context(), self.getast(), other)
            w_obj = W_Z3AstObject(space)
            w_obj.setast(ast)
            return w_obj
        method.__name__ = "method_%s" % func.__name__
        return method
    method_lt = new_binop(classdef, "<", rz3.z3_mk_lt)
    method_gt = new_binop(classdef, ">", rz3.z3_mk_gt)
    method_gt = new_binop(classdef, "**", rz3.z3_mk_power)

    @classdef.method("enable")
    def method_enable(self, space):
        space.send(
            space.w_z3,
            space.newsymbol("add_constraint"),
            [self]
        )
        return self

    @classdef.method("disable")
    def method_enable(self, space):
        space.send(
            space.w_z3,
            space.newsymbol("remove_constraint"),
            [self]
        )
        return self

    @classdef.method("value")
    def method_value(self, space):
        return space.send(space.w_z3, space.newsymbol("[]"), [self])
