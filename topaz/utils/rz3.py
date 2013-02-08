import os
import sys

from pypy.rpython.tool import rffi_platform
from pypy.rpython.lltypesystem.rffi import *
from pypy.rpython.lltypesystem.lltype import *
from pypy.translator.tool.cbuild import ExternalCompilationInfo


WINNT = os.name == "nt"
POSIX = os.name == "posix"


class CConfig:
    includes = ["rffi_z3.h"]

    z3_dir = os.path.abspath(os.path.join(
        os.path.dirname(__file__),
        os.path.pardir,
        os.path.pardir,
        "dependencies",
        "z3"
    ))
    z3_exe = os.path.join(z3_dir, "build", "z3")
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
        includes=includes,
        include_dirs=[
            onig_path,
            os.getcwd() + "/rupypy/utils/re"
        ],
        libraries=["onig"],
        library_dirs=[onig_lib_path],
        separate_module_files=["rupypy/utils/re/rffi_helper.c"]
    )
