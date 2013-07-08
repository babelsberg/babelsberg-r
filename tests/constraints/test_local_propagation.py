import py

from ..base import BaseTopazTest

class TestLocalPropagation(BaseTopazTest):
    def test_simple(self, space):
        w_res = space.execute("""
        require "libdeltablue"

        string, number = "0", 0
        always predicate: -> { string == number },
               methods:  -> {[ string <-> { number.to_s },
                               number <-> { string.to_i } ]}

        $res = [string, number]
        string = "23"
        $res << string << number
        number = 7
        $res << string << number
        return $res
        """)
        assert self.unwrap(space, w_res) == ["0", 0, "23", 23, "7", 7]
