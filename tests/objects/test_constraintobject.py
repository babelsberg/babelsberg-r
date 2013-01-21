from ..base import BaseTopazTest


class TestConstraintVariableObject(BaseTopazTest):
    def test_names(self, space):
        space.execute("ConstraintVariable")
        space.execute("Constraints")

    def test_local(self, space):
        w_res = space.execute("""
        require "libcassowary"
        a = 1
        constrain { a == 10 }
        return a
        """)
        assert self.unwrap(space, w_res) == 10
        w_res = space.execute("""
        a = 1
        constrain { a >= 10 }
        a = 11
        return a
        """)
        assert self.unwrap(space, w_res) == 11

    def test_ivar(self, space):
        w_res = space.execute("""
        require "libcassowary"
        @a = 1
        constrain { @a == 10 }
        return @a
        """)
        assert self.unwrap(space, w_res) == 10
        w_res = space.execute("""
        @a = 1
        constrain { @a >= 10 }
        @a = 11
        return @a
        """)
        assert self.unwrap(space, w_res) == 11

    def test_cvar(self, space):
        w_res = space.execute("""
        require "libcassowary"
        @@a = 1
        constrain { @@a == 10 }
        return @@a
        """)
        assert self.unwrap(space, w_res) == 10
        w_res = space.execute("""
        @@a = 1
        constrain { @@a >= 10 }
        @@a = 11
        return @@a
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
            constrain { @x >= 0 }
            constrain { @y >= 0 }
            constrain { @x < 640 }
            constrain { @y < 480 }
          end
        end
        
        pt1 = Point.new(-1, 10)
        pt2 = Point.new(20, 20)
        res << [[pt1.x, pt1.y], [pt2.x, pt2.y]]
        constrain { pt1.x == pt2.x }
        res << [[pt1.x, pt1.y], [pt2.x, pt2.y]]
        constrain { pt1.x == 5 }
        res << [[pt1.x, pt1.y], [pt2.x, pt2.y]]
        """)
        assert self.unwrap(space, w_res) == [
            [[0, 10], [20, 20]],
            [[0, 10], [0, 20]],
            [[5, 10], [5, 10]]
        ] or self.unwrap(space, w_res) == [
            [[0, 10], [20, 20]],
            [[20, 10], [20, 20]],
            [[5, 10], [5, 10]]
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
            constrain { @x >= 0 }
            constrain { @y >= 0 }
            constrain { @x < 640 }
            constrain { @y < 480 }
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
            constrain { pt1.y == pt2.y }
          end
        
          def length
            @end.x - @start.x
          end
        end
        
        h = HorizontalLine.new(Point.new(1, 1), Point.new(2, 2))
        constrain { h.length >= 100 }
        return h.length
        """)
        assert self.unwrap(space, w_res) == 100
