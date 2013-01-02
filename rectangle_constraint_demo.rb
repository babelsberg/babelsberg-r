class Point
  class ::Numeric
    def x(other)
      Point.new(self, other)
    end
  end

  attr_reader :x, :y

  def initialize(x, y)
    @x = x
    @y = y
  end

  def -(other)
    raise TypeError, "expected Point" unless other.class == self.class
    (self.x - other.x).x (self.y - other.y)
  end

  def to_s
    "#{x}x#{y}"
  end
end

class Rectangle
  attr_reader :area, :origin, :extent

  def initialize(hash)
    @origin = hash[:origin] or raise "missing key: origin"
    @extent = hash[:extent] or raise "missing key: extent"

    constrain: @area == @extent[0] * @extent[1]
  end

  def to_s
    "#{origin}->#{extent - origin} (area: #{area})"
  end
end

r = Rectangle.new origin: 0.x(0), extent: 10.x(10)
puts "origin: #{r.origin}, extent: #{r.extent}, area: #{r.area}"
constrain: r.area == 10
puts "origin: #{r.origin}, extent: #{r.extent}, area: #{r.area}"
