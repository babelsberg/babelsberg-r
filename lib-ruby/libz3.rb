Z3::Instance = Z3.new

class Z3::Z3Pointer
  def begin_assign(v)
    @proposed_value_constraint = self == v
    Z3::Instance.add_constraint(@proposed_value_constraint)
  end

  def assign
    Z3::Instance.solve
  end

  def end_assign
    Z3::Instance.remove_constraint(@proposed_value_constraint)
    @proposed_value_constraint = nil
  end

  alias plain_enable enable

  def enable(preference=nil)
    plain_enable
    Z3::Instance.solve
  end

  def readonly!
    unless @ro_constraint
      @ro_constraint = self == value
      Z3::Instance.add_constraint(@ro_constraint)
    end
  end

  def writable!
    if @ro_constraint
      Z3::Instance.remove_constraint(@ro_constraint)
      @ro_constraint = nil
    end
  end
end

class Numeric
  alias coerce_wo_z3 coerce
  def coerce(other)
    if other.kind_of?(Z3::Z3Pointer)
      [other, Z3::Instance.make_real(self)]
    else
      coerce_wo_z3(other)
    end
  end
end

class Float
  alias coerce_wo_z3 coerce
  def coerce(other)
    if other.kind_of?(Z3::Z3Pointer)
      [other, Z3::Instance.make_real(self)]
    else
      coerce_wo_z3(other)
    end
  end
end

class Fixnum
  alias coerce_wo_z3 coerce
  def coerce(other)
    if other.kind_of?(Z3::Z3Pointer)
      [other, Z3::Instance.make_int(self)]
    else
      coerce_wo_z3(other)
    end
  end
end

class Z3
  def weight
    100
  end

  def constraint_variable_for(value)
    case value
    when Fixnum
      return Z3::Instance.make_int_variable(value)
    when TrueClass, FalseClass
      Z3::Instance.make_bool_variable(value)
    when Numeric
      return Z3::Instance.make_real_variable(value.to_f)
    end
  end
end

class Numeric
  def constraint_solver
    Z3::Instance
  end
end

class TrueClass
  def constraint_solver
    Z3::Instance
  end
end

class FalseClass
  def constraint_solver
    Z3::Instance
  end
end

class Array
  def alldifferent?
    return true if self.empty?
    asts = []
    each do |element|
      asts << case element
      when Fixnum
        Z3::Instance.make_int_variable(element)
      when Float
        Z3::Instance.make_real_variable(element)
      when true, false
        Z3::Instance.make_bool_variable(element)
      when Z3::Z3Pointer
        element
      else
        raise "Cannot solve alldifferent? on this array (no Z3 interpretation for #{element.inspect})"
      end
    end

    begin
      return asts.pop.alldifferent(*asts)
    rescue RuntimeError
      # we're not constructing constraints
      return self.uniq.size == self.size
    end
  end
end

puts "Z3 constraint solver loaded."
