class FloatRwIO
  def initialize(*args, &block)
    @file = File.new(*args, &block)
    @ticker = Fiber.new do
      loop do
        refresh
        Fiber.yield
      end
    end
  end

  def content
    @file.rewind
    @file.read.to_f
  end

  def content=(float)
    @file.truncate(0)
    @file.write(float.to_s)
  end

  def refresh
    val = get_value
    @constraint_variable.suggest_value(val)
    if @constraint_variable.value != val
      self.content = @constraint_variable.value
    end
  end

  def for_constraint(name)
    @constraint_variable = content.for_constraint(name)
  end
end

puts "IO constraint solver loaded."
