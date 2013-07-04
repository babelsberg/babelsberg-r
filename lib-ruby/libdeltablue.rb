$LOAD_PATH.unshift(File.expand_path("../deltablue/lib/", __FILE__))
require "deltared"

# XXX: Ugh, no namespace
class DeltaRed::Variable
  def method_missing(name, *args, &block)
    # XXX: Hack: never send, just check that it could work
    super unless value.respond_to?(name)
  end

  def suggest_value(val)
    self.value = val
  end
end

class DeltaRedSolver < ConstraintObject
  def constraint(block, strength, weight, error, methods)
    methods_hash = __constrain__(&methods)
    DeltaRed.constraint! do |c|
      methods_hash.keys.each do |k|
        block_k = methods_hash[k]
        constraint = Constraint.new(&block_k)
        k_sources = constraint.constraint_variables
        p k_sources
        c.formula({k_sources => k}) {|*a| block_k.call }
      end
    end
  end
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

      DeltaRedSolver.new.constraint(block, strength, weight, error, methods)
    else
      if strength_or_hash.nil?
        prim_always(&block)
      elsif !strength_or_hash.is_a?(Hash)
        prim_always(strength_or_hash, &block)
      end
    end
  end
end
