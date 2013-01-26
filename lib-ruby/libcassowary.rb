require "set"

module Cassowary
  VERSION = "0.5.0"

  class Error < StandardError; end
  class InternalError < Error; end
  class NonLinearResult < Error; end
  class NotEnoughStays < Error; end
  class RequiredFailure < Error; end
  class TooDifficult < Error; end
end

module Cassowary
  module Equalities
    def ==(expr, strength = Strength::RequiredStrength, weight = 1.0)
      cn_equality(LinearEquation, self - expr, strength, weight)
    end

    def >=(expr, strength = Strength::RequiredStrength, weight = 1.0)
      cn_equality(LinearInequality, self - expr, strength, weight)
    end

    def >(expr, strength = Strength::RequiredStrength, weight = 1.0)
      cn_equality(LinearInequality, self - (expr + 1), strength, weight)
    end

    def <=(expr, strength = Strength::RequiredStrength, weight = 1.0)
      expr = expr.as_linear_expression if expr.is_a?(Numeric)
      cn_equality(LinearInequality, expr - self, strength, weight)
    end

    def <(expr, strength = Strength::RequiredStrength, weight = 1.0)
      expr = expr.is_a?(Numeric) ? (expr - 1).as_linear_expression : (expr - 1)
      cn_equality(LinearInequality, expr - self, strength, weight)
    end

    private
    def cn_equality(klass, expr, strength, weight)
      cn = klass.new
      cn.expression = expr
      cn.strength = strength
      cn.weight = weight
      cn
    end
  end
end

module Cassowary
  class AbstractVariable < ConstraintObject
    attr_accessor :name

    def initialize(hash = {})
      self.name = hash[:name]
    end

    def dummy?
      false
    end

    def external?
      raise NotImplementedError, "my subclass should have implemented #external?"
    end

    def pivotable?
      raise NotImplementedError, "my subclass should have implemented #pivotable?"
    end

    def restricted?
      raise NotImplementedError, "my subclass should have implemented #restricted?"
    end

    def inspect
      if name
        "#{name}"
      else
        "<CV#0x#{object_id.to_s(16)}>"
      end
    end
  end
end

module Cassowary
  class DummyVariable < AbstractVariable
    def dummy?
      true
    end

    def external?
      false
    end

    def pivotable?
      false
    end

    def restricted?
      true
    end
  end
end

module Cassowary
  class ObjectiveVariable < AbstractVariable
    def external?
      false
    end

    def pivotable?
      false
    end

    def restricted?
      false
    end
  end
end

module Cassowary
  class SlackVariable < AbstractVariable
    def external?
      false
    end

    def pivotable?
      true
    end

    def restricted?
      true
    end
  end
end

module Cassowary
  class Variable < AbstractVariable
    include Equalities

    attr_accessor :value

    def initialize(hash = {})
      super
      self.value = hash[:value]
    end

    def *(expr)
      self.as_linear_expression * expr
    end

    def +(expr)
      self.as_linear_expression + expr
    end

    def -(expr)
      self.as_linear_expression - expr
    end

    def /(expr)
      self.as_linear_expression / expr
    end

    def as_linear_expression
      expr = LinearExpression.new
      expr.terms[self] = 1.0
      expr
    end

    def external?
      true
    end

    def pivotable?
      false
    end

    def restricted?
      false
    end

    def -@
      -1.0.as_linear_expression * self
    end

    def inspect
      "#{super}[#{value.inspect}]"
    end

    def suggest_value(v)
      SimplexSolver.instance.add_edit_var(self, Strength::StrongStrength)
      SimplexSolver.instance.begin_edit
      SimplexSolver.instance.suggest_value(self, v)
      SimplexSolver.instance.resolve
      SimplexSolver.instance.end_edit
    end
  end
end

module Cassowary
  class Constraint < ConstraintObject
    attr_accessor :strength, :weight

    def expression
      raise NotImplementedError, "my subclass should have implemented #expression"
    end

    def edit_constraint?
      false
    end

    def inequality?
      false
    end

    def required?
      strength.required?
    end

    def stay_constraint?
      false
    end

    def enable(strength=:required)
      if strength == :required
        self.strength = Strength::RequiredStrength
      elsif strength == :strong
        self.strength = Strength::StrongStrength
      elsif strength == :medium
        self.strength = Strength::MediumStrength
      elsif strength == :weak
        self.strength = Strength::WeakStrength
      else
        raise ArgumentError, "Unsupported symbolic strength #{strength} " +
          "(expected one of :required, :strong, :medium, :weak"
      end
      SimplexSolver.instance.add_constraint(self)
    end

    def disable
      SimplexSolver.instance.remove_constraint(self)
    end
  end
end

module Cassowary
  class EditOrStayConstraint < Constraint
    attr_accessor :variable

    def initialize(hash = {})
      self.variable = hash[:variable]
      self.strength = hash[:strength]
      self.weight = (hash[:weight] || 1.0)
    end

    def expression
      e = LinearExpression.new
      e.constant = variable.value
      e.terms[variable] = -1.0
      e
    end
  end

  class EditConstraint < EditOrStayConstraint
    attr_accessor :value

    def initialize(hash = {})
      super
      self.value = hash[:value]
    end

    def edit_constraint?
      true
    end
  end

  class StayConstraint < EditOrStayConstraint
    def stay_constraint?
      true
    end
  end
end

module Cassowary
  class LinearConstraint < Constraint
    attr_accessor :expression
  end

  class LinearEquation < LinearConstraint
    def inspect
      "#{strength.inspect}(#{expression.inspect}=0)"
    end
  end

  class LinearInequality < LinearConstraint
    def inequality?
      true
    end

    def inspect
      "#{strength.inspect}(#{expression.inspect}>=0)"
    end
  end
end

module Cassowary
  class SymbolicWeight
    include Enumerable
    include Comparable

    StrengthLevels = 3

    def initialize(levels = {})
      @levels = [0.0] * StrengthLevels
      case levels
      when Hash
        levels.each_pair do |k, v|
          self[k] = v
        end
      when Array
        levels.each_with_index do |e, idx|
          self[idx] = e
        end
      else
        raise InternalError
      end
    end

    def each(*args, &block)
      @levels.each(*args, &block)
    end

    def [](idx)
      @levels[idx]
    end

    def []=(idx, value)
      @levels[idx] = value
    end

    def *(n)
      raise InternalError unless n.is_a? Numeric
      result = SymbolicWeight.new
      each_with_index do |e, idx|
        result[idx] = e * n
      end
      result
    end

    def /(n)
      raise InternalError unless n.is_a? Numeric
      result = SymbolicWeight.new
      each_with_index do |e, idx|
        result[idx] = e / n
      end
      result
    end

    def +(n)
      raise InternalError unless n.is_a? SymbolicWeight
      result = SymbolicWeight.new
      each_with_index do |e, idx|
        result[idx] = e + n[idx]
      end
      result
    end

    def -(n)
      raise InternalError unless n.is_a? SymbolicWeight
      result = SymbolicWeight.new
      each_with_index do |e, idx|
        result[idx] = e - n[idx]
      end
      result
    end

    def <=>(other)
      raise InternalError unless other.is_a? SymbolicWeight
      each_with_index do |e, idx|
        return -1 if e < other[idx]
        return 1 if e > other[idx]
      end
      0
    end

    def cl_approx(s)
      raise InternalError unless s.is_a? SymbolicWeight
      each_with_index do |e, idx|
        return false unless e.cl_approx(s[idx])
      end
      true
    end

    def cl_approx_zero
      cl_approx Zero
    end

    def definitely_negative
      epsilon = SimplexSolver::Epsilon
      nepsilon = 0.0 - epsilon
      each do |e|
        return true if e < nepsilon
        return false if e > epsilon
      end
      false
    end

    def symbolic_weight?
      true
    end

    def inspect
      "[" + @levels.join(",") + "]"
    end

    Zero = new([0.0] * StrengthLevels)
  end
end

module Cassowary
  class Strength
    attr_accessor :name, :symbolic_weight

    def initialize(name = nil, symbolic_weight = nil)
      self.name = name
      self.symbolic_weight = symbolic_weight
    end

    def required?
      self == RequiredStrength
    end

    def inspect
      "#{name}"
    end

    def each
      [RequiredStrength, StrongStrength, MediumStrength, WeakStrength].each do |str|
        yield str
      end
    end

    RequiredStrength = new "required"
    StrongStrength = new "strong", SymbolicWeight.new([1.0])
    MediumStrength = new "medium", SymbolicWeight.new([0.0, 1.0])
    WeakStrength = new "weak", SymbolicWeight.new([0.0, 0.0, 1.0])
  end
end

module Cassowary
  class LinearExpression < ConstraintObject
    include Equalities

    attr_accessor :constant, :terms

    def self.new_with_symbolic_weight
      result = self.new
      result.constant = SymbolicWeight::Zero
      result
    end

    def initialize
      self.constant = 0.0
      self.terms = {}
    end

    def any_variable
      if terms.any?
        terms.keys.first
      else
        raise InternalError, "expression is constant"
      end
    end

    def as_linear_expression
      self
    end

    def coefficient_for(variable)
      terms[variable] || 0.0
    end

    def constant?
      terms.empty?
    end

    def each_variable_and_coefficient(&block)
      terms.each_pair(&block)
    end

    def add_variable(variable, coefficient, subject = nil, solver = nil)
      if terms.has_key? variable
        new_coeff = coefficient + terms[variable]
        if new_coeff.cl_approx_zero
          terms.delete variable
          solver.note_removed_variable(variable, subject) if solver
        else
          terms[variable] = new_coeff
        end
      else
        terms[variable] = coefficient
        solver.note_added_variable(variable, subject) if solver
      end
    end

    def add_expression(expr, times, subject = nil, solver = nil)
      increment_constant(times * expr.constant)
      expr.each_variable_and_coefficient do |v, c|
        add_variable(v, times * c, subject, solver)
      end
    end

    def new_subject(subject)
      nreciprocal = -(1.0 / terms.delete(subject))
      self.constant *= nreciprocal
      terms.each_pair do |v, c|
        terms[v] = c * nreciprocal
      end
    end

    def change_subject(old, new)
      reciprocal = 1.0 / terms.delete(new)
      nreciprocal = -reciprocal
      self.constant *= nreciprocal
      terms.each_pair do |v, c|
        terms[v] = c * nreciprocal
      end
      terms[old] = reciprocal
    end

    def increment_constant(num)
      self.constant += num
    end

    def substitute_variable(var, expr, subject, solver)
      multiplier = terms.delete(var)
      increment_constant(multiplier * expr.constant)
      expr.each_variable_and_coefficient do |v, c|
        if old_coeff = terms[v]
          new_coeff = old_coeff + (multiplier * c)
          if new_coeff.cl_approx_zero
            terms.delete v
            solver.note_removed_variable v, subject
          else
            terms[v] = new_coeff
          end
        else
          terms[v] = multiplier * c
          solver.note_added_variable v, subject
        end
      end
    end

    def *(x)
      return x * constant if constant?

      n = if x.is_a? Numeric
            x.to_f
          else
            expr = x.as_linear_expression
            raise NonLinearResult unless expr.constant?
            expr.constant
          end
      result = LinearExpression.new
      result.constant = n * constant
      terms.each_pair do |v, c|
        result.terms[v] = n * c
      end
      result
    end

    def /(x)
      expr = x.as_linear_expression
      raise NonLinearResult unless expr.constant?
      self * (1.0 / expr.constant)
    end

    def +(x)
      expr = x.as_linear_expression
      result = LinearExpression.new
      result.constant = constant + expr.constant
      terms.each_pair do |v, c|
        result.terms[v] = c
      end
      expr.each_variable_and_coefficient do |v, c|
        result.add_variable(v, c)
      end
      result
    end

    def -(x)
      expr = x.as_linear_expression
      result = LinearExpression.new
      result.constant = constant - expr.constant
      terms.each_pair do |v, c|
        result.terms[v] = c
      end
      expr.each_variable_and_coefficient do |v, c|
        result.add_variable(v, -c)
      end
      result
    end

    def inspect
      terms.keys.inject(constant.inspect) do |str, v|
        "#{str}+#{terms[v].inspect}*#{v.inspect}"
      end
    end
  end
end

module Cassowary
  class SimplexSolver

    attr_accessor :rows, :columns, :objective, :infeasible_rows,
    :stay_plus_error_vars, :stay_minus_error_vars, :edit_vars,
    :edit_constraints, :edit_plus_error_vars, :edit_minus_error_vars,
    :prev_edit_constants, :new_edit_constants, :marker_vars,
    :error_vars, :auto_solve

    Epsilon = 1.0e-8

    def self.instance
      @instance ||= begin
                      s = SimplexSolver.new
                      s.auto_solve = false
                      s
                    end
    end

    def add_bounds(var, lower = nil, upper = nil)
      add_constraint(lower <= var) if lower
      add_constraint(var <= upper) if upper
    end

    def add_constraint(constraint)
      expr = make_expression(constraint)
      unless try_adding_directly(expr)
        add_with_artificial_variable(expr)
      end
      if auto_solve
        optimize(objective)
        set_external_variables
      end
    end

    def remove_constraint(cn)
      reset_stay_constants

      # remove any error variables from the objective function
      evars = error_vars.delete(cn) || []
      zrow = objective
      obj = rows[zrow]
      evars.each do |v|
        expr = rows[v]
        if expr.nil?
          obj.add_variable(v, cn.strength.symbolic_weight * -cn.weight, zrow, self)
        else
          obj.add_expression(expr, cn.strength.symbolic_weight * -cn.weight, zrow, self)
        end
      end

      exit_var = nil
      col = nil
      min_ratio = 0

      # try to make the marker variable basic, if it isn't already
      marker = marker_vars.delete(cn)
      unless rows.has_key? marker
        # choose which variable to move out of the basis. only consider restricted basic vars
        col = columns[marker]
        col.each do |v|
          if v.restricted?
            expr = rows[v]
            coeff = expr.coefficient_for(marker)
            # only consider negative coefficients
            if coeff < 0.0
              r = 0.0 - expr.constant / coeff
              if exit_var.nil? or r < min_ratio
                min_ratio = r
                exit_var = v
              end
            end
          end
        end

        # If exitVar is still nil at this point, then either the
        # marker variable has a positive coefficient in all equations,
        # or it only occurs in equations for unrestricted variables.
        # If it does occur in an equation for a restricted variable,
        # pick the equation that gives the smallest ratio.  (The row
        # with the marker variable will become infeasible, but all the
        # other rows will still be feasible; and we will be dropping
        # the row with the marker variable.  In effect we are removing
        # the non-negativity restriction on the marker variable.)
        if exit_var.nil?
          col.each do |v|
            if v.restricted?
              expr = rows[v]
              coeff = expr.coefficient_for(marker)
              r = expr.constant / coeff
              if exit_var.nil? or r < min_ratio
                min_ratio = r
                exit_var = v
              end
            end
          end
        end

        # If exitVar is still nil, and col is empty, then exitVar
        # doesn't occur in any equations, so just remove it.
        # Otherwise pick an exit var from among the unrestricted
        # variables whose equation involves the marker var
        if exit_var.nil?
          if col.empty?
            remove_parametric_var(marker)
          else
            exit_var = col.to_a.first
          end
        end

        if exit_var
          pivot(marker, exit_var)
        end
      end

      # Now delete any error variables.  If cn is an inequality, it
      # also contains a slack variable; but we use that as the
      # marker variable and so it has been deleted when we removed
      # its row
      if rows.has_key?(marker)
        remove_row(marker)
      end
      evars.each do |v|
        remove_parametric_var(v) unless v == marker
      end

      if cn.stay_constraint?
        self.stay_plus_error_vars = stay_plus_error_vars.reject do |v| evars.include? v end
        self.stay_minus_error_vars = stay_minus_error_vars.reject do |v| evars.include? v end
      end

      if cn.edit_constraint?
        # find the index in editPlusErrorVars of the error variable for this constraint
        index = find_edit_error_index(evars)

        # remove the error variables from editPlusErrorVars and editMinusErrorVars
        edit_plus_error_vars.delete_at(index)
        edit_minus_error_vars.delete_at(index)

        # remove the constants from prevEditConstants
        prev_edit_constants.delete_at(index)
      end

      if auto_solve
        optimize(zrow)
        set_external_variables
      end
    end

    def resolve(cs = nil)
      if cs
        self.new_edit_constants = cs
      end

      # Re-solve the current collection of constraints for the new values in newEditConstants.
      self.infeasible_rows = []
      update_stay_constants
      reset_edit_constants
      dual_optimize
      set_external_variables
    end

    def solve
      update_stay_constants
      optimize objective
      set_external_variables
    end

    def suggest_value(var, val)
      edit_vars.each_with_index do |v, idx|
        if v == var
          new_edit_constants[idx] = val
        end
        return self
      end
      raise InternalError, "variable not currently being edited"
    end

    def add_edit_var(variable, strength)
      add_constraint(EditConstraint.new variable: variable, strength: strength)
    end

    def add_stay(variable, strength = Strength::WeakStrength)
      add_constraint(StayConstraint.new variable: variable, strength: strength)
    end

    def begin_edit
      self.new_edit_constants = [nil] * edit_vars.size
    end

    def end_edit
      edit_constraints.each do |cn|
        remove_constraint(cn)
      end
      self.edit_vars = []
      self.edit_constraints = []
    end

    def note_added_variable(var, subject)
      if subject
        columns[var] ||= Set.new
        columns[var] << subject
      end
    end

    def note_removed_variable(var, subject)
      if subject
        columns[var].delete(subject)
      end
    end

    private
    def add_row(var, expr)
      rows[var] = expr
      expr.each_variable_and_coefficient do |v, c|
        columns[v] ||= Set.new
        columns[v] << var
      end
    end

    def add_with_artificial_variable(expr)
      av = SlackVariable.new
      az = ObjectiveVariable.new
      azrow = LinearExpression.new

      # the artificial objective is av, which we know is equal to expr
      # (which contains only parametric variables)
      azrow.constant = expr.constant
      expr.each_variable_and_coefficient do |v, c|
        azrow.terms[v] = c
      end

      add_row(az, azrow)
      add_row(av, expr)

      # try to optimize av to 0
      optimize az

      # Check that we were able to make the objective value 0.  If
      # not, the original constraint was unsatisfiable.
      raise RequiredFailure unless azrow.constant.cl_approx_zero

      if e = rows[av]
        # Find another variable in this row and pivot, so that av
        # becomes parametric.  If there isn't another variable in the
        # row then the tableau contains the equation av=0 -- just
        # delete av's row.
        if e.constant?
          remove_row(av)
          return nil
        else
          pivot(e.any_variable, av)
        end
      end

      # av should be parametric at this point
      remove_parametric_var av

      # remove the temporary objective function
      remove_row az
    end

    def choose_subject(expr)
      # We are trying to add the constraint expr=0 to the tableaux.
      # Try to choose a subject (a variable to become basic) from
      # among the current variables in expr.  If expr contains any
      # unrestricted variables, then we must choose an unrestricted
      # variable as the subject.  Also, if the subject is new to the
      # solver we won't have to do any substitutions, so we prefer new
      # variables to ones that are currently noted as parametric.  If
      # expr contains only restricted variables, if there is a
      # restricted variable with a negative coefficient that is new to
      # the solver we can make that the subject.  Otherwise we can't
      # find a subject, so return nil.  (In this last case we have to
      # add an artificial variable and use that variable as the
      # subject -- this is done outside this method though.)
      #
      # Note: in checking for variables that are new to the solver, we
      # ignore whether a variable occurs in the objective function, since
      # new slack variables are added to the objective function by
      # 'makeExpression:', which is called before this method.
      found_unrestricted = false
      found_new_restricted = false
      subject = nil
      coeff = nil

      expr.each_variable_and_coefficient do |v, c|
        if found_unrestricted
          # We have already found an unrestricted variable.  The only
          # time we will want to use v instead of the current choice
          # 'subject' is if v is unrestricted and new to the solver
          # and 'subject' isn't new.  If this is the case just pick v
          # immediately and return.
          unless v.restricted?
            return v unless columns.has_key? v
          end
        else
          if v.restricted?
            # v is restricted.  If we have already found a suitable
            # restricted variable just stick with that.  Otherwise, if
            # v is new to the solver and has a negative coefficient
            # pick it.  Regarding being new to the solver -- if the
            # variable occurs only in the objective function we regard
            # it as being new to the solver, since error variables are
            # added to the objective function when we make the
            # expression.  We also never pick a dummy variable here.
            if !found_new_restricted and !v.dummy? and c < 0.0
              col = columns[v]
              if col.nil? or (col.size == 1 and col.include? objective)
                subject = v
                found_new_restricted = true
              end
            end
          else
            # v is unrestricted.  If v is also new to the solver just
            # pick it now
            return v unless columns.has_key? v
            subject = v
            found_unrestricted = true
          end
        end
      end

      # subject is nil.  Make one last check -- if all of the
      # variables in expr are dummy variables, then we can pick a
      # dummy variable as the subject.
      return subject unless subject.nil?
      expr.each_variable_and_coefficient do |v, c|
        return nil unless v.dummy?
        # if v is new to the solver tentatively make it the subject
        unless columns.has_key? v
          subject = v
          coeff = c
        end
      end

      # If we get this far, all of the variables in the expression
      # should be dummy variables.  If the constant is nonzero we are
      # trying to add an unsatisfiable required constraint.  (Remember
      # that dummy variables must take on a value of 0.)  Otherwise,
      # if the constant is zero, multiply by -1 if necessary to make
      # the coefficient for the subject negative.
      raise RequiredFailure unless expr.constant.cl_approx_zero
      if coeff > 0
        expr.each_variable_and_coefficient do |v, c|
          expr.terms[v] = 0.0 - c
        end
      end

      subject
    end

    def delta_edit_constant(delta, plus_error_var, minus_error_var)
      if expr = rows[plus_error_var]
        expr.increment_constant delta
        # error variables are always restricted -- so the row is
        # infeasible if the constant is negative
        (infeasible_rows << plus_error_var) if expr.constant < 0.0
        return nil
      end

      if expr = rows[minus_error_var]
        expr.increment_constant -delta
        (infeasible_rows << plus_error_var) if expr.constant < 0.0
        return nil
      end

      # Neither minusErrorVar nor plusErrorVar is basic.  So they must
      # both be nonbasic, and will both occur in exactly the same
      # expressions.  Find all the expressions in which they occur by
      # finding the column for the minusErrorVar (it doesn't matter
      # whether we look for that one or for plusErrorVar).  Fix the
      # constants in these expressions.
      columns[minus_error_var].each do |basic_var|
        expr = rows[basic_var]
        c = expr.coefficient_for(minus_error_var)
        expr.increment_constant c * delta
        if basic_var.restricted? and expr.constant < 0.0
          infeasible_rows << basic_var
        end
      end
    end

    def dual_optimize
      # We have set new values for the constants in the edit
      # constraints.  Re-optimize using the dual simplex algorithm.
      entry_var = nil
      zrow = rows[objective]
      until infeasible_rows.empty?
        exit_var = infeasible_rows.shift
        if expr = rows[exit_var]
          if expr.constant < 0.0
            ratio = nil
            expr.each_variable_and_coefficient do |v, c|
              if c > 0.0 and v.pivotable?
                zc = zrow.terms[v]
                r = zc ? zc / c : SymbolicWeight::Zero
                if ratio.nil? or r < ratio or (r == ratio and v.hash < entry_var.hash)
                  entry_var = v
                  ratio = r
                end
              end
            end
            raise InternalError if ratio.nil?
            pivot entry_var, exit_var
          end
        end
      end
    end

    def find_edit_error_index(evars)
      evars.each do |v|
        if index = edit_plus_error_vars.index(v)
          return index
        end
      end
      raise InternalError, "didn't find a variable"
    end

    def initialize
      self.objective = ObjectiveVariable.new
      self.rows = {objective => LinearExpression.new_with_symbolic_weight}
      self.columns = {}
      self.infeasible_rows = []
      self.prev_edit_constants = []
      self.stay_plus_error_vars = []
      self.stay_minus_error_vars = []
      self.edit_vars = []
      self.edit_constraints = []
      self.edit_plus_error_vars = []
      self.edit_minus_error_vars = []
      self.marker_vars = {}
      self.error_vars = {}
      self.auto_solve = true
    end

    def make_expression(cn)
      # Make a new linear expression representing the constraint cn,
      # replacing any basic variables with their defining expressions.
      # Normalize if necessary so that the constant is non-negative.
      # If the constraint is non-required give its error variables an
      # appropriate weight in the objective function.
      expr = LinearExpression.new
      cnexpr = cn.expression
      expr.constant = cnexpr.constant
      cnexpr.each_variable_and_coefficient do |v, c|
        e = rows[v]
        if e.nil?
          expr.add_variable(v, c)
        else
          expr.add_expression(e, c)
        end
      end

      # add slack and error variables as needed
      if cn.inequality?
        # cn is an inequality, so add a slack variable.  The original
        # constraint is expr>=0, so that the resulting equality is
        # expr-slackVar=0.  If cn is also non-required add a negative
        # error variable, giving expr-slackVar = -errorVar, in other
        # words expr-slackVar+errorVar=0.  Since both of these
        # variables are newly created we can just add them to the
        # expression (they can't be basic).
        slackvar = SlackVariable.new
        expr.terms[slackvar] = -1.0
        marker_vars[cn] = slackvar
        unless cn.required?
          eminus = SlackVariable.new
          expr.terms[eminus] = 1.0

          zrow = rows[objective]
          zrow.terms[eminus] = cn.strength.symbolic_weight * cn.weight
          error_vars[cn] = [eminus]
          note_added_variable(eminus, objective)
        end
      else
        if cn.required?
          # Add a dummy variable to the expression to serve as a
          # marker for this constraint.  The dummy variable is never
          # allowed to enter the basis when pivoting.
          dummyvar = DummyVariable.new
          expr.terms[dummyvar] = 1.0
          marker_vars[cn] = dummyvar
        else
          # cn is a non-required equality.  Add a positive and a
          # negative error variable, making the resulting constraint
          # expr = eplus - eminus, in other words expr-eplus+eminus=0
          eplus = SlackVariable.new
          eminus = SlackVariable.new
          expr.terms[eplus] = -1.0
          expr.terms[eminus] = 1.0

          # index the constraint under one of the error variables
          marker_vars[cn] = eplus
          zrow = rows[objective]
          zrow.terms[eplus] = cn.strength.symbolic_weight * cn.weight
          note_added_variable(eplus, objective)
          zrow.terms[eminus] = cn.strength.symbolic_weight * cn.weight
          error_vars[cn] = [eplus, eminus]
          note_added_variable(eminus, objective)

          if cn.stay_constraint?
            stay_plus_error_vars << eplus
            stay_minus_error_vars << eminus
          end

          if cn.edit_constraint?
            edit_vars << cn.variable
            edit_constraints << cn
            edit_plus_error_vars << eplus
            edit_minus_error_vars << eminus
            prev_edit_constants << cnexpr.constant
          end
        end
      end

      # The constant in the expression should be non-negative.  If
      # necessary normalize the expression by multiplying by -1.
      if expr.constant < 0
        expr.constant = 0.0 - expr.constant
        expr.each_variable_and_coefficient do |v, c|
          expr.terms[v] = 0.0 - c
        end
      end
      expr
    end

    def optimize(zvar)
      # Minimize the value of the objective.  (The tableau should
      # already be feasible.)
      zrow = rows[zvar]
      exitvar = nil
      while true do
        # Find a variable in the objective function with a negative
        # coefficient (ignoring dummy variables). If all coefficients
        # are positive we're done.  To implement Bland's anticycling
        # rule, if there is more than one variable with a negative
        # coefficient, pick the one with the smaller id (implemented
        # as hash).
        entryvar = nil
        zrow.each_variable_and_coefficient do |v, c|
          if v.pivotable? and c.definitely_negative and (entryvar.nil? or v.hash < entryvar.hash)
            entryvar = v
          end
        end

        # if all coefficients were positive (or if the objective
        # function has no pivotable variables) we are at optimum
        return nil if entryvar.nil?

        # Choose which variable to move out of the basis.  Only
        # consider pivotable basic variables (that is, restricted,
        # non-dummy variables).
        minratio = nil
        columns[entryvar].each do |v|
          if v.pivotable?
            expr = rows[v]
            coeff = expr.coefficient_for(entryvar)

            if coeff < 0.0
              r = -(expr.constant / coeff)
              # Decide whether to make v be the best choice for exit
              # variable so far by comparing the ratios. In case of a
              # tie, choose the variable with the smaller id (to
              # implement Bland's anticycling rule).
              if minratio.nil? or r < minratio or (r == minratio and v.hash < exitvar.hash)
                minratio = r
                exitvar = v
              end
            end
          end
        end

        # If minRatio is still nil at this point, it means that the
        # objective function is unbounded, i.e. it can become
        # arbitrarily negative.  This should never happen in this
        # application.
        raise InternalError if minratio.nil?
        pivot entryvar, exitvar
      end
    end

    def pivot(entryvar, exitvar)
      # Do a pivot.  Move entryVar into the basis (i.e. make it a
      # basic variable), and move exitVar out of the basis (i.e. make
      # it a parametric variable). expr is the expression for the
      # exit variable (about to leave the basis) -- so that the old
      # tableau includes the equation exitVar = expr
      expr = remove_row(exitvar)

      # Compute an expression for the entry variable.  Since expr has
      # been deleted from the tableau we can destructively modify it
      # to build this expression.
      expr.change_subject exitvar, entryvar
      substitute_out(entryvar, expr)
      add_row(entryvar, expr)
    end

    def remove_parametric_var(var)
      set = columns.delete(var)
      set.each do |v|
        rows[v].terms.delete(var)
      end
    end

    def remove_row(var)
      expr = rows.delete(var)
      expr.each_variable_and_coefficient do |v, c|
        columns[v].delete var
      end
      infeasible_rows.delete(var)
      expr
    end

    def reset_edit_constants
      # Each of the non-required edits will be represented by an
      # equation of the form
      #
      #   v = c + eplus - eminus
      #
      # where v is the variable with the edit, c is the previous edit
      # value, and eplus and eminus are slack variables that hold the
      # error in satisfying the edit constraint.  We are about to
      # change something, and we want to fix the constants in the
      # equations representing the edit constraints.  If one of eplus
      # and eminus is basic, the other must occur only in the
      # expression for that basic error variable.  (They can't both be
      # basic.)  Fix the constant in this expression.  Otherwise they
      # are both nonbasic.  Find all of the expressions in which they
      # occur, and fix the constants in those.  See the UIST paper for
      # details.

      raise InternalError if new_edit_constants.size != edit_plus_error_vars.size
      new_edit_constants.each_with_index do |ec, idx|
        delta = ec - prev_edit_constants[idx]
        prev_edit_constants[idx] = ec
        delta_edit_constant(delta, edit_plus_error_vars[idx], edit_minus_error_vars[idx])
      end
    end

    def reset_stay_constants
      # Each of the non-required stays will be represented by an
      # equation of the form
      #
      #   v = c + eplus - eminus
      #
      # where v is the variable with the stay, c is the previous value
      # of v, and eplus and eminus are slack variables that hold the
      # error in satisfying the stay constraint.  We are about to
      # change something, and we want to fix the constants in the
      # equations representing the stays.  If both eplus and eminus
      # are nonbasic they have value 0 in the current solution,
      # meaning the previous stay was exactly satisfied.  In this case
      # nothing needs to be changed.  Otherwise one of them is basic,
      # and the other must occur only in the expression for that basic
      # error variable.  Reset the constant in this expression to 0.

      stay_plus_error_vars.each_with_index do |ev, idx|
        expr = rows[ev] || rows[stay_minus_error_vars[idx]]
        expr.constant = 0.0 if expr
      end
    end

    def update_stay_constants
      # Each of the non-required stays will be represented by an
      # equation of the form
      #
      #   v = c + eplus - eminus
      #
      # where v is the variable with the stay, c is the previous value
      # of v, and eplus and eminus are slack variables that hold the
      # error in satisfying the stay constraint. We are about to solve
      # the whole thing again. Reset c in this expression to the
      # current value of v, so the "programmer intent" is still
      # satisfied.

      stay_plus_error_vars.each_with_index do |ev, idx|
        expr = rows[ev] || rows[stay_minus_error_vars[idx]]
        if expr
          marker_vars.each_pair do |staycn, stayvariable|
            if stayvariable == expr
              expr.constant = staycn.variable.value
              break
            end
          end
        end
      end
    end

    def set_external_variables
      # Set each external basic variable to its value, and set each
      # external parametric variable to 0.  (It isn't clear that we
      # will ever have external parametric variables -- every external
      # variable should either have a stay on it, or have an equation
      # that defines it in terms of other external variables that do
      # have stays.  For the moment I'll put this in though.)
      # Variables that are internal to the solver don't actually store
      # values -- their values are just implicit in the tableu -- so
      # we don't need to set them.
      rows.each_pair do |var, expr|
        var.value = expr.constant if var.external?
      end

      columns.keys.each do |var|
        var.value = 0.0 if var.external?
      end
    end

    def substitute_out(old_var, expr)
      col = columns.delete(old_var)
      col.each do |v|
        row = rows[v]
        row.substitute_variable(old_var, expr, v, self)
        if v.restricted? and row.constant < 0.0
          infeasible_rows << v
        end
      end
    end

    def try_adding_directly(expr)
      # If possible choose a subject for expr (a variable to become
      # basic) from among the current variables in expr.  If this
      # isn't possible, add an artificial variable and use that
      # variable as the subject.
      subject = choose_subject(expr)
      return false if subject.nil?
      expr.new_subject subject
      if columns.has_key? subject
        substitute_out subject, expr
      end
      add_row subject, expr
      true
    end
  end
end

class Object
  def cl_approx(x)
    self == x
  end

  def symbolic_weight?
    false
  end
end

class Float
  def cl_approx(float)
    # Answer true if I am approximately equal to the argument
    epsilon = Cassowary::SimplexSolver::Epsilon
    if self == 0.0
      float.abs < epsilon
    elsif float == 0.0
      abs < epsilon
    else
      (self - float).abs < (abs * epsilon)
    end
  end

  def cl_approx_zero
    cl_approx 0.0
  end

  def definitely_negative
    # return true if I am definitely negative (i.e. smaller than negative epsilon)"
    self < (0.0 - Cassowary::SimplexSolver::Epsilon)
  end
end

class Numeric
  include Cassowary::Equalities

  def as_linear_expression
    expr = Cassowary::LinearExpression.new
    expr.constant = self.to_f
    expr
  end
end

Constraints.for_variables_of_type Numeric do |name, value|
  v = Cassowary::Variable.new(name: name, value: value)
  Cassowary::SimplexSolver.instance.add_stay(v)
  v
end
Constraints.register_solver Cassowary::SimplexSolver.instance

puts "Cassowary constraint solver loaded."
