from __future__ import absolute_import

from rpython.rlib.rfloat import float_as_rbigint_ratio

from topaz.coerce import Coerce
from topaz.module import ClassDef
from topaz.objects.objectobject import W_RootObject, W_Object
from topaz.objects.constraintobject import W_ConstraintMarkerObject
from topaz.utils import rz3


class Z3Exception(Exception):
    pass


MAX_REAL_INT = 2**32 - 1 # hard in Z3


class W_Z3Object(W_Object):
    _attrs_ = ["ctx", "solver", "enabled_constraints", "is_solved", "next_id"]
    _immutable_fields_ = ["ctx", "solver"]
    classdef = ClassDef("Z3", W_Object.classdef)

    def __init__(self, space, klass=None):
        W_Object.__init__(self, space, klass=klass)
        cfg = rz3.z3_mk_config()
        rz3.z3_set_param_value(cfg, "MODEL", "true")
        ctx = rz3.z3_mk_context(cfg)
        rz3.z3_del_config(cfg)
        solver = rz3.z3_mk_solver(ctx)
        rz3.z3_solver_inc_ref(ctx, solver)
        self.ctx = ctx
        self.solver = solver
        self.enabled_constraints = []
        self.is_solved = False
        self.next_id = 0

    @classdef.setup_class
    def setup_class(cls, space, w_cls):
        w_ptr_cls = space.getclassfor(W_Z3Ptr)
        space.set_const(w_cls, w_ptr_cls.name, w_ptr_cls)

    def make_variable(self, space, w_object, ctx, ty):
        # XXX: This should somehow also set the initial value
        sym = rz3.z3_mk_int_symbol(ctx, self.next_id)
        self.next_id += 1
        return W_Z3Ptr(space, self, rz3.z3_mk_const(ctx, sym, ty), w_object)

    def assert_ptr(self, space, w_pointer):
        if not isinstance(w_pointer, W_Z3Ptr):
            raise space.error(
                space.w_TypeError,
                "expected %s, got %s" % (space.getclassfor(W_Z3Ptr).name, space.getclass(w_pointer).name)
            )

    @classdef.singleton_method("allocate")
    def method_allocate(self, space):
        # TODO: context config passing
        return W_Z3Object(space)

    @classdef.method("make_real_variable")
    def make_real_variable(self, space, w_value):
        space.convert_type(w_value, space.w_float, "to_f") # Just for the error raising
        ty = rz3.z3_mk_real_sort(self.ctx)
        return self.make_variable(space, w_value, self.ctx, ty)

    @classdef.method("make_real")
    def make_real(self, space, w_value):
        value = Coerce.float(space, w_value)
        try:
            num, den = float_as_rbigint_ratio(value)
        except OverflowError, ValueError:
            raise space.error(
                space.w_ArgumentError,
                "cannot rationalize %s" % space.str_w(
                    space.send(w_value, "inspect")
                )
            )
        try:
            int_num = num.toint()
            int_den = den.toint()
        except OverflowError:
            int_num = 1
            int_den = 1

        while int_num > MAX_REAL_INT or int_den > MAX_REAL_INT:
            int_num = int_num >> 2
            int_den = int_den >> 2

        return W_Z3Ptr(space, self, rz3.z3_mk_real(self.ctx, int_num, int_den))

    @classdef.method("make_int_variable")
    def make_real_variable(self, space, w_value):
        space.convert_type(w_value, space.w_fixnum, "to_int") # Just for the error raising
        ty = rz3.z3_mk_int_sort(self.ctx)
        return self.make_variable(space, w_value, self.ctx, ty)

    @classdef.method("make_int")
    def make_real(self, space, w_value):
        value = space.int_w(space.convert_type(w_value, space.w_fixnum, "to_int"))
        ty = rz3.z3_mk_int_sort(self.ctx)
        return W_Z3Ptr(space, self, rz3.z3_mk_int(self.ctx, value, ty))

    @classdef.method("make_bool_variable")
    def make_bool_variable(self, space, w_value):
        if w_value is not space.w_true and w_value is not space.w_false and w_value is not space.w_nil:
            raise space.error(space.w_TypeError, "can't convert %s into bool" % space.getclass(w_value).name)
        ty = rz3.z3_mk_bool_sort(self.ctx)
        return self.make_variable(space, w_value, self.ctx, ty)

    @classdef.method("make_bool", value="bool")
    def make_bool(self, space, value):
        if value:
            return W_Z3Ptr(space, self, rz3.z3_mk_true(self.ctx))
        else:
            return W_Z3Ptr(space, self, rz3.z3_mk_false(self.ctx))

    @classdef.method("add_constraint")
    def method_add_constraint(self, space, w_other):
        self.assert_ptr(space, w_other)
        # print rz3.z3_ast_to_string(self.ctx, w_other.pointer)
        self.enabled_constraints.append(w_other)
        return w_other

    @classdef.method("remove_constraint")
    def method_remove_constraint(self, space, w_other):
        self.assert_ptr(space, w_other)
        try:
            self.enabled_constraints.remove(w_other)
            return w_other
        except ValueError:
            return space.w_nil

    @classdef.method("solve")
    def method_solve(self, space):
        self.is_solved = False
        rz3.z3_solver_reset(self.ctx, self.solver)
        for constraint in self.enabled_constraints:
            assert isinstance(constraint, W_Z3Ptr)
            rz3.z3_solver_assert(self.ctx, self.solver, constraint.pointer)
        solve_result = rz3.z3_solver_check(self.ctx, self.solver)
        if solve_result < 0:
            raise space.error(space.w_RuntimeError, "unsatisfiable constraint system")
        elif solve_result == 0:
            raise space.error(space.w_RuntimeError, "Z3 cannot solve this constraint system")
        self.is_solved = True
        return space.w_true

    @classdef.method("[]")
    def method_get_interpretation(self, space, w_ast):
        self.assert_ptr(space, w_ast)
        if not self.is_solved:
            return space.w_nil
        else:
            model = rz3.z3_solver_get_model(self.ctx, self.solver)
            try:
                decl = w_ast.getdecl(self.ctx)
            except Z3Exception:
                return space.w_nil
            if rz3.z3_model_has_interp(self.ctx, model, decl) == 0:
                return space.w_nil
            interp_ast = rz3.z3_model_get_const_interp(self.ctx, model, decl)
            kind = rz3.z3_get_ast_kind(self.ctx, interp_ast)
            if kind == 0: # Z3_NUMERAL_AST
                try:
                    return space.newint(rz3.z3_get_numeral_int(self.ctx, interp_ast))
                except rz3.Z3Error:
                    return space.newfloat(rz3.z3_get_numeral_real(self.ctx, interp_ast))
            elif kind == 1: # Z3_APP_AST ... XXX: bools, in our case
                result = rz3.z3_get_bool_value(self.ctx, interp_ast)
                return space.newbool(result == 1) # 1 is Z3_L_TRUE
            else:
                raise NotImplementedError("Ast type %d" % kind)


class W_Z3Ptr(W_ConstraintMarkerObject):
    _attrs_ = ["w_z3", "pointer", "w_value"]
    _immutable_fields_ = ["w_z3", "pointer"]
    classdef = ClassDef("Z3Pointer", W_ConstraintMarkerObject.classdef)

    def __init__(self, space, w_z3, pointer, w_value=None):
        W_Object.__init__(self, space, space.getclassfor(W_Z3Ptr))
        self.w_z3 = w_z3
        self.pointer = pointer
        self.w_value = w_value
        rz3.z3_ast_inc_ref(self.w_z3.ctx, self.pointer)

    def __del__(self):
        rz3.z3_ast_dec_ref(self.w_z3.ctx, self.pointer)

    def getsingletonclass(self, space):
        raise space.error(space.w_TypeError, "can't define singleton")

    def getdecl(self, ctx):
        decl = rz3.z3_get_app_decl(ctx, self.pointer)
        err = rz3.z3_get_error_code(ctx)
        if err != 0:
            raise Z3Exception
        return decl

    classdef.undefine_allocator()

    def coerce_constant_arg(self, space, w_arg):
        w_z3ptr_cls = space.getclassfor(W_Z3Ptr)
        if not space.is_kind_of(w_arg, w_z3ptr_cls):
            if w_arg in [space.w_true, space.w_false, space.w_nil]:
                w_other = space.send(self.w_z3, "make_bool", [w_arg])
            elif space.is_kind_of(w_arg, space.w_fixnum):
                w_other = space.send(self.w_z3, "make_int", [w_arg])
            else:
                w_other = space.send(self.w_z3, "make_real", [w_arg])
        else:
            w_other = w_arg

        if not space.is_kind_of(w_other, w_z3ptr_cls):
            raise space.error(space.w_TypeError, "%s can't be coerced into %s::%s" % (
                    space.getclass(w_arg).name,
                    space.w_z3.name,
                    w_z3ptr_cls.name
            ))
        else:
            assert isinstance(w_other, W_Z3Ptr)
            return w_other.pointer

    def new_binop(classdef, name, func):
        @classdef.method(name)
        def method(self, space, w_other):
            other = self.coerce_constant_arg(space, w_other)
            ast = func(self.w_z3.ctx, self.pointer, other)
            return W_Z3Ptr(space, self.w_z3, ast)
        method.__name__ = "method_%s" % func.__name__
        return method
    method_lt = new_binop(classdef, "<", rz3.z3_mk_lt)
    method_gt = new_binop(classdef, ">", rz3.z3_mk_gt)
    method_pow = new_binop(classdef, "**", rz3.z3_mk_power)
    method_eq = new_binop(classdef, "==", rz3.z3_mk_eq)
    method_eq = new_binop(classdef, "!=", rz3.z3_mk_ne)
    method_ge = new_binop(classdef, ">=", rz3.z3_mk_ge)
    method_le = new_binop(classdef, "<=", rz3.z3_mk_le)
    method_add = new_binop(classdef, "+", rz3.z3_mk_add)
    method_sub = new_binop(classdef, "-", rz3.z3_mk_sub)
    method_div = new_binop(classdef, "/", rz3.z3_mk_div)
    method_mul = new_binop(classdef, "*", rz3.z3_mk_mul)
    method_mod = new_binop(classdef, "%", rz3.z3_mk_mod)
    method_rem = new_binop(classdef, "remainder", rz3.z3_mk_rem)
    method_or = new_binop(classdef, "or", rz3.z3_mk_or)
    # method_and = new_binop(classdef, "and", rz3.z3_mk_and)

    @classdef.method("abs")
    def method_abs(self, space):
        cond = space.send(self, "<", [space.newint(0)])
        assert isinstance(cond, W_Z3Ptr)
        then = space.send(self, "-@")
        assert isinstance(then, W_Z3Ptr)
        ast = rz3.z3_mk_ite(self.w_z3.ctx, cond.pointer, then.pointer, self.pointer)
        return W_Z3Ptr(space, self.w_z3, ast)

    @classdef.method("if_true")
    def method_if_true(self, space, w_then):
        assert isinstance(w_then, W_Z3Ptr)
        false_case = rz3.z3_mk_true(self.w_z3.ctx)
        ast = rz3.z3_mk_ite(self.w_z3.ctx, self.pointer, w_then.pointer, false_case)
        return W_Z3Ptr(space, self.w_z3, ast)

    @classdef.method("if_false")
    def method_if_true(self, space, w_then):
        assert isinstance(w_then, W_Z3Ptr)
        true_case = rz3.z3_mk_true(self.w_z3.ctx)
        ast = rz3.z3_mk_ite(self.w_z3.ctx, self.pointer, true_case, w_then.pointer)
        return W_Z3Ptr(space, self.w_z3, ast)

    @classdef.method("ite")
    def method_if_true(self, space, w_true, w_false):
        assert isinstance(w_true, W_Z3Ptr)
        assert isinstance(w_false, W_Z3Ptr)
        ast = rz3.z3_mk_ite(self.w_z3.ctx, self.pointer, w_true.pointer, w_false.pointer)
        return W_Z3Ptr(space, self.w_z3, ast)

    @classdef.method("alldifferent")
    def method_alldifferent(self, space, args_w):
        w_constraint = space.current_constraint()
        if not w_constraint:
            raise space.error(space.w_RuntimeError)
        else:
            asts_w = [self.coerce_constant_arg(space, w_arg) for w_arg in args_w]
            asts_w.append(self.pointer)
            return W_Z3Ptr(space, self.w_z3, rz3.z3_mk_distinct(self.w_z3.ctx, asts_w))

    @classdef.method("-@")
    def method_unary_minus(self, space):
        ast = rz3.z3_mk_unary_minus(self.w_z3.ctx, self.pointer)
        return W_Z3Ptr(space, self.w_z3, ast)

    @classdef.method("enable")
    def method_enable(self, space):
        space.send(
            self.w_z3,
            "add_constraint",
            [self]
        )
        return self

    @classdef.method("disable")
    def method_enable(self, space):
        space.send(
            self.w_z3,
            "remove_constraint",
            [self]
        )
        return self

    @classdef.method("value")
    def method_value(self, space):
        w_value = space.send(self.w_z3, "[]", [self])
        if w_value is space.w_nil:
            return self.w_value or space.w_nil
        elif self.w_value:
            self.w_value = w_value
        return w_value
