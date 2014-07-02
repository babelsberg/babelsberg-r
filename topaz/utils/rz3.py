import os
import platform
import sys

from rpython.rtyper.tool import rffi_platform
from rpython.rtyper.lltypesystem import rffi, lltype
from rpython.translator.tool.cbuild import ExternalCompilationInfo

class Z3Error(Exception):
    pass


WINNT = os.name == "nt"
POSIX = os.name == "posix"
_64BIT = "64bit" in platform.architecture()[0]

z3_dir = os.path.abspath(os.path.join(
    os.path.dirname(__file__),
    os.path.pardir,
    os.path.pardir,
    "dependencies",
    "z3"
))
z3_include_path = os.path.join(z3_dir, "src", "api")
z3_build_path = os.path.join(z3_dir, "build")
z3_exe = os.path.join(z3_build_path, "z3")
z3_lib = "z3"
if WINNT:
    z3_exe += ".exe"
    z3_lib = "libz3"

if not os.path.isfile(z3_exe):
    old_dir = os.getcwd()
    os.chdir(z3_dir)
    try:
        if POSIX:
            os.system("autoconf")
            os.system("./configure")
        my_python = sys.executable
        if not my_python:
            my_python = "python"
        if not os.path.exists(z3_build_path):
            os.mkdir(z3_build_path)
        os.system("%s %s" % (
                my_python,
                os.path.join(
                    z3_dir,
                    "scripts",
                    "mk_make.py"
                )
        ))
        os.chdir(z3_build_path)
        if WINNT:
            os.system("nmake")
        elif POSIX:
            os.system("make")
        else:
            raise NotImplementedError("cannot build z3 on non-windows and non-posix systems")
    finally:
        os.chdir(old_dir)

eci = ExternalCompilationInfo(
    includes=["z3.h"],
    include_dirs=[z3_include_path],
    libraries=[z3_lib],
    library_dirs=[z3_build_path]
    # separate_module_files=["rupypy/utils/re/rffi_helper.c"]
)

class CConfig:
    _compilation_info_ = eci
    if WINNT:
        calling_conv = "win"
    else:
        calling_conv = "c"

config = rffi_platform.configure(CConfig)

# Create config
Z3_config = rffi.COpaquePtr("Z3_config")
z3_mk_config = rffi.llexternal("Z3_mk_config", [], Z3_config, compilation_info=eci)
z3_del_config = rffi.llexternal("Z3_del_config", [Z3_config], lltype.Void, compilation_info=eci)
z3_set_param_value = rffi.llexternal(
    "Z3_set_param_value",
    [Z3_config, rffi.CCHARP, rffi.CCHARP],
    lltype.Void,
    compilation_info=eci
)

# Create context
Z3_context = rffi.COpaquePtr("Z3_context")
z3_mk_context = rffi.llexternal("Z3_mk_context", [Z3_config], Z3_context, compilation_info=eci)
z3_del_context = rffi.llexternal("Z3_del_context", [Z3_context], lltype.Void, compilation_info=eci)

# AST
Z3_ast = rffi.COpaquePtr("Z3_ast")
Z3_astP = rffi.VOIDPP
Z3_func_decl = rffi.COpaquePtr("Z3_func_decl")
Z3_bool = rffi.INT

_z3_get_numeral_string = rffi.llexternal(
    "Z3_get_numeral_string",
    [Z3_context, Z3_ast],
    rffi.CCHARP,
    compilation_info=eci
)

def z3_get_numeral_string(ctx, ast):
    return rffi.charp2str(_z3_get_numeral_string(ctx, ast))

_z3_get_numeral_int = rffi.llexternal(
    "Z3_get_numeral_int64" if _64BIT else "Z3_get_numeral_int64",
    [Z3_context, Z3_ast, rffi.INTP],
    rffi.INT,
    compilation_info=eci
)

def z3_get_numeral_int(ctx, ast):
    ptr = lltype.malloc(rffi.INTP.TO, 1, flavor='raw', zero=True)
    status = _z3_get_numeral_int(ctx, ast, ptr)
    result = int(ptr[0])
    lltype.free(ptr, flavor='raw')
    if status != 1:
        raise Z3Error("result does not fit into int-type")
    else:
        return result

if _64BIT:
    _z3_get_numeral_real = rffi.llexternal(
        "Z3_get_numeral_rational_int64",
        [Z3_context, Z3_ast, rffi.LONGP, rffi.LONGP],
        rffi.INT,
        compilation_info=eci
    )
    def z3_get_numeral_real(ctx, ast):
        from rpython.rlib.rfloat import INFINITY
        from math import copysign

        nom = lltype.malloc(rffi.LONGP.TO, 1, flavor='raw', zero=True)
        den = lltype.malloc(rffi.LONGP.TO, 1, flavor='raw', zero=True)
        status = _z3_get_numeral_real(ctx, ast, nom, den)
        fnom = float(int(nom[0]))
        fden = float(int(den[0]))
        lltype.free(nom, flavor='raw')
        lltype.free(den, flavor='raw')
        if fnom == 0.0 and fden == 0.0:
            return 0
        elif fden == 0.0:
            sign = copysign(1.0, fnom)
            if sign > 0:
                return copysign(INFINITY, fden)
            else:
                return copysign(INFINITY, -fden)
        elif status != 1:
            raise Z3Error("result does not fit into int-type")
        else:
            if fnom == 0 or fden == 0:
                return 0
            return fnom / fden
else:
    _z3_get_denominator = rffi.llexternal("Z3_get_denominator", [Z3_context, Z3_ast], Z3_ast, compilation_info=eci)
    _z3_get_numerator = rffi.llexternal("Z3_get_numerator", [Z3_context, Z3_ast], Z3_ast, compilation_info=eci)
    def z3_get_numeral_real(ctx, ast):
        nom_ast = _z3_get_numerator(ctx, ast)
        den_ast = _z3_get_denominator(ctx, ast)
        nom = z3_get_numeral_int(ctx, nom_ast)
        den = z3_get_numeral_int(ctx, den_ast)
        return float(nom) / float(den)

z3_is_algebraic_number = rffi.llexternal("Z3_is_algebraic_number", [Z3_context, Z3_ast], rffi.INT, compilation_info=eci)
z3_get_algebraic_number_upper = rffi.llexternal("Z3_get_algebraic_number_upper", [Z3_context, Z3_ast, rffi.UINT], Z3_ast, compilation_info=eci)

z3_get_ast_kind = rffi.llexternal("Z3_get_ast_kind", [Z3_context, Z3_ast], rffi.INT, compilation_info=eci)
z3_get_app_decl = rffi.llexternal("Z3_get_app_decl", [Z3_context, Z3_ast], Z3_func_decl, compilation_info=eci)
z3_func_decl_to_ast = rffi.llexternal("Z3_func_decl_to_ast", [Z3_context, Z3_func_decl], Z3_ast, compilation_info=eci)
z3_mk_app = rffi.llexternal("Z3_mk_app", [Z3_context, Z3_func_decl, rffi.UINT, Z3_astP], Z3_ast, compilation_info=eci)

def z3_func_declp_to_ast(ctx, func_decl_p):
    return z3_func_decl_to_ast(ctx, rffi.cast(Z3_func_decl, func_decl_p))

# Symbols
Z3_symbol = rffi.COpaquePtr("Z3_symbol")
z3_mk_string_symbol = rffi.llexternal(
    "Z3_mk_string_symbol",
    [Z3_context, rffi.CCHARP],
    Z3_symbol,
    compilation_info=eci
)
z3_mk_int_symbol = rffi.llexternal(
    "Z3_mk_int_symbol",
    [Z3_context, rffi.INT],
    Z3_symbol,
    compilation_info=eci
)

# Pointers
Z3_symbolP = rffi.VOIDPP
Z3_func_declP = rffi.VOIDPP
Z3_sortP = rffi.VOIDPP

# Sorts
Z3_sort = rffi.COpaquePtr("Z3_sort")
z3_mk_int_sort = rffi.llexternal("Z3_mk_int_sort", [Z3_context], Z3_sort, compilation_info=eci)
z3_mk_real_sort = rffi.llexternal("Z3_mk_real_sort", [Z3_context], Z3_sort, compilation_info=eci)
z3_mk_bool_sort = rffi.llexternal("Z3_mk_bool_sort", [Z3_context], Z3_sort, compilation_info=eci)

z3_sort_to_ast = rffi.llexternal("Z3_sort_to_ast", [Z3_context, Z3_sort], Z3_ast, compilation_info=eci)
_z3_get_sort = rffi.llexternal("Z3_get_sort", [Z3_context, Z3_ast], Z3_sort, compilation_info=eci)
_z3_mk_enumeration_sort = rffi.llexternal("Z3_mk_enumeration_sort", [Z3_context, Z3_symbol, rffi.UINT, Z3_symbolP, Z3_func_declP, Z3_func_declP], Z3_sort, compilation_info=eci)

def z3_mk_enumeration_sort(ctx, name, names):
    size = len(names)

    consts = lltype.malloc(Z3_func_declP.TO, size, flavor="raw")
    testers = lltype.malloc(Z3_func_declP.TO, size, flavor="raw")

    llnames = lltype.malloc(Z3_symbolP.TO, size, flavor="raw")

    for i in range(0, size):
        llnames[i] = z3_mk_string_symbol(ctx, str(i))#names[i].__id__)

    sort = _z3_mk_enumeration_sort(
            ctx,
            name,
            size,
            llnames,
            consts,
            testers)

    # Free the buffers!
    result_consts = []
    for i in range(0, size):
        tmp_const = z3_mk_app(ctx, rffi.cast(Z3_func_decl, consts[i]), 0, rffi.cast(Z3_astP, 0))
        z3_ast_inc_ref(ctx, tmp_const)
        result_consts.append(tmp_const)

    z3_ast_inc_ref(ctx, z3_sort_to_ast(ctx, sort))

    return (sort, result_consts)

# Bool
z3_mk_not = rffi.llexternal("Z3_mk_not", [Z3_context, Z3_ast], Z3_ast, compilation_info=eci)

# Arithmetic
def binop(name):
    globals()[name.lower()] = rffi.llexternal(name, [Z3_context, Z3_ast, Z3_ast], Z3_ast, compilation_info=eci)
binop("Z3_mk_lt")
binop("Z3_mk_gt")
binop("Z3_mk_le")
binop("Z3_mk_ge")
binop("Z3_mk_power")
binop("Z3_mk_eq")
binop("Z3_mk_div")
binop("Z3_mk_rem")
binop("Z3_mk_mod")

z3_mk_unary_minus = rffi.llexternal("Z3_mk_unary_minus", [Z3_context, Z3_ast], Z3_ast, compilation_info=eci)

def z3_mk_ne(context, ast1, ast2):
    return z3_mk_not(context, z3_mk_eq(context, ast1, ast2))


def multiop(name):
    def create_method(func, name):
        def method(ctx, left, right):
            ptr = lltype.malloc(Z3_astP.TO, 2, flavor='raw')
            ptr[0] = left
            ptr[1] = right
            ast = func(ctx, 2, ptr)
            lltype.free(ptr, flavor='raw')
            return ast
        method.__name__ = name.lower()
        globals()[name.lower()] = method
    create_method(
        rffi.llexternal(
            name,
            [Z3_context, rffi.UINT, Z3_astP],
            Z3_ast,
            compilation_info=eci
        ),
        name
    )
multiop("Z3_mk_add")
multiop("Z3_mk_sub")
multiop("Z3_mk_mul")


# Numerals
z3_mk_real = rffi.llexternal("Z3_mk_real", [Z3_context, rffi.INT, rffi.INT], Z3_ast, compilation_info=eci)
z3_mk_int = rffi.llexternal("Z3_mk_int", [Z3_context, rffi.INT, Z3_sort], Z3_ast, compilation_info=eci)

# Propositional Logic
_z3_mk_distinct = rffi.llexternal("Z3_mk_distinct", [Z3_context, rffi.UINT, Z3_astP], Z3_ast, compilation_info=eci)
def z3_mk_distinct(ctx, asts):
    size = len(asts)
    ptr = lltype.malloc(Z3_astP.TO, size, flavor='raw')
    for i, ast in enumerate(asts):
        ptr[i] = ast
    ast = _z3_mk_distinct(ctx, size, ptr)
    lltype.free(ptr, flavor='raw')
    return ast

multiop("Z3_mk_and")
multiop("Z3_mk_or")
z3_mk_true = rffi.llexternal("Z3_mk_true", [Z3_context], Z3_ast, compilation_info=eci)
z3_mk_false = rffi.llexternal("Z3_mk_false", [Z3_context], Z3_ast, compilation_info=eci)
z3_get_bool_value = rffi.llexternal("Z3_get_bool_value", [Z3_context, Z3_ast], rffi.INT, compilation_info=eci)
z3_mk_ite = rffi.llexternal("Z3_mk_ite", [Z3_context, Z3_ast, Z3_ast, Z3_ast], Z3_ast, compilation_info=eci)


# Constants
z3_mk_const = rffi.llexternal("Z3_mk_const", [Z3_context, Z3_symbol, Z3_sort], Z3_ast, compilation_info=eci)

# Models
Z3_model = rffi.COpaquePtr("Z3_model")
z3_model_get_const_interp = rffi.llexternal(
    "Z3_model_get_const_interp",
    [Z3_context, Z3_model, Z3_func_decl],
    Z3_ast,
    compilation_info=eci
)
z3_model_has_interp = rffi.llexternal(
    "Z3_model_has_interp",
    [Z3_context, Z3_model, Z3_func_decl],
    Z3_bool,
    compilation_info=eci
)
_z3_model_eval = rffi.llexternal(
    "Z3_model_eval",
    [Z3_context, Z3_model, Z3_ast, Z3_bool, Z3_astP],
    Z3_bool,
    compilation_info=eci
)
def z3_model_eval(ctx, model, ast, completion):
    evaluated_ast = lltype.malloc(Z3_astP.TO, 1, flavor="raw")
    z3_completion =  1 if completion else 0

    _z3_model_eval(ctx, model, ast, z3_completion, evaluated_ast)
    result_ast = rffi.cast(Z3_ast, evaluated_ast[0])
    z3_ast_inc_ref(ctx, result_ast)

    return result_ast


# Solvers
Z3_solver = rffi.COpaquePtr("Z3_solver")
z3_mk_solver = rffi.llexternal("Z3_mk_solver", [Z3_context], Z3_solver, compilation_info=eci)
z3_solver_check = rffi.llexternal(
    "Z3_solver_check",
    [Z3_context, Z3_solver],
    Z3_bool,
    compilation_info=eci
)
z3_solver_assert = rffi.llexternal(
    "Z3_solver_assert",
    [Z3_context, Z3_solver, Z3_ast],
    lltype.Void,
    compilation_info=eci
)
z3_solver_get_model = rffi.llexternal(
    "Z3_solver_get_model",
    [Z3_context, Z3_solver],
    Z3_model,
    compilation_info=eci
)
z3_solver_reset = rffi.llexternal("Z3_solver_reset", [Z3_context, Z3_solver], lltype.Void, compilation_info=eci)

# Refcounting
z3_solver_inc_ref = rffi.llexternal("Z3_solver_inc_ref", [Z3_context, Z3_solver], lltype.Void, compilation_info=eci)
z3_solver_dec_ref = rffi.llexternal("Z3_solver_dec_ref", [Z3_context, Z3_solver], lltype.Void, compilation_info=eci)
z3_model_inc_ref = rffi.llexternal("Z3_model_inc_ref", [Z3_context, Z3_model], lltype.Void, compilation_info=eci)
z3_model_dec_ref = rffi.llexternal("Z3_model_dec_ref", [Z3_context, Z3_model], lltype.Void, compilation_info=eci)
z3_ast_inc_ref = rffi.llexternal("Z3_inc_ref", [Z3_context, Z3_ast], lltype.Void, compilation_info=eci)
z3_ast_dec_ref = rffi.llexternal("Z3_dec_ref", [Z3_context, Z3_ast], lltype.Void, compilation_info=eci)

# Errors
z3_get_error_code = rffi.llexternal("Z3_get_error_code", [Z3_context], rffi.INT, compilation_info=eci)
_z3_ast_to_string = rffi.llexternal("Z3_ast_to_string", [Z3_context, Z3_ast], rffi.CCHARP, compilation_info=eci)
def z3_ast_to_string(ctx, ast):
    return rffi.charp2str(_z3_ast_to_string(ctx, ast))

# SMT-Lib
_z3_parse_smtlib2_string = rffi.llexternal(
    "Z3_parse_smtlib2_string",
    [Z3_context, rffi.CCHARP,
     rffi.UINT, Z3_symbolP, Z3_sortP,
     rffi.UINT, Z3_symbolP, Z3_func_declP],
    Z3_ast,
    compilation_info=eci
)
def z3_parse_smtlib2_string(ctx, string, decls):
    size = len(decls)
    csymbols = lltype.malloc(Z3_symbolP.TO, size, flavor="raw")
    cdecls   = lltype.malloc(Z3_func_declP.TO, size, flavor="raw")
    idx = 0
    for key in decls:
        csymbols[idx] = z3_mk_string_symbol(ctx, key)
        cdecls[idx] = decls[key]
        idx += 1

    return _z3_parse_smtlib2_string(
        ctx,
        string,
        0, lltype.nullptr(Z3_symbolP.TO), lltype.nullptr(Z3_sortP.TO),
        size,
        csymbols,
        cdecls
    )

z3_get_smtlib_num_formulas = rffi.llexternal("Z3_get_smtlib_num_formulas", [Z3_context], rffi.UINT, compilation_info=eci)
z3_get_smtlib_formula = rffi.llexternal("Z3_get_smtlib_formula", [Z3_context, rffi.UINT], Z3_ast, compilation_info=eci)
z3_get_smtlib_num_assumptions = rffi.llexternal("Z3_get_smtlib_num_assumptions", [Z3_context], rffi.UINT, compilation_info=eci)
z3_get_smtlib_assumption = rffi.llexternal("Z3_get_smtlib_assumption", [Z3_context, rffi.UINT], Z3_ast, compilation_info=eci)
z3_get_smtlib_num_decls = rffi.llexternal("Z3_get_smtlib_num_decls", [Z3_context], rffi.UINT, compilation_info=eci)
z3_get_smtlib_decl = rffi.llexternal("Z3_get_smtlib_decl", [Z3_context, rffi.UINT], Z3_func_decl, compilation_info=eci)



if False:
    def wrap(func):
        def foo(*args):
            print func.__name__
            return func(*args)
        return foo
    for func in globals().keys():
        if hasattr(globals()[func], '__call__'):
            globals()[func] = wrap(globals()[func])
