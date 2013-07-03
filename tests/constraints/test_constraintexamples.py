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

    def test_kaleidoscopebench(self, space, tmpdir, capfd):
        self.run(space, tmpdir, "benchmark.rb")
        out, err = capfd.readouterr()
        assert out == u"""Cassowary constraint solver loaded.
<Mouse: 0.0>
<Mercury: 0.0->0.0>
<Thermometer: 200.0->0.0>
<grey Rectangle: 0.0->0.0>
<white Rectangle: 200.0->0.0>
0.0
<Display: 0.0>
"""

    def test_animal_puzzle(self, space, tmpdir, capfd):
        self.run(space, tmpdir, "animal_puzzle.rb")
        out, err = capfd.readouterr()
        assert out == u"""Z3 constraint solver loaded.
Spend exactly 100 dollars and buy exactly 100 animals. Dogs cost
15 dollars, cats cost 1 dollar, and mice cost 25 cents each. You
have to buy at least one of each. How many of each should you buy?
Dogs: 3, cats: 41, mice: 56
"""

    def test_animal_puzzle(self, space, tmpdir, capfd):
        self.run(space, tmpdir, "animal_puzzle.rb")
        out, err = capfd.readouterr()
        assert out == u"""Z3 constraint solver loaded.
Spend exactly 100 dollars and buy exactly 100 animals. Dogs cost
15 dollars, cats cost 1 dollar, and mice cost 25 cents each. You
have to buy at least one of each. How many of each should you buy?
Dogs: 3, cats: 41, mice: 56
"""

    def test_eight_queens(self, space, tmpdir, capfd):
        self.run(space, tmpdir, "nqueens.rb")
        out, err = capfd.readouterr()
        assert out == u"""Z3 constraint solver loaded.
[#<Queen: 0x0>, #<Queen: 1x3>, #<Queen: 2x1>, #<Queen: 3x2>, #<Queen: 4x4>, #<Queen: 5x5>, #<Queen: 6x6>, #<Queen: 7x7>]
"""
