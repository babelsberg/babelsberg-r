$LOAD_PATH.unshift(File.expand_path("../deltablue/lib/", __FILE__))
require "deltared"

class DeltaRed::Variable < ConstraintObject
  def <(block)
    # XXX
    # TODO: check that we're in `always'
    # TODO: strength and stuff
    constraint = ::Constraint.new(&block)
    k_sources = constraint.constraint_variables
    @path, @block = {k_sources => self}, block
    self
  end

  def __builder__
    if Thread.current[:builder].nil? || Thread.current[:builder].built?
      Thread.current[:builder] = DeltaRed::Builder.new(DeltaRed::Constraint::DEFAULT_OPTIONS)
    end
    Thread.current[:builder]
  end

  def enable
    @constraint ||= __build
    @constraint.enable
  end

  def disable
    @constraint.disable
  end

  def __build
    r = DeltaRed.constraint do |c|
      c.formula(@path) do |*a|
        @block.call
      end
      if @others
        @others.each do |other|
          other.__build_on(c)
        end
      end
    end
  end

  def __build_on(builder)
    builder.formula(@path) do |*a|
      @block.call
    end
  end

  def method_missing(name, *args)
    super unless value.respond_to? name
  end

  def suggest_value(val)
    self.value = val
  end
end

# Enable DeltaBlue
class Object
  def for_constraint(name)
    DeltaRed.variables(self)
  end
end
