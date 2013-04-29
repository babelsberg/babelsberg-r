class IOSolver
  class Variable < BasicObject
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

    def enable
      TickingSolver.enable(self)
    end

    def disable
      TickingSolver.disable(self)
    end

    def method_missing(method, *args, &block)
      Ast.new(self, method, *args, &block)
    end
  end

  class Ast < Variable
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
      # XXX: Should always delegate, but useless until we have String solver otherwise
      # unless result.is_a?(IO)
      if result.ancestors.any? { |mod| Constraints.variable_handlers[mod] }
        constraint = always { result.send(@method, *@args, &@block) }
        constraint.disable
      else
        @ast.send(@method, *@args, &@block)
      end
    end
  end

  class TickingSolver
    def self.new
      @instance ||= begin
        TickingSolver.allocate
        @instance.initialize
      end
    end

    def initialize
      @asts = []
      @ticker = Fiber.new do
        @asts.each(&:refresh)
        Fiber.yield
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

Constraints.for_variables_of_type IO do |name, value|
  IOSolver::Variable.new(name, value)
end
Constraints.register_solver IOSolver::TickingSolver.instance

puts "IO constraint solver loaded."
