import copy
import py

from ..base import BaseTopazTest

E = 0.00000000000001

class TestConstraintVariableObject(BaseTopazTest):
    def execute(self, space, code, *libs):
        results = []
        for lib in libs:
            results.append(copy.deepcopy(space).execute("""
            require "%s"

            %s
            """ % (lib, code)))
        return results[0] if len(results) == 1 else results

    def test_names(self, space):
        space.execute("ConstraintVariable")

    def test_nothing(self, space, capfd):
        space.execute("always { true }")
        out, err = capfd.readouterr()
        assert err.startswith("Warning")

    def test_execution_mode_switching(self, space):
        w_res = space.execute("""
        require "libcassowary"
        class A < ConstraintObject
          def initialize
            @a = 1
          end

          def normal
            @a
          end

          def block(&block)
            @a
          end

          def splat(*args)
            @a
          end
        end

        class B
          attr_reader :a
          def initialize
            @a = 1
          end
        end

        a = A.new
        b = B.new
        return [Constraint.new { a.normal }.value,
                Constraint.new { a.block(&:to_s) }.value,
                Constraint.new { a.splat 2, 3, 4 }.value,
                Constraint.new { b.a }.value.is_a?(ConstraintObject) ]
        """)
        assert self.unwrap(space, w_res) == [1, 1, 1, True]

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

    def test_double_constraint(self, space):
        w_res = space.execute("""
        require "libcassowary"
        a = 0
        always { a >= 10 }
        a = 15
        always { a <= 11 }
        return a
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
        x = 5.0
        y = 1.0
        always { x / y == 2 }

        a = 5
        b = 1
        always { a / b == 2 }
        return x, y, a, b
        """)
        assert self.unwrap(space, w_res) == [-1, 0, 38, 0]

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
        $area_executions = []
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
            $area_executions << 1
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
        w_res = self.execute(space, code, "libz3")
        assert self.unwrap(space, w_res) == [
            [
                101, 1, # invalid point is adjusted
                100, 2, # Assignment works, adjusts other coordinate
                101, 1, # Setting a new Point that is too small
                101, 1, # Setting a new Point that would work
                100, 2, # point that is no longer constrained keeps last value
                1, 2,   # subsequent change then works imperatively
            ],
            [1, 1, 1]
        ]

    def test_mix_bools_and_numbers(self, space):
        w_res = space.execute("""
        require "libz3"

        a = true
        b = 10.0

        x = true
        y = 10
        always { b > 10 }
        always { y > 10 }
        always { a == b > 10 }
        always { x == y > 10 }
        return a, b, x, y
        """)
        assert self.unwrap(space, w_res) == [True, 11, True, 11]

    def test_constraint_solver_interaction_different_domains(self, space):
        w_res = space.execute("""
        require "libz3"
        require "libcassowary"

        a = true
        b = 15
        always { b < 11 }
        $res = [[a, b]]
        always { a == b > 10 }
        $res << [a, b]
        return $res
        """)
        assert self.unwrap(space, w_res) == [[True, 10], [False, 10.0]]

        w_res = space.execute("""
        require "libz3"
        require "libcassowary"

        a = true
        b = 15
        always(solver: Cassowary::SimplexSolver.instance) { b < 11 }
        $res = [[a, b]]
        always(solver: Z3::Instance) { a == b > 10 }
        $res << [a, b]
        return $res
        """)
        assert self.unwrap(space, w_res) == [[True, 10], [False, 10.0]]

        w_res = space.execute("""
        require "libz3"
        require "libcassowary"

        a = true
        b = 15
        always(solver: Cassowary::SimplexSolver.instance) { b < 11 }
        $res = [[a, b]]
        always(solver: Z3::Instance) { a == b > 10 }
        $res << [a, b]
        return $res
        """)
        assert self.unwrap(space, w_res) == [[True, 10], [False, 10.0]]

    def test_constraint_solver_interaction_z3_on_top(self, space):
        w_res = space.execute("""
        require "libz3"
        require "libcassowary"

        class Cassowary::SimplexSolver
          def weight
            -1
          end
        end

        class Z3
          def weight
            1000 # ensure that Z3 is upstream from Cassowary
          end
        end

        a = true
        b = 15
        always(solver: Cassowary::SimplexSolver.instance) { b <= 10 }
        $res = [[a, b]]
        always(solver: Z3::Instance) { a == b >= 10 && a }
        $res << [a, b]
        return $res
        """)
        assert self.unwrap(space, w_res) == [[True, 10], [True, 10.0]]

    def test_inconsistent_constraints_solver_interaction(self, space):
        with self.raises(space, "RuntimeError", "unsatisfiable constraint system"):
            space.execute("""
            require "libz3"
            require "libcassowary"

            b = 15
            always(solver: Cassowary::SimplexSolver.instance) { b <= 10 }
            $res = [b]
            always(solver: Z3::Instance) { b > 100 }
            $res << b
            return $res
            """)

    def test_constraint_solver_interaction_different_domains_failure(self, space):
        with self.raises(space, "RuntimeError", "unsatisfiable constraint system"):
            space.execute("""
            require "libz3"
            require "libcassowary"

            class Cassowary::SimplexSolver
              def weight
                1000
              end
            end

            class Z3
              def weight
                -1000 # ensure that Z3 is donwstream from Cassowary
              end
            end

            a = true
            b = 15
            always(solver: Cassowary::SimplexSolver.instance) { b < 11 }
            always(solver: Z3::Instance) { a == b > 100 }
            always(solver: Z3::Instance) { a } # cannot be satisfied, as `b' is readonly from Z3
            """)

    def test_constraint_solver_interaction_same_domain(self, space):
        w_res = space.execute("""
        require "libz3"
        require "libcassowary"

        a = 15
        b = 10
        always(solver: Z3::Instance) { b > 10 }
        $res = [a,b]
        always(solver: Cassowary::SimplexSolver.instance) { a < b }
        return $res << a << b
        """)
        assert (
            self.unwrap(space, w_res) == [15, 11, 10, 11] or
            # depending on whether Cassowary manipulates a or b
            self.unwrap(space, w_res) == [15, 11, 15, 16]
        )

    def test_solver_interaction_assignment(self, space):
        w_res = space.execute("""
        require "libcassowary"
        require "libz3"

        a = true
        b = 10
        always(solver: Cassowary::SimplexSolver.instance) { b >= 11 }
        $res = [a, b]
        always(solver: Z3::Instance) { a == (b > 15) }
        $res << a << b
        b = 20
        $res << a << b
        return $res
        """)
        assert self.unwrap(space, w_res) == [
            True, 11, # a is unchanged, b is >= 11
            False, 11, # Z3 cannot change b, so a is changed to false
            True, 20, # after cassowary assigned 20, Z3 is triggered and picks up 20
        ]

    @py.test.mark.xfail
    def test_solver_interaction_assignment2(self, space):
        w_res = space.execute("""
        require "libcassowary"
        require "libz3"

        a = true
        b = 10
        c = 20
        always(solver: Cassowary::SimplexSolver.instance) { b + c >= 20 }
        $res = [a, b, c]
        always(solver: Z3::Instance) { a == (b > 15) }
        $res << a << b << c
        c = 1
        $res << a << b << c
        return $res
        """)
        assert self.unwrap(space, w_res) == [
            True, 10, 20, # everything's fine
            False, 10, 20, # Z3 cannot change b, so a is changed to false
            True, 19, 1, # after cassowary assigned 19 to b, Z3 is triggered and picks it up
        ]

    def test_solver_variable_delegation(self, space):
        w_cassowary = self.execute(
            space,
            """
            class FloatString < String
              def assign_constraint_value(a_value)
                clear.insert(0, a_value.to_s)
              end

              def for_constraint(name)
                @float ||= self.to_f
                Constraint.new { @float }
              end
            end

            a = 1.0
            b = FloatString.new("2.9")
            always { a > b }
            return a, b
            """,
            "libcassowary")
        assert (self.unwrap(space, w_cassowary) == [3.9, "2.9"] or
                self.unwrap(space, w_cassowary) == [1.0, "0.0"])

    def test_solver_ro_variable_delegation(self, space):
        w_cassowary = self.execute(
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
                Constraint.new { @float }
              end
            end

            a = 1.0
            b = FloatString.new("2.9")
            always { a == b }
            return a, b
            """,
            "libcassowary")
        res = self.unwrap(space, w_cassowary)
        assert 2.9 - E <= res[0] <= 2.9 + E
        assert "2.9" == res[1]

    def test_solver_ro_variable_delegation_w_update(self, space):
        w_cassowary = self.execute(
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
                Constraint.new { @float }
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
            "libcassowary")
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

    def test_and(self, space):
        w_ca, w_z3 = self.execute(
            space,
            """
            quality = -1
            always { quality > 0 && quality < 100 }
            return quality
            """,
            "libcassowary", "libz3")
        assert self.unwrap(space, w_ca) == 1
        assert self.unwrap(space, w_z3) > 0 and self.unwrap(space, w_z3) < 100
        with self.raises(space, "Cassowary::RequiredFailure"):
            space.execute("""
            require "libcassowary"
            qual = -1
            always { qual > 0 && qual < 100 }
            qual = 1000
            return qual
            """)
        with self.raises(space, "RuntimeError"):
            space.execute("""
            require "libz3"
            quali = -1
            always { quali > 0 && quali < 100 }
            quali = 1000
            return quali
            """)

    def test_multiple_constraints_out_of_one(self, space):
        w_ca, w_z3 = self.execute(
            space,
            """
            class Point
              attr_accessor :x, :y

              def initialize(x, y)
                self.x = x
                self.y = y
              end

              def +(pt)
                Point.new(x + pt.x, y + pt.y)
              end

              def ==(pt)
                x == pt.x && y == pt.y
              end
            end

            a = Point.new(1, 1)
            b = Point.new(1, 1)
            c = Point.new(1, 1)
            always { a + b == c }
            return [a.x, a.y], [b.x, b.y], [c.x, c.y]
            """,
            "libcassowary", "libz3")
        ca = self.unwrap(space, w_ca)
        z3 = self.unwrap(space, w_z3)

        assert ca[0][0] + ca[1][0] == ca[2][0]
        assert ca[0][1] + ca[1][1] == ca[2][1]

        assert z3[0][0] + z3[1][0] == z3[2][0]
        assert z3[0][1] + z3[1][1] == z3[2][1]

    def test_readonly(self, space):
        w_ca, w_z3 = self.execute(
            space,
            """
            res = []
            a = 10
            b = 20
            always { a.? == b + 10 }
            res << a << b
            a = 15
            res << a << b
            return res
            """,
            "libcassowary", "libz3")
        assert [10, 0, 15, 5] == self.unwrap(space, w_ca)
        assert [10, 0, 15, 5] == self.unwrap(space, w_z3)

    def test_multiple_constraints_disable(self, space):
        w_ca, w_z3 = self.execute(
            space,
            """
            res = []
            a = 0
            b = 0
            c = always { a == 10 && b == 15 }
            res << a << b
            c.disable
            b = 10
            res << b
            a = 5
            res << a
            return res
            """,
            "libcassowary", "libz3")
        # This results in a RequiredFailure if it doesn't work correctly
        assert [10, 15, 10, 5] == self.unwrap(space, w_ca)
        assert [10, 15, 10, 5] == self.unwrap(space, w_z3)

    def test_changing_strength(self, space):
        w_ca = space.execute("""
            require "libcassowary"
            res = []
            a = 0
            b = 0
            c = always { a == 10 && b == 15 }
            res << a << b
            c.strength = :weak
            b = 10
            res << b
            a = 5
            res << a
            return res
            """)
        # This results in a RequiredFailure if it doesn't work correctly
        assert [10, 15, 10, 5] == self.unwrap(space, w_ca)

    def test_once(self, space):
        w_ca, w_z3 = self.execute(
            space,
            """
            a = 10
            b = 10
            always { b == a * 2 }
            once { a == 100 }
            return a, b, a = 10
            """,
            "libcassowary", "libz3")
        # raises a RequiredFailure if once does not disable the block
        assert self.unwrap(space, w_ca) == [100, 200, 10]
        assert self.unwrap(space, w_z3) == [100, 200, 10]

    def test_during(self, space):
        w_ca, w_z3 = self.execute(
            space,
            """
            $res = []
            a = 10
            b = 200
            always { a >= 100 && b == a * 2 }.during do
              $res << a << b
              a = 200
              $res << a << b
            end
            # now the constraint should have been disabled
            a = 10
            return $res << a << b
            """,
            "libcassowary", "libz3")
        assert self.unwrap(space, w_ca) == [100, 200, 200, 400, 10, 400]
        assert self.unwrap(space, w_z3) == [100, 200, 200, 400, 10, 400]

    # from Cassowary tests test_edit1
    def test_edit_var_stream(self, space):
        w_ca = space.execute("""
        require "libcassowary"
        $res = []
        $top_self = self
        $top_self.singleton_class.send(:attr_reader, :x, :y)

        class Stream
          def initialize(ary)
            @ary = ary
          end

          def next
            ($res << $top_self.x << $top_self.y) if @ary.size > 0
            @ary.pop
          end
        end

        @x = 20
        @y = 30
        always { @x >= 10 }
        always { @x <= 100 }
        always { @x == @y * 2 }

        edit_stream = Stream.new([25, 80, 35])
        edit(edit_stream) { @y }

        $res << @x << @y

        edit_stream = Stream.new([44])
        edit(edit_stream) { @x }

        return $res << @x << @y
        """)
        assert self.unwrap(space, w_ca) == [
            20, 10,
            70, 35,
            100, 50,
            50, 25,
            50, 25, # after edit, variables keep their last values
            44, 22
        ]

    # from Cassowary tests test_edit2
    def test_edit_2var_stream(self, space):
        w_ca = space.execute("""
        require "libcassowary"
        $res = []
        $top_self = self
        $top_self.singleton_class.send(:attr_reader, :x, :y, :z)

        class Stream
          def initialize(ary)
            @ary = ary.reverse
          end

          def next
            ($res << $top_self.x << $top_self.y << $top_self.z) if @ary.size > 0
            @ary.pop
          end
        end

        @x = 20
        @y = 30
        @z = 120
        always { @z == @x * 2 + y }

        edit_stream = Stream.new([
            [10, 5],
            [-10, 15]
        ])
        edit(edit_stream) { [@x, @y] }

        return $res << @x << @y << @z
        """)
        assert self.unwrap(space, w_ca) == [
            45, 30, 120,
            10, 5, 25,
            -10, 15, -5
        ]

    def test_edit_complex_object_stream(self, space):
        w_ca = space.execute("""
        require "libcassowary"
        $res = []

        class Point
          attr_accessor :x, :y
          def initialize(x, y); self.x, self.y = x, y; end
        end

        @top = Point.new 0, 0
        $top = @top

        class Stream
          def initialize(ary)
            @ary = ary
          end

          def next
            ($res << $top.x << $top.y) if @ary.size > 0
            @ary.pop
          end
        end

        always { @top.x >= 10 }
        always { @top.x <= 100 }
        always { @top.x == @top.y * 2 }

        edit_stream = Stream.new([Point.new(10, 10), Point.new(20, 20)])
        edit(stream: edit_stream, accessors: [:x, :y]) { @top }

        $res << @top.x << @top.y
        return $res
        """)
        assert self.unwrap(space, w_ca) == [
            10, 5,
            20, 10,
            10, 5
        ]

    def test_non_solveable_variable_constraint_blocks(self, space):
        w_res = space.execute("""
        $calls = 0
        a = "hello"
        always { $calls += 1; a.is_a?(String) }
        always { $calls += 1; a.is_a?(String) }
        a = "foo"
        return $calls
        """)
        assert self.unwrap(space, w_res) == 4

    def test_class_constraint(self, space):
        space.execute("""
        a = 10
        always { a.kind_of? Fixnum }
        """)

        with self.raises(space, "ArgumentError"):
            space.execute("""
            b = 10
            always { b.kind_of? Fixnum }
            b = "hello"
            """)

        space.execute("""
        c = []
        always { c.respond_to? :insert }
        c = "hello"
        """)

        with self.raises(space, "ArgumentError"):
            space.execute("""
            d = []
            always { d.respond_to? :insert }
            d = 10
            """)

        space.execute("""
        e = []
        always { e.is_a? Enumerable }
        e = {}
        """)

        with self.raises(space, "ArgumentError"):
            space.execute("""
            f = []
            always { f.is_a? Enumerable }
            f = "hello"
            """)

    def test_disable_class_constraint(self, space):
        # This raises if it fails
        space.execute("""
        f = 1
        once { f.is_a? Fixnum }
        f = "hello"
        """)

    def test_abs(self, space):
        w_res = space.execute("""
        require "libz3"
        x = 10
        always { x.abs >= 100 }
        x = -100
        return x
        """)
        assert self.unwrap(space, w_res) == -100

    def test_identity1(self, space):
        w_res = space.execute("""
        a = Object.new
        b = Object.new
        always { a is? b }
        return a.object_id == b.object_id, (a is? b)
        """)
        assert self.unwrap(space, w_res) == [True, True]

    def test_identity2(self, space):
        w_res = space.execute("""
        a = Object.new
        b = Object.new
        c = always { a is? b }
        $res = [a.object_id == b.object_id]
        a = x = Object.new
        $res << [a.object_id == b.object_id, a.object_id == x.object_id]
        b = x = Object.new
        $res << [a.object_id == b.object_id, b.object_id == x.object_id]
        c.disable
        a = x = Object.new
        $res << [a.object_id != b.object_id, a.object_id == x.object_id]
        return $res
        """)
        assert self.unwrap(space, w_res) == [
            True,
            [True, True],
            [True, True],
            [True, True]
        ]

    @py.test.mark.xfail # this will work once interacting solvers eager assignment is enabled
    def test_identity3(self, space):
        w_res = space.execute("""
        require "libcassowary"
        a = 0
        b = 5
        always { a is? b }
        $res = [a, b]
        always { a >= 11 }
        $res << a << b
        always { b >= 15 }
        return $res << a << b
        """)
        assert self.unwrap(space, w_res) == [0, 0, 11, 11, 15, 15]

    def test_identity4(self, space):
        # cannot constrain identity of dynamically built objects
        with self.raises(space, "ArgumentError"):
            space.execute("""
            Pt = Struct.new("Pt", :x, :y)
            @x = @y = 0
            def top
              return Pt.new(@x, @y)
            end

            b = Pt.new(10, 10)
            always { top is? b }
            """)
        with self.raises(space, "ArgumentError"):
            space.execute("""
            @x = @y = 10
            def top
              return @x + @y
            end

            b = 20
            always { top is? b }
            """)

    def test_identity_recalc(self, space):
        w_res = space.execute("""
        Cell = Struct.new("Cell", :v, :n)
        second = Cell.new(1, nil)
        list = Cell.new(0, second)
        $res = [(list.n is? second)]
        always { list.n is? second }
        $res << (list.n is? second)
        list = Cell.new(1, nil)
        $res << (list.n is? second)
        return $res
        """)
        assert self.unwrap(space, w_res) == [True, True, True]

    def test_invalid_multiple_assignment(self, space):
        with self.raises(space, "RuntimeError", "multiply assigned variable in constraint execution"):
            space.execute("""
            require "libcassowary"
            @sum = -1
            def foo
              @sum = 0
              @sum = 1
            end
            always { foo == 1 }
            """)

    @py.test.mark.xfail
    def test_lazy_solver_selection(self, space):
        w_z3, w_cassowary = self.execute(
            space,
            """
            def foo(a = nil)
              x = nil
              if a
                always { x == a.? }
              else
                x = 100
              end
              return x
            end
            return foo, foo(10)
            """,
            "libz3", "libcassowary"
        )
        assert self.unwrap(space, w_z3) == [100, 10]
        assert self.unwrap(space, w_cassowary) == [100, 10]

    @py.test.mark.xfail
    def test_late_type_assignment(self, space):
        w_z3, w_cassowary = self.execute(
            space,
            """
            x = nil
            always { x.respond_to? :nil? }
            x = 10
            always { x + 10 == 100 }
            return x
            """,
            "libz3", "libcassowary")
        assert self.unwrap(space, w_z3) == 90
        assert self.unwrap(space, w_cassowary) == 90

    def test_atomic_assignment(self, space):
        res_w = self.execute(space,
        """
        x = 100
        y = 100
        z = 100
        always { x + y + z == 300 }
        x, y, z = 10, 90, 200
        return x, y, z
        """,
        "libz3", "libcassowary")
        w_z3, w_cassowary = [self.unwrap(space, w_res) for w_res in res_w]
        assert w_cassowary == [10, 90, 200]
        assert w_cassowary == w_z3

    def test_atomic_assignment2(self, space):
        res_w = self.execute(space,
        """
        x, y, z = 10, 90, 200
        always { x + y + z == 300 }
        $res = [[x, y, z]]
        x, y, z = z, y, x
        $res << [x, y, z]
        return $res
        """,
        "libcassowary", "libz3")
        w_cassowary, w_z3 = [self.unwrap(space, w_res) for w_res in res_w]
        assert w_cassowary[0][0] == w_cassowary[1][2]
        assert w_cassowary[0][1] == w_cassowary[1][1]
        assert w_cassowary[0][2] == w_cassowary[1][0]
        assert w_z3[0][0] == w_z3[1][2]
        assert w_z3[0][1] == w_z3[1][1]
        assert w_z3[0][2] == w_z3[1][0]

    def test_atomic_assignment3(self, space):
        cassowary = self.unwrap(space, space.execute(
        """
        require "libcassowary"
        class Point
          attr_accessor :x, :y
          def initialize(a, b)
            @x = a
            @y = b
          end
        end

        x = Point.new(10, 10)
        y = Point.new(90, 90)
        z = Point.new(200, 200)
        always { x.x + y.x + z.x == 300 }
        $res = [[x.x, y.x, z.x]]
        x, y, z = z, y, x
        $res << [x.x, y.x, z.x]
        return $res
        """))
        assert cassowary[0][0] == cassowary[1][2]
        assert cassowary[0][1] == cassowary[1][1]
        assert cassowary[0][2] == cassowary[1][0]

    def test_no_solver(self, space):
        w_c, w_z3 = self.execute(
            space,
            """
            a = b = 0
            x = nil
            always { a + b == 10 }
            always(solver: nil) do
              x = a.to_s
              true # so the system knows we want the side effect
            end
            a = 100
            return x
            """,
            "libcassowary", "libz3"
        )
        assert self.unwrap(space, w_c) == "100.0"
        assert self.unwrap(space, w_z3) == "100"
