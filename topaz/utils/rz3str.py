import os
import platform
import sys

from rpython.rtyper.tool import rffi_platform
from rpython.rtyper.lltypesystem import rffi, lltype
from rpython.translator.tool.cbuild import ExternalCompilationInfo

from topaz.utils.rz3 import Z3_context, Z3_sort, Z3_ast, Z3_astP, Z3_func_decl, Z3_bool, z3_lib, z3_build_path, Z3Error
from topaz.system import IS_WINDOWS, IS_POSIX, IS_LINUX, IS_64BIT


z3str_dir = os.path.abspath(os.path.join(
    os.path.dirname(__file__),
    os.path.pardir,
    os.path.pardir,
    "dependencies",
    "z3str"
))
z3str_include_path = z3str_dir
z3str_build_path = z3str_dir
z3str_exe = os.path.join(z3str_build_path, "libz3str")
z3str_lib = "z3str"
if IS_WINDOWS:
    z3str_exe += ".dll"
elif IS_LINUX:
    z3str_exe += ".so"
else:
    z3str_exe += ".dylib"


if not os.path.isfile(z3str_exe):
    old_dir = os.getcwd()
    os.chdir(z3str_dir)
    try:
        if IS_WINDOWS:
            os.system("nmake")
        elif IS_POSIX:
            os.system("make")
        else:
            raise NotImplementedError("cannot build z3 on non-windows and non-posix systems")
    finally:
        os.chdir(old_dir)

eci = ExternalCompilationInfo(
    includes=["strTheory.h"],
    include_dirs=[z3str_include_path],
    libraries=[z3_lib, z3str_lib],
    library_dirs=[z3_build_path, z3str_build_path]
)

class CConfig:
    _compilation_info_ = eci
    if IS_WINDOWS:
        calling_conv = "win"
    else:
        calling_conv = "c"

globals().update(rffi_platform.configure(CConfig))

# String
Z3_theory = rffi.COpaquePtr("Z3_theory")
z3_get_string_sort_from_theory = rffi.llexternal("my_get_String_sort", [Z3_theory], Z3_sort, compilation_info=eci)
z3_mk_str_theory = rffi.llexternal("mk_pa_theory", [Z3_context], Z3_theory, compilation_info=eci)
# const string value
z3_mk_str_value = rffi.llexternal("my_mk_str_value", [Z3_theory, rffi.CCHARP], Z3_ast, compilation_info=eci)
# string variable with name
z3_mk_str_var = rffi.llexternal("my_mk_str_var", [Z3_theory, rffi.CCHARP], Z3_ast, compilation_info=eci)

z3_str_final_check = rffi.llexternal("cb_final_check", [Z3_theory], Z3_bool, compilation_info=eci)
z3_str_init_search = rffi.llexternal("cb_init_search", [Z3_theory], lltype.Void, compilation_info=eci)

z3_mk_str_concat = rffi.llexternal("mk_concat", [Z3_theory, Z3_ast, Z3_ast], Z3_ast, compilation_info=eci)
z3_mk_str_length = rffi.llexternal("mk_length", [Z3_theory, Z3_ast], Z3_ast, compilation_info=eci)

def str_reduce_method(name, nullptr=False):
    def create_method(func, name):
        def method(theory, left, right):
            args = lltype.malloc(Z3_astP.TO, 2, flavor='raw')
            args[0] = left
            args[1] = right
            if nullptr:
                nullptr = lltype.malloc(Z3_astP.TO, 1, flavor='raw')
                ast = func(theory, args, nullptr)
                lltype.free(nullptr, flavor='raw')
            else:
                ast = func(ctx, 2, ptr)
            lltype.free(args, flavor='raw')
            return ast
        method.__name__ = name.lower()
        globals()["z3_str_" + name.lower()] = method
    if nullptr:
        create_method(
            rffi.llexternal("reduce_" + name, [Z3_theory, Z3_astP, Z3_astP], Z3_ast, compilation_info=eci),
            name
        )
    else:
        create_method(
            rffi.llexternal("reduce_" + name, [Z3_theory, Z3_astP], Z3_ast, compilation_info=eci),
            name
        )
str_reduce_method("contains")
str_reduce_method("endswith")
str_reduce_method("startswith")
str_reduce_method("subStr")
# str_reduce_method("replace")
str_reduce_method("indexof", nullptr=True)


# Old api
z3_assert_cnstr = rffi.llexternal("Z3_assert_cnstr", [Z3_context, Z3_ast], lltype.Void, compilation_info=eci)
z3_check = rffi.llexternal("Z3_check", [Z3_context], Z3_bool, compilation_info=eci)
