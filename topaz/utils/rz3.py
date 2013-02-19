import os
import sys

from pypy.rpython.tool import rffi_platform
from pypy.rpython.lltypesystem import rffi, lltype
from pypy.translator.tool.cbuild import ExternalCompilationInfo


WINNT = os.name == "nt"
POSIX = os.name == "posix"


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
        os.system("python scripts/mk_make.py")
        os.chdir("build")
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
    library_dirs=[onig_build_path]
    # separate_module_files=["rupypy/utils/re/rffi_helper.c"]
)

class CConfig:
    _compilation_info_ = eci
    if WINNT:
        calling_conv = "win"
    else:
        calling_conv = "c"

config = platform.configure(CConfig)

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
z3_get_numeral_string = rffi.llexternal(
    "Z3_get_numeral_string",
    [Z3_context, Z3_ast],
    rffi.CCHARP,
    compilation_info=eci
)
z3_get_ast_kind = rffi.llexternal("Z3_get_ast_kind", [Z3_context, Z3_ast], rffi.INT, compilation_info=eci)

# Sorts
Z3_sort = rffi.COpaquePtr("Z3_sort")
z3_mk_int_sort = rffi.llexternal("Z3_mk_int_sort", [Z3_context], Z3_sort, compilation_info=eci)

# Arithmetic
z3_mk_lt = rffi.llexternal("Z3_mk_lt", [Z3_context, Z3_ast, Z3_ast], Z3_ast, compilation_info=eci)

# Numerals
z3_mk_real = rffi.llexternal("Z3_mk_real", [Z3_context, rffi.INT, rffi.INT], Z3_ast, compilation_info=eci)
z3_mk_int = rffi.llexternal("Z3_mk_int", [Z3_context, rffi.INT, Z3_sort], Z3_ast, compilation_info=eci)

# Symbols
Z3_symbol = rffi.COpaquePtr("Z3_symbol")
z3_mk_string_symbol = rffi.llexternal(
    "Z3_mk_string_symbol",
    [Z3_context, rffi.CCHARP],
    Z3_symbol,
    compilation_info=eci
)

# Constants
z3_mk_const = rffi.llexternal("Z3_mk_const", [Z3_context, Z3_symbol, Z3_sort], compilation_info=eci)

# Models
Z3_model = rffi.COpaquePtr("Z3_model")
z3_model_get_const_interp = rffi.llexternal(
    "Z3_model_get_const_interp",
    [Z3_context, Z3_model, Z3_func_decl],
    Z3_ast,
    compilation_info=eci
)

# Solvers
Z3_bool = rffi.INT
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
