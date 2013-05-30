require "libcassowary"

class Mercury
  def initialize
    @top = 10
    @bottom = 0
  end

  def top=(num)
    @top = num
  end

  def top
    @top
  end

  def bottom
    @bottom
  end

  def height
    @top - @bottom
  end

  def inspect
    "<Mercury: #{@top}->#{@bottom}>"
  end
end

class Mouse
  def initialize
    @location_y = 10
  end

  def location_y
    @location_y
  end

  def location_y=(arg)
    @location_y = arg
  end

  def inspect
    "<Mouse: #{@location_y}>"
  end
end

class Rectangle
  def initialize(name, top, bottom)
    @name = name
    @top = top
    @bottom = bottom
  end

  def top
    @top
  end

  def top=(arg)
    @top = arg
  end

  def bottom
    @bottom
  end

  def bottom=(arg)
    @bottom = arg
  end

  def inspect
    "<#{@name} Rectangle: #{@top}->#{@bottom}>"
  end
end

class Thermometer < Rectangle
  def initialize(top, bottom)
    super("thermometer", top, bottom)
  end

  def inspect
    "<Thermometer: #{@top}->#{@bottom}>"
  end
end

class Display
  def initialize
    @number = 0
  end

  def number
    @number
  end

  def number=(arg)
    @number = arg
  end

  def inspect
    "<Display: #{@number}>"
  end
end

mouse = Mouse.new
mercury = Mercury.new
thermometer = Thermometer.new(200, 0)
grey = Rectangle.new("grey", mercury.top, mercury.bottom)
white = Rectangle.new("white", thermometer.top, mercury.top)
temperature = mercury.height
display = Display.new

always { temperature == mercury.height }
always { white.top == thermometer.top }
always { white.bottom == mercury.top }
always { grey.top == mercury.top }
always { grey.bottom == mercury.bottom }
always { display.number == temperature }
always(:strong) { mercury.top == mouse.location_y }
always { mercury.top <= thermometer.top }
always { mercury.bottom == thermometer.bottom }
always { thermometer.bottom == 0 }
always { thermometer.top == 200 }
start = Time.now
iterations = 1
(0...iterations).each do |i|
  mouse.location_y = i
end
puts [mouse, mercury, thermometer, grey, white, temperature, display].map { |e| e.inspect }
