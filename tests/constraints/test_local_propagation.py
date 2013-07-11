import py

from ..base import BaseTopazTest

class TestLocalPropagation(BaseTopazTest):
    def test_simple(self, space):
        w_res = space.execute("""
        require "libdeltablue"

        string, number = "0", 0
        always predicate: -> { string == number.to_s },
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

    def test_interface_constraint(self, space):
        w_res = space.execute("""
        require "libdeltablue"

        to_i_able = nil
        always predicate: -> { to_i_able.respond_to? :to_i },
               methods: -> {[ to_i_able <-> { "" } ]}

        $res = []
        $res << to_i_able
        to_i_able = 100
        $res << to_i_able
        return $res
        """)
        assert self.unwrap(space, w_res) == ["", 100]

    def test_class_constraint_raises(self, space):
        with self.raises(space, "RuntimeError", "Failed to enforce a required constraint"):
            space.execute("""
            require "libdeltablue"
            string = nil

            always predicate: -> { string.is_a? String },
                   methods: -> {[ string <-> { "" } ]}

            string = 10
            """)

    def test_non_required_class_constraint_doesnt_raise(self, space):
        space.execute("""
        require "libdeltablue"
        string = nil

        always predicate: -> { string.is_a? String },
               methods: -> {[ string <-> { "" } ]},
               priority: :medium

        string = 10
        # Fails if this raises
        """)

    def test_simple_alt_syntax(self, space):
        w_res = space.execute("""
        require "libdeltablue"

        string, number = "0", 0
        always predicate: -> { string == number.to_s } do
          [string <-> { number.to_s },
           number <-> { string.to_i }]
        end

        $res = [string, number]
        string = "23"
        $res << string << number
        number = 7
        $res << string << number
        return $res
        """)
        assert self.unwrap(space, w_res) == ["0", 0, "23", 23, "7", 7]

    def test_arithmetic(self, space):
        w_res = space.execute("""
        require "libdeltablue"
        $res = []
        x, y, z = 0, 0, 0

        always predicate: -> { x + y == z } do
          [x <-> { z - y },
           y <-> { z - x },
           z <-> { x + y }]
        end

        $res << [x, y, z]
        x = 20
        $res << [x, y, z]
        z = 100
        $res << [x, y, z]
        return $res
        """)
        assert self.unwrap(space, w_res) == [
            [0, 0, 0],
            [20, -20, 0],
            [20, 80, 100]
        ]

    def test_identity_constraint(self, space):
        w_res = space.execute("""
        require "libdeltablue"
        $res = []
        a = Object.new
        b = Object.new

        always { a.equal? b }
        $res << a.object_id << b.object_id
        a = Object.new
        $res << a.object_id << b.object_id
        return $res
        """)
        res = self.unwrap(space, w_res)
        assert res[0] == res[1]
        assert res[2] == res[3]
