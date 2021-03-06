$LOAD_PATH.unshift(File.expand_path("../cassowary/lib/", __FILE__))
require "cassowary"

class Cassowary::SimplexSolver
  def weight
    200
  end

  def constraint_variable_for(value)
    case value
    when Numeric, nil
      v = Cassowary::Variable.new(value: value || 0)
      v.solver = self
      Cassowary::SimplexSolver.instance.add_stay(v)
      v
    end
  end
end

class Cassowary::Variable
  attr_accessor :solver

  def readonly!
    unless @ro_constraint
      @ro_constraint = self == value
      Cassowary::SimplexSolver.instance.add_constraint(@ro_constraint)
    end
  end

  def writable!
    if @ro_constraint
      Cassowary::SimplexSolver.instance.remove_constraint(@ro_constraint)
      @ro_constraint = nil
    end
  end
end

class Numeric
  alias coerce_wo_cassowary coerce
  def coerce(other)
    if other.kind_of?(Cassowary::AbstractVariable) || other.kind_of?(Cassowary::Constraint)
      [other, self.as_linear_expression]
    else
      coerce_wo_cassowary(other)
    end
  end
end

class Float
  alias coerce_wo_cassowary coerce
  def coerce(other)
    if other.kind_of?(Cassowary::AbstractVariable) || other.kind_of?(Cassowary::Constraint)
      [other, self.as_linear_expression]
    else
      coerce_wo_cassowary(other)
    end
  end
end

class Fixnum
  alias coerce_wo_cassowary coerce
  def coerce(other)
    if other.kind_of?(Cassowary::AbstractVariable) || other.kind_of?(Cassowary::Constraint)
      [other, self.as_linear_expression]
    else
      coerce_wo_cassowary(other)
    end
  end
end

class Numeric
  def constraint_solver
    Cassowary::SimplexSolver.instance
  end
end

class Object
  def __parse_edit_constraint_arguments(stream, opts, block)
    # TODO: make this work if we mix complex objects and float
    # variables in block
    if stream.is_a? Hash
      raise ArgumentError, "wrong number of arguments (2 for 1..2)" if opts
      opts = stream
      stream = opts[:stream]
    end
    unless stream.respond_to? :next
      raise ArgumentError, "#{stream} does not respond to `next'"
    end

    opts ||= {}
    strength = opts[:strength] || opts[:priority] || :strong
    strength = Cassowary.symbolic_strength(strength)

    unless block
      raise(ArgumentError, "No variable binding given")
    end

    accessors = opts[:accessors]

    return stream, strength, accessors, block
  end

  def __create_edit_vars_from_accessors(accessors, constraints, block)
    complex_vars = [*block.call]
    store_class = Class.new
    store_class.send(:attr_accessor, *accessors)
    complex_vars.collect do |var|
      # Create an object that has instance variables corresponding
      # to the accessors. Assert equality constraints between those
      # instance variables and the result of the complex objects'
      # accessor functions. We use the instance variables in
      # Cassowary, but due to the equalities, the complex objects
      # will be updated as needed
      store = store_class.new
      accessors.collect do |sym|
        store.send(:"#{sym}=", var.send(sym))
        constraints << always { store.send(sym) == var.send(sym) }
        Constraint.new(solver: Cassowary::SimplexSolver.instance) { store.send(sym) }.constraint_variables
      end
    end.flatten
  end

  def __check_edit_vars(vars)
    vars.each do |o|
      unless o.is_a? Cassowary::Variable
        raise ArgumentError, "Block did not return a Cassowary::Variable or array of Cassowary::Variables, cannot create edit constraint"
      end
    end
  end

  def __do_edit(stream, strength, vars, accessors)
    Cassowary::SimplexSolver.instance.tap do |solver|
      vars.each do |var|
        solver.add_edit_var var, strength
      end
      solver.solve
      solver.begin_edit
      next_vals = stream.next

      while next_vals
        if accessors
          next_vals = [*next_vals].collect do |val|
            accessors.collect do |sym|
              val.send(sym)
            end
          end.flatten
        end

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

  def edit(stream, opts = nil, &block)
    stream, strength, accessors, block = __parse_edit_constraint_arguments(stream, opts, block)
    temp_constraints = nil

    if accessors
      temp_constraints = []
      vars = __create_edit_vars_from_accessors(accessors, temp_constraints, block)
    else
      vars = Constraint.new(solver: Cassowary::SimplexSolver.instance, &block).constraint_variables
    end

    __check_edit_vars(vars)
    __do_edit(stream, strength, vars, accessors)

    temp_constraints.each(&:disable) if temp_constraints
    nil
  end
end

puts "Cassowary constraint solver loaded."
