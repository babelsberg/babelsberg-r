import py

from ..base import BaseTopazTest

class TestLocalPropagation(BaseTopazTest):
    def test_simple(self, space):
        w_res = space.execute("""
        require "libdeltablue"

        string, number = "0", 0
        always { string <-> { number.to_s }
                 number <-> { string.to_i } }

        $res = [string, number]
        string = "23"
        $res << string << number
        number = 7
        $res << string << number
        return $res
        """)
        assert self.unwrap(space, w_res) == ["0", 0, "23", 23, "7", 7]

    def test_pythagoras(self, space):
        w_res = space.execute("""
        require "libdeltablue"

        a, b, c = 0, 0, 0
        always predicate: ->{ a ** 2 + b ** 2 == c ** 2 },
               methods: ->{{ a => ->{ Math.sqrt(c**2 - b**2) },
                             b => ->{ Math.sqrt(c**2 - a**2) },
                             c => ->{ Math.sqrt(a**2 + b**2) }}}

        $res = [[a, b, c]]
        a = 100
        $res << [a, b, c]
        b = 20
        $res << [a, b, c]
        c = 17
        $res << [a, b, c]
        return $res
        """)
        assert self.unwrap(space, w_res) == [
            [0, 0, 0],
            [100, 0, 0],
        ]

    def test_a_and_b(self, space):
        w_res = space.execute("""
        require "libdeltablue"

        a, b = 0, 0
        always predicate: ->{ a + b == 2 },
               methods: ->{{ a => ->{ 2 - b },
                             b => ->{ 2 - a }}}

        $res = [[a, b]]
        a = 100
        $res << [a, b]
        b = 20
        $res << [a, b, c]
        c = 17
        $res << [a, b, c]
        return $res
        """)
        assert self.unwrap(space, w_res) == [
            [0, 0, 0],
            [100, 0, 0],
        ]
