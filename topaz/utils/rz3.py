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
if WINNT:
    z3_exe += ".exe"

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
        os.system("%s %s" % (
                my_python,
                os.path.join(
                    z3_dir,
                    "scripts",
                    "mk_make.py"
                )
        ))
        os.chdir(os.path.join(z3_dir, "build"))
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
    libraries=["z3"],
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
        [Z3_context, Z3_ast, rffi.INTP, rffi.INTP],
        rffi.INT,
        compilation_info=eci
    )
    def z3_get_numeral_real(ctx, ast):
        nom = lltype.malloc(rffi.INTP.TO, 1, flavor='raw', zero=True)
        den = lltype.malloc(rffi.INTP.TO, 1, flavor='raw', zero=True)
        status = _z3_get_numeral_real(ctx, ast, nom, den)
        fnom = float(int(nom[0]))
        fden = float(int(den[0]))
        lltype.free(nom, flavor='raw')
        lltype.free(den, flavor='raw')
        if status != 1:
            raise Z3Error("result does not fit into int-type")
        else:
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

z3_get_ast_kind = rffi.llexternal("Z3_get_ast_kind", [Z3_context, Z3_ast], rffi.INT, compilation_info=eci)
z3_get_app_decl = rffi.llexternal("Z3_get_app_decl", [Z3_context, Z3_ast], Z3_func_decl, compilation_info=eci)

# Sorts
Z3_sort = rffi.COpaquePtr("Z3_sort")
z3_mk_int_sort = rffi.llexternal("Z3_mk_int_sort", [Z3_context], Z3_sort, compilation_info=eci)
z3_mk_real_sort = rffi.llexternal("Z3_mk_real_sort", [Z3_context], Z3_sort, compilation_info=eci)
z3_mk_bool_sort = rffi.llexternal("Z3_mk_bool_sort", [Z3_context], Z3_sort, compilation_info=eci)

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
z3_mk_true = rffi.llexternal("Z3_mk_true", [Z3_context], Z3_ast, compilation_info=eci)
z3_mk_false = rffi.llexternal("Z3_mk_false", [Z3_context], Z3_ast, compilation_info=eci)
z3_get_bool_value = rffi.llexternal("Z3_get_bool_value", [Z3_context, Z3_ast], rffi.INT, compilation_info=eci)

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
