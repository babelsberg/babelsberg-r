import py

from ..base import BaseTopazTest

E = 0.00000000000001

class TestConstraintVariableObject(BaseTopazTest):
    def execute(self, space, code, *libs):
        return [space.execute("""
                require "%s"

                %s
                """ % (lib, code)) for lib in libs]

    def test_names(self, space):
        space.execute("ConstraintVariable")

    def test_local(self, space):
        w_cassowary, w_z3 = self.execute(
            space,
            """
            a = 1
            always { a == 10 }
            return a
            """,
            "libz3", "libcassowary")
        assert self.unwrap(space, w_cassowary) == 10
        assert self.unwrap(space, w_z3) == 10
        w_cassowary, w_z3 = self.execute(
            space,
            """
            b = 1
            always { b > 10 }
            b = 11
            return b
            """,
            "libz3", "libcassowary")
        assert self.unwrap(space, w_cassowary) == 11
        assert self.unwrap(space, w_z3) == 11

    def test_ivar(self, space):
        w_res = space.execute("""
        require "libcassowary"
        @a = 1
        always { @a == 10 }
        return @a
        """)
        assert self.unwrap(space, w_res) == 10
        w_res = space.execute("""
        @b = 1
        always { @b > 10 }
        @b = 11
        return @b
        """)
        assert self.unwrap(space, w_res) == 11

    def test_cvar(self, space):
        w_res = space.execute("""
        require "libcassowary"
        @@a = 1
        always { @@a == 10 }
        return @@a
        """)
        assert self.unwrap(space, w_res) == 10
        w_res = space.execute("""
        @@b = 1
        always { @@b > 10 }
        @@b = 11
        return @@b
        """)
        assert self.unwrap(space, w_res) == 11

    def test_simple_path(self, space):
        w_res = space.execute("""
        require "libcassowary"
        res = []
        class Point
          def x
            @x
          end

          def y
            @y
          end

          def initialize(x, y)
            @x = x
            @y = y
            always { @x >= 0 }
            always { @y >= 0 }
            always { @x < 640 }
            always { @y < 480 }
          end
        end

        pt1 = Point.new(-1, 10)
        pt2 = Point.new(20, 20)
        res << [[pt1.x, pt1.y], [pt2.x, pt2.y]]
        always { pt1.x == pt2.x }
        res << [[pt1.x, pt1.y], [pt2.x, pt2.y]]
        always { pt1.x == 5 }
        res << [[pt1.x, pt1.y], [pt2.x, pt2.y]]
        """)
        assert self.unwrap(space, w_res) == [
            [[0, 10], [20, 20]],
            [[0, 10], [0, 20]],
            [[5, 10], [5, 20]]
        ] or self.unwrap(space, w_res) == [
            [[0, 10], [20, 20]],
            [[20, 10], [20, 20]],
            [[5, 10], [5, 20]]
        ]

    def test_complex_path(self, space):
        w_res = space.execute("""
        require "libcassowary"
        res = []
        class Point
          def x
            @x
          end

          def y
            @y
          end

          def initialize(x, y)
            @x = x
            @y = y
            always { @x >= 0 }
            always { @y >= 0 }
            always { @x < 640 }
            always { @y < 480 }
          end
        end

        class HorizontalLine
          def start
            @start
          end

          def end
            @end
          end

          def initialize(pt1, pt2)
            @start = pt1
            @end = pt2
            always { pt1.y == pt2.y }
          end

          def length
            @end.x - @start.x
          end
        end

        h = HorizontalLine.new(Point.new(1, 1), Point.new(2, 2))
        always { h.length >= 100 }
        return h.length
        """)
        assert self.unwrap(space, w_res) == 100

    def test_errors(self, space):
        with self.raises(space, "ArgumentError"):
            space.execute("always")
        with self.raises(space, "TypeError"):
            space.execute("always { true }")
        with self.raises(space, "TypeError"):
            space.execute("always { true }")

    def test_preferences(self, space):
        w_res = space.execute("""
        require "libcassowary"
        res = []
        x = 10
        always(:strong) { x > 10 }
        res << x
        always(:medium) { x < 5 }
        res << x
        always(:required) { x < 10 }
        res << x
        return res
        """)
        assert self.unwrap(space, w_res) == [11, 11, 9]

    def test_quadratic(self, space):
        w_res = space.execute("""
        require "libz3"
        a = 1.0
        always { a ** 2.0 < 16 }
        return a
        """)
        assert self.unwrap(space, w_res) == -3

    def test_quadratic_real(self, space):
        w_res = space.execute("""
        require "libz3"
        a = 1.0
        always { a ** 2.0 == 30.25 }
        return a
        """)
        assert self.unwrap(space, w_res) == -5.5

    def test_quadratic_pos_real(self, space):
        w_res = space.execute("""
        require "libz3"
        a = 1.0
        always { a ** 2.0 == 30.25 }
        always { a > 0 }
        return a
        """)
        assert self.unwrap(space, w_res) == 5.5

    def test_boolean(self, space):
        w_res = space.execute("""
        require "libz3"
        a = false
        always { a == true }
        return a
        """)
        assert w_res is space.w_true

    def test_div(self, space):
        w_res = space.execute("""
        require "libz3"
        x = 5
        y = 1
        always { x / y == 2 }
        return x, y
        """)
        assert self.unwrap(space, w_res) == [1, 0]

    def test_complex_path_with_z3(self, space):
        w_res = space.execute("""
        require "libz3"
        res = []
        class Point
          def x
            @x
          end

          def y
            @y
          end

          def initialize(x, y)
            @x = x
            @y = y
            always { @x >= 0 }
            always { @y >= 0 }
            always { @x < 640 }
            always { @y < 480 }
          end
        end

        class HorizontalLine
          def start
            @start
          end

          def end
            @end
          end

          def initialize(pt1, pt2)
            @start = pt1
            @end = pt2
            always { pt1.y == pt2.y }
          end

          def length
            @end.x - @start.x
          end
        end

        h = HorizontalLine.new(Point.new(1, 1), Point.new(2, 2))
        always { h.length >= 100 }
        return h.length
        """)
        assert self.unwrap(space, w_res) >= 100

    def test_attr_reader(self, space):
        w_res = space.execute("""
        require "libz3"
        res = []
        class Point
          attr_accessor :x, :y

          def initialize(x, y)
            self.x = x
            self.y = y
            always { self.x >= 0 }
            always { self.y >= 0 }
          end
        end
        pt = Point.new(-10, -10)
        return pt.x, pt.y
        """)
        assert self.unwrap(space, w_res) == [0, 0]

    def test_invalidation_along_path(self, space):
        code = """
        $area_executions = 0
        res = []

        class Point
          attr_accessor :x, :y

          def initialize(x, y)
            self.x, self.y = x, y
          end
        end

        class Rect
          attr_accessor :origin, :extent

          def initialize(origin, extent)
            self.origin, self.extent = origin, extent
          end

          def area
            $area_executions += 1
            extent.x * extent.y
          end
        end

        extent_1 = Point.new(10, 10)
        r = Rect.new(Point.new(0, 0), extent_1)
        always { r.area > 100 }
        res << r.extent.x << r.extent.y

        r.extent.x = 100
        res << r.extent.x << r.extent.y

        r.extent = Point.new(5, 5)
        res << r.extent.x << r.extent.y

        r.extent = Point.new(50, 50)
        res << r.extent.x << r.extent.y

        res << extent_1.x << extent_1.y
        extent_1.x = 1
        res << extent_1.x << extent_1.y

        return res, $area_executions
        """
        [w_res] = self.execute(space, code, "libz3")
        assert self.unwrap(space, w_res) == [
            [
                101, 1, # invalid point is adjusted
                100, 2, # Assignment works, adjusts other coordinate
                101, 1, # Setting a new Point that is too small
                101, 1, # Setting a new Point that would work
                100, 2, # point that is no longer constrained keeps last value
                1, 2,   # subsequent change then works imperatively
            ],
            3
        ]

    def test_mix_bools_and_numbers(self, space):
        w_res = space.execute("""
        require "libz3"

        a = true
        b = 10
        always { a == b > 10 }
        return a, b
        """)
        assert self.unwrap(space, w_res) == [True, 11]

    @py.test.mark.xfail
    def test_constraint_solver_interaction_different_domains(self, space):
        w_res = space.execute("""
        require "libz3"
        require "libcassowary"

        raise "Test problem" unless 1.for_constraint("name").is_a?(Cassowary::Variable)

        a = true
        b = 10
        always { b < 11 }
        always { a == b > 10 }
        return a, b
        """)
        assert self.unwrap(space, w_res) == [False, 10.0]

    @py.test.mark.xfail
    def test_constraint_solver_interaction_same_domain(self, space):
        w_res = space.execute("""
        require "libz3"

        a = 20
        b = 10
        always { b > 10 }

        require "libcassowary"
        raise "Test problem" unless 1.for_constraint("name").is_a?(Cassowary::Variable)

        always { a < b }

        return a, b
        """)
        assert self.unwrap(space, w_res) == [10.0, 11]

    def test_solver_variable_delegation(self, space):
        w_cassowary, w_z3 = self.execute(
            space,
            """
            class FloatString < String
              def assign_constraint_value(a_value)
                clear.insert(0, a_value.to_s)
              end

              def for_constraint(name)
                @float ||= self.to_f
                __constrain__ { @float }
              end
            end

            a = 1.0
            b = FloatString.new("2.9")
            always { a > b }
            return a, b
            """,
            "libcassowary", "libz3")
        assert self.unwrap(space, w_cassowary) == [3.9, "2.9"]
        assert (self.unwrap(space, w_z3) == [0, "-1.0"] or
                self.unwrap(space, w_z3) == [3.9, "2.9"])

    def test_solver_ro_variable_delegation(self, space):
        w_cassowary, w_z3 = self.execute(
            space,
            """
            class FloatString < String
              attr_reader :float
              def assign_constraint_value(a_value)
                # raise "shouldn't happen"
              end

              def for_constraint(name)
                unless @float
                  @float = 0
                  always { @float == self.to_f }
                end
                __constrain__ { @float }
              end
            end

            a = 1.0
            b = FloatString.new("2.9")
            always { a == b }
            return a, b
            """,
            "libcassowary", "libcassowary")
        res = self.unwrap(space, w_cassowary)
        assert 2.9 - E <= res[0] <= 2.9 + E
        assert "2.9" == res[1]

    def test_solver_ro_variable_delegation_w_update(self, space):
        w_cassowary, w_z3 = self.execute(
            space,
            """
            class FloatString < String
              def assign_constraint_value(a_value)
                # raise "shouldn't happen"
              end

              def for_constraint(name)
                unless @float
                  @float = 0
                  @stay = always { @float == self.to_f }
                end
                __constrain__ { @float }
              end

              def update(float)
                self.clear.insert(0, float.to_s)
                if @stay
                  @stay.disable
                  @stay = always { @float == self.to_f }
                end
              end
            end

            res = []
            a = 1.0
            b = FloatString.new("2.9")
            always { a == b }
            res << a << b
            b.update(1.1)
            return res << a << b
            """,
            "libcassowary", "libcassowary")
        res = self.unwrap(space, w_cassowary)
        assert 2.9 - E <= res[0] <= 2.9 + E
        assert "1.1" == res[1]
        assert 1.1 - E <= res[2] <= 1.1 + E
        assert "1.1" == res[3]

    def test_must_not_change_var(self, space):
        w_cassowary, w_z3 = self.execute(
            space,
            """
            a = 1.0
            b = "2.0"
            always { a == b.to_f }
            return a, b
            """,
            "libcassowary", "libz3")
        assert self.unwrap(space, w_cassowary) == [2.0, "2.0"]
        assert self.unwrap(space, w_z3) == [2.0, "2.0"]

    def test_path_with_strength(self, space):
        w_res = space.execute("""
        require "libcassowary"

        $executions = 0

        content = "100"
        quality = 50
        res = []

        stay = always(:strong) { $executions += 1; quality == content.to_f }
        res << quality
        always { quality < 100 }
        always { quality > 0 }
        res << quality
        content = "111" # this will re-execute the stay block, and
                        # if it looses the strength, it will raise
                        # a RequiredFailure
        res << quality
        return res, $executions
        """)
        assert self.unwrap(space, w_res) == [[100, 99, 99], 2]
