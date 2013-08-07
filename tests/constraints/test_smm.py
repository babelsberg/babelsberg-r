import os
import platform
import subprocess

import pytest

from topaz.main import _entry_point


class TestMain(object):
    def run(self, space, tmpdir, file=None, status=0, ruby_args=[], argv=[]):
        args = ["topaz"]
        args += ruby_args
        f = os.path.abspath(os.path.join(__file__, "..", "constraintfixtures", file))
        args.append(str(f))
        args += argv
        res = _entry_point(space, args)
        assert res == status
        return f

    # this version of the program outputs the solution rather than just saying that it worked
    def test_smm(self, space, tmpdir, capfd):
        self.run(space, tmpdir, "smm.rb")
        out, err = capfd.readouterr()
        assert out.split('\n')[-2] == u"solution: [s,e,n,d,m,o,r,y] = [9, 5, 6, 7, 1, 0, 8, 2]"
