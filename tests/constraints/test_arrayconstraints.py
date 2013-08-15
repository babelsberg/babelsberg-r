import operator
import py

from ..base import BaseTopazTest

E = 0.00000000000001

class TestArrayConstraints(BaseTopazTest):
    def execute(self, space, code, *libs):
        return [space.execute("""
                require "%s"
                $sum_execs = 0

                class Array
                  def sum
                    if empty?
                      $sum_execs += 1
                      return 0
                    end
                    self[0] + self[1..-1].sum
                  end
                end

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

    def test_simple_array2(self, space):
        with self.raises(space, "Cassowary::RequiredFailure"):
            space.execute(
            """
            require "libcassowary"
            ary = [1, 2, 3]
            always { ary[1] == 10 }
            ary[1] = 20
            """)

    def test_sum(self, space):
        w_ca, w_z3 = self.execute(
            space,
            """
            a = [1, 2, 3]
            always { a[0] == 10 && a[1] == 20 }
            always { a.sum == 60 }
            return a.sum, a
            """,
            "libcassowary", "libz3")
        assert self.unwrap(space, w_ca) == [60, [10, 20, 30]]
        assert self.unwrap(space, w_z3) == [60, [10, 20, 30]]

    def test_sum2(self, space):
        w_ca, w_z3 = self.execute(
            space,
            """
            a = [1, 2, 3]
            always { a.sum == 60 }
            $res = [$sum_execs, a.sum]
            a << 20
            return $res << $sum_execs << a.sum
            """,
            "libcassowary", "libz3")
        assert self.unwrap(space, w_ca) == [1, 60, 3, 60]
        assert self.unwrap(space, w_z3) == [1, 60, 3, 60]

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

    def test_linear_constraints(self, space):
        w_ca, w_z3 = self.execute(
            space,
            """
            a = [0.0, 0.0]
            always { a[0] * 2 + a[1] == 20.0 }
            always { a[0] + a[1] + a[2] * 2 == 38.0 }
            always { a.sum == 18 }
            return a[0], a[1], a[2]
            """,
            "libcassowary", "libz3")
        assert self.unwrap(space, w_ca) == [22, -24, 20]
        assert self.unwrap(space, w_z3) == [22, -24, 20]

    def test_sum_as_element(self, space):
        w_ca, w_z3 = self.execute(
            space,
            """
            a = [0, 10]
            always { a.sum == 18 }
            always { a[0] == a.sum }
            return a.sum, a
            """,
            "libcassowary", "libz3")
        assert self.unwrap(space, w_ca) == [18, [18, 0]]
        assert self.unwrap(space, w_z3) == [18, [18, 0]]

    def test_progression(self, space):
        w_ca = space.execute(
            """
            require 'libcassowary'
            require 'libarraysolver'

            a = [0, 10, 20, 30, 40]
            (0...(a.size - 1)).each do |i|
              always { a[i] > a[i + 1] }
            end
            always { a.sum == 50 }
            return a
            """)
        result = self.unwrap(space, w_ca)
        assert reduce(operator.add, result) == 50
        for i in xrange(len(result) - 1):
            assert result[i] > result[i + 1]

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

    def test_cyclices_among_regions(self, space):
        w_ca, w_z3 = self.execute(
            space,
            """
            a = [0, 0, 0]
            always do
              (a.length == a[0]) &&
              (a.length <= 3) &&
              (a.sum == 10) &&
              (a[1] == 2)
            end
            return a
            """,
            "libcassowary", "libz3")
        assert self.unwrap(space, w_ca) == [3, 2, 5]
        assert self.unwrap(space, w_z3) == [3, 2, 5]

    def test_inject(self, space):
        w_ca, w_z3 = self.execute(
            space,
            """
            a = [0, 0, 0]
            always do
              a.inject(0) { |memo, ea| memo + ea } == 100
            end
            p a
            return a
            """,
            "libcassowary", "libz3")
        assert reduce(operator.add, self.unwrap(space, w_ca)) == 100
        assert reduce(operator.add, self.unwrap(space, w_z3)) == 100
