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

    def test_smm(self, space, tmpdir, capfd):
        self.run(space, tmpdir, "smm.rb")
        out, err = capfd.readouterr()
        print "testing - where is this output?"
        assert out.split('\n')[-2] == u"Working solution"
