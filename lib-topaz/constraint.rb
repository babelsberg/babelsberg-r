class Constraint < ConstraintObject
  def during(&block)
    res = yield
    disable
    res
  end
end
