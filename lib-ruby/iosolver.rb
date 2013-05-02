class IOSolver
  class Variable < ConstraintObject
    def initialize(name, value)
      @name = name
      @value = value
    end

    def suggest_value(v)
      @value = v
    end

    def refresh
      @value.rewind if @value.respond_to?(:rewind)
      @value
    end

    def enable(strength = nil)
      raise NotImplementedError
      raise "cannot enable constraint twice" if @enabled
      @enabled = true
      @strength = strength
      TickingSolver.instance.enable(self)
    end

    def disable
      @enabled = false
      TickingSolver.instance.disable(self)
    end

    def respond_to?(sym, include_private=false)
      super || @value.respond_to?(sym, include_private)
    end

    def method_missing(method, *args, &block)
      Ast.new(self, method, *args, &block)
    end
  end

  class Ast < Variable
    attr_reader :ast

    def initialize(ast, method, *args, &block)
      @ast = ast
      @method = method
      @args = args
      @block = block
    end

    def suggest_value(v)
      @ast.suggest_value(v)
    end

    def refresh
      result = @ast.refresh
      return result.send(@method, *@args, &@block) unless @enabled # not top-level

      # TODO: try read-only first, fallback to writing into file
      # constraint = always { result.send(@method, *@args, &@block) }
      # constraint = always { @args[0] <= c(result) }
      # constraint.disable
      c = result.send(@method, *@args, &@block)
      p result, @args
      p c
      p "refreshed"
      result
    end

    def inspect
      "#{super[0..-2]}:#{@method.inspect}(#{@args.inspect})>"
    end
  end

  class TickingSolver
    class << self
      alias superclass_new new
    end

    def self.new
      raise "#{name} should have only one instance" if @instance
      @instance = superclass_new
    end

    def self.instance
      @instance ||= new
    end

    def initialize
      @asts = []
      @ticker = Fiber.new do
        loop do
          @asts.each(&:refresh)
          Fiber.yield
        end
      end
    end

    def solve
      @ticker.resume
    end

    def enable(ast)
      @asts << ast
    end

    def disable(ast)
      @asts.delete(ast)
    end
  end
end

class IO
  def self.for_constraint(name, value)
    IOSolver::Variable.new(name, value)
  end
end

puts "IO constraint solver loaded."
