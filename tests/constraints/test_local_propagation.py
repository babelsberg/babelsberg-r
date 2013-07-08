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
