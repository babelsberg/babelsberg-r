class ConstraintVariable < ConstraintObject
  def suggest_value(val)
    variable.suggest_value(val)
  end

  def ==(other)
    variable == (other.kind_of?(self.class) ? other.variable : other)
  end

  def method_missing(method, *args, &block)
    if variable.respond_to? method
      args = args.map do |arg|
        arg.kind_of?(self.class) ? arg.variable : arg
      end
      variable.send(method, *args, &block)
    else
      value.send(method, *args, &block)
    end
  end
end
