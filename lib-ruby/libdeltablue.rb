$LOAD_PATH.unshift(File.expand_path("../deltablue/lib/", __FILE__))
require "deltared"

# XXX: Ugh, no namespace
class DeltaRed::Variable
  def <(block)
    # TODO: check that we're in `always'
    # TODO: strength and stuff
    constraint = ::Constraint.new(&block)
    k_sources = constraint.constraint_variables
    mapping = {k_sources => self}
    DeltaRed::Formula.new(mapping, block)
  end

  def method_missing(name, *args, &block)
    # XXX: Hack: never send, just check that it could work?
    super unless value.respond_to?(name)
  end

  def suggest_value(val)
    # TODO: check predicate first
    self.value = val
  end
end

class DeltaRed::Formula
  def initialize(mapping, block)
    @mapping, @block = mapping, block
  end

  def add_to_constraint(c)
    c.formula(@mapping) {|*a| @block.call }
  end
end

class DeltaRed::Solver < ConstraintObject
  def add_constraint(block, strength, weight, error, methods)
    formulas = __constrain__(&methods)
    DeltaRed.constraint! do |c|
      formulas.each do |formula|
        formula.add_to_constraint(c)
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
      weight = strength_or_hash[:weight]
      error = strength_or_hash[:error]
      methods = strength_or_hash[:methods]
      DeltaRed::Solver::Instance.add_constraint(block, strength, weight, error, methods)
    else
      if strength_or_hash.nil?
        prim_always(&block)
      elsif !strength_or_hash.is_a?(Hash)
        prim_always(strength_or_hash, &block)
      end
    end
  end
end
