$LOAD_PATH.unshift(File.expand_path("../cassowary/lib/", __FILE__))
require "cassowary"

class Numeric
  alias prev_coerce coerce
  def coerce(other)
    if other.kind_of?(Cassowary::AbstractVariable) || other.kind_of?(Cassowary::Constraint)
      [other, self.as_linear_expression]
    else
      prev_coerce(other)
    end
  end
end

class Float
  alias prev_coerce coerce
  def coerce(other)
    if other.kind_of?(Cassowary::AbstractVariable) || other.kind_of?(Cassowary::Constraint)
      [other, self.as_linear_expression]
    else
      prev_coerce(other)
    end
  end
end

class Fixnum
  alias prev_coerce coerce
  def coerce(other)
    if other.kind_of?(Cassowary::AbstractVariable) || other.kind_of?(Cassowary::Constraint)
      [other, self.as_linear_expression]
    else
      prev_coerce(other)
    end
  end
end

class Numeric
  def for_constraint(name)
    v = Cassowary::Variable.new(name: name, value: self)
    Cassowary::SimplexSolver.instance.add_stay(v)
    v
  end
end

class Object
  def edit(stream, strength = Cassowary::Strength::StrongStrength, &block)
    unless stream.respond_to? :next
      raise ArgumentError, "#{stream} does not respond to `next'"
    end
    unless block
      raise(ArgumentError, "No variable binding given")
    end
    vars = Constraint.new(&block).constraint_variables
    unless vars.all? { |o| o.is_a? Cassowary::Variable }
      raise ArgumentError, "Block did not return a Cassowary::Variable or array of Cassowary::Variables, cannot create edit constraint"
    end
    Cassowary::SimplexSolver.instance.tap do |solver|
      vars.each do |var|
        solver.add_edit_var var, strength
      end
      solver.solve
      solver.begin_edit
      next_vals = stream.next
      while next_vals
        solver.resolve [*next_vals]
        begin
          next_vals = stream.next
        rescue StopIteration
          break
        end
      end
      solver.end_edit
    end
  end
end

puts "Cassowary constraint solver loaded."
