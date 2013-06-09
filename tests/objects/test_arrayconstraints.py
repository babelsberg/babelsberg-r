import py

from ..base import BaseTopazTest

E = 0.00000000000001

class TestArrayConstraints(BaseTopazTest):
    def execute(self, space, code, *libs):
        return [space.execute("""
                require "%s"
                require "libarraysolver"

                %s
                """ % (lib, code)) for lib in libs]

    def test_simple_array(self, space):
        w_ca, w_z3 = self.execute(
            space,
            """
            ary = [1, 2, 3]
            always { ary[0] == 10 }
            return ary[0]
            """,
            "libcassowary", "libz3")
        assert self.unwrap(space, w_ca) == 10
        assert self.unwrap(space, w_z3) == 10

    def test_sum(self, space):
        w_ca, w_z3 = self.execute(
            space,
            """
            a = [1, 2, 3]
            always { a[0] == 10 && a[1] == 20 }
            always { a.sum == 60 }
            return a
            """,
            "libcassowary", "libz3")
        assert self.unwrap(space, w_ca) == [10, 20, 30]
        assert self.unwrap(space, w_z3) == [10, 20, 30]

    def test_length(self, space):
        w_ca, w_z3 = self.execute(
            space,
            """
            a = [1]
            always { a.length == 3 }
            return a
            """,
            "libcassowary", "libz3")
        assert self.unwrap(space, w_ca) == [1, 0, 0]
        assert self.unwrap(space, w_z3) == [1, 0, 0]

    def test_equality(self, space):
        w_ca, w_z3 = self.execute(
            space,
            """
            ary = [1]
            always { ary == [1, 2, 3] }
            return ary
            """,
            "libcassowary", "libz3")
        assert self.unwrap(space, w_ca) == [1, 2, 3]
        assert self.unwrap(space, w_z3) == [1, 2, 3]

    def test_variable_equality(self, space):
        w_ca, w_z3 = self.execute(
            space,
            """
            a = [1]
            b = [4, 5, 6]
            always { a == b }
            return a, b
            """,
            "libcassowary", "libz3")
        assert self.unwrap(space, w_ca)[0] == self.unwrap(space, w_ca)[1]
        assert self.unwrap(space, w_z3)[0] == self.unwrap(space, w_z3)[1]

    @py.test.mark.xfail
    def test_complex_equality(self, space):
        w_ca, w_z3 = self.execute(
            space,
            """
            class Point
              attr_accessor :x, :y
              def initialize(x, y)
                self.x = x
                self.y = y
              end

              def ==(other)
                other.x == self.x && other.y == self.y
              end
            end

            a = [Point.new(1, 1)]
            b = [Point.new(2, 2)]
            always { a == b }
            return a, b
            """,
            "libcassowary", "libz3")
        assert self.unwrap(space, w_ca)[0] == self.unwrap(space, w_ca)[1]
        assert self.unwrap(space, w_z3)[0] == self.unwrap(space, w_z3)[1]
