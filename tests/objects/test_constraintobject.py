from ..base import BaseTopazTest


class TestConstraintVariableObject(BaseTopazTest):
    def test_names(self, space):
        space.execute("ConstraintVariable")
        space.execute("Constraints")

    def test_local(self, space):
        w_res = space.execute("""
        require "libcassowary"
        a = 1
        always{ a == 10 }
        return a
        """)
        assert self.unwrap(space, w_res) == 10
        w_res = space.execute("""
        b = 1
        always { b > 10 }
        b = 11
        return b
        """)
        assert self.unwrap(space, w_res) == 11

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
