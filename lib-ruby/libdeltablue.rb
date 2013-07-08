$LOAD_PATH.unshift(File.expand_path("../deltablue/lib/", __FILE__))
require "deltared"

# XXX: Ugh, no namespace
class DeltaRed::Variable < ConstraintObject
  def predicates
    @predicates ||= []
  end

  def add_predicate(pred)
    predicates << pred
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
    super unless value.respond_to? name
  end

  def suggest_value(val)
    prev = @value
    @value = val
    unless predicates.all?(&:call)
      # assign previous value and let deltablue handle the constraints
      @value = prev
      self.value = val
    end
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
    formulas = __constrain__(&methods)

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
end

# Enable DeltaBlue
class Object
  def for_constraint(name)
    DeltaRed.variables(self)
  end
end

# Patch always
class Object
  alias prim_always always

  def always(strength_or_hash = nil, &block)
    if strength_or_hash.is_a?(Hash)
      block ||= strength_or_hash[:predicate]
      strength = strength_or_hash[:priority] || strength_or_hash[:strength]
      methods = strength_or_hash[:methods]
      DeltaRed::Solver::Instance.add_constraint(block, strength, methods)
    else
      if strength_or_hash.nil?
        prim_always(&block)
      elsif !strength_or_hash.is_a?(Hash)
        prim_always(strength_or_hash, &block)
      end
    end
  end
end
