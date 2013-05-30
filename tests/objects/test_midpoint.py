import py

from ..base import BaseTopazTest

E = 0.00000000000001

class TestConstraintVariableObject(BaseTopazTest):
    def execute(self, space, code, *libs):
        return [space.execute("""
                require "%s"

                %s
                """ % (lib, code)) for lib in libs]

    def test_midpoint(self, space):
        w_res = space.execute("""
        require "libcassowary"
        res = []
        class Point
          def x; @x; end
          def y; @y; end

          def + q
            Point.new(x+q.x,y+q.y)
          end

          def * n
            Point.new(x*n, y*n)
          end

          def / n
            Point.new(x/n, y/n)
          end

          def == o
            o.x == self.x && o.y == self.y
          end

          def initialize(x, y)
            @x = x
            @y = y
          end
        end

        class MidpointLine
          attr_reader :end1, :end2, :midpoint

          def initialize(pt1, pt2)
            @end1 = pt1
            @end2 = pt2
            @midpoint = Point.new(0,0)
            always { (end1 + end2) == (midpoint*2) }
          end

          def length
            @end2.x - @end1.x
          end
        end

        p1 = Point.new(0,10)
        p2 = Point.new(20,30)
        m = MidpointLine.new(p1,p2)
        # first test point * and /, then the midpoint line
        return [(p1*2).x, (p1*2).y, (p2/10).x, (p2/10).y, m.midpoint.x, m.midpoint.y ]
        """)
        assert self.unwrap(space, w_res) == [0,20,2,3,10,20]
