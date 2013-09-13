$LOAD_PATH.unshift(File.expand_path("../deltablue/lib/", __FILE__))
require "deltared"

# XXX: Ugh, no namespace
class DeltaRed::Variable < ConstraintObject
  def predicates
    @predicates ||= []
  end

  def add_predicate(pred)
    predicates << pred if pred
  end

  def <(block)
    # TODO: check that we're in `always'
    # TODO: strength and stuff
    constraint = ::Constraint.new(&block)
    k_sources = constraint.constraint_variables
    mapping = {k_sources => self}
    DeltaRed::Formula.new(mapping, block)
  end

  def method_missing(name, *args, &block)
    # XXX: Is this really necessary?
    super unless value.respond_to?(name)
    self
  end

  def begin_assign(v)
    @proposed_value = v
  end

  def assign
    prev = @value
    @value = @proposed_value
    unless predicates.all?(&:call)
      # assign previous value and let deltablue handle the constraints
      @value = prev
      self.value = @proposed_value
    end
  end

  def end_assign
    @proposed_value = nil
  end
end

class DeltaRed::Formula < ConstraintObject
  def initialize(mapping, block)
    @mapping, @block = mapping, block
  end

  def add_to_constraint(c)
    c.formula(@mapping) {|*a| @block.call }
  end

  def add_predicate(proc)
    variables.each do |var|
      var.add_predicate(proc)
    end
  end

  def variables
    (@mapping.keys + @mapping.values).flatten.uniq
  end
end

class DeltaRed::Solver < ConstraintObject
  def add_constraint(predicate, strength, methods)
    formulas = Constraint.new(&methods).value

    strength ||= :required
    strength = case strength
               when :weak then DeltaRed::WEAK
               when :medium then DeltaRed::MEDIUM
               when :strong then DeltaRed::STRONG
               when :required then DeltaRed::REQUIRED
               else raise ArgumentError, "unsupported strength #{strength}"
               end

    DeltaRed.constraint!(strength: strength) do |c|
      formulas.each do |formula|
        formula.add_to_constraint(c)
        formula.add_predicate(predicate)
      end
    end
  end

  Instance = self.new

  def constraint_variable_for(obj)
    DeltaRed.variables(obj)
  end

  def weight
    10
  end
end

# Enable DeltaBlue
class Object
  def constraint_solver
    DeltaRed::Solver::Instance
  end
end

# Patch always
class Object
  alias prim_always always

  def always(strength_or_hash = nil, &block)
    if strength_or_hash.is_a?(Hash) &&
        (strength_or_hash[:predicate] || strength_or_hash[:methods])
      predicate = strength_or_hash[:predicate]
      strength = strength_or_hash[:priority] || strength_or_hash[:strength]
      methods = strength_or_hash[:methods]
      if block and methods.nil? # we can leave the predicate off, if we want
        methods = block
      elsif block and predicate.nil?
        predicate = block
      end
      solver = strength_or_hash[:solver] || DeltaRed::Solver::Instance
      solver.add_constraint(predicate, strength, methods)
    else
      if strength_or_hash.nil?
        prim_always(&block)
      else
        prim_always(strength_or_hash, &block)
      end
    end
  end
end
