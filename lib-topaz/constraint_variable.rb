class ConstraintVariable < ConstraintObject
  def suggest_value(val)
    variable.suggest_value(val)
  end

  def ==(other)
    self.method_missing(:"==", other)
  end
end
