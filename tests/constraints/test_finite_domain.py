import py

from ..base import BaseTopazTest

E = 0.00000000000001

class TestFinitDomain(BaseTopazTest):
    def test_alldifferent(self, space):
        w_res = space.execute("""
        require "libz3"

        a = 10
        b = 10.0
        c = 10
        d = true
        e = true
        always { [a, b, c, d, e].alldifferent? }
        return a, b, c, d, e, [a, b, c, d, e].alldifferent?
        """)
        res = self.unwrap(space, w_res)
        assert res[0] != res[1]
        assert res[0] != res[2]
        assert res[1] != res[2]
        assert res[3] and not res[4] or not res[3] and res[4]
        assert res[5]

    def test_alldifferent_ary(self, space):
        w_res = space.execute("""
        require "libz3"
        require "libarraysolver"

        ary = [0, 0, 0, 0]
        always { ary.alldifferent? }
        return ary
        """)
        res = self.unwrap(space, w_res)
        assert res[0] != res[1] and res[0] != res[2] and res[0] != res[3]
        assert res[1] != res[2] and res[1] != res[3]
        assert res[2] != res[3]
