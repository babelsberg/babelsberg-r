require "libdeltablue"
require "libz3"
require "libcassowary"

class Array
  def mapsum(&block)
    freeze
    return 0 if self.empty?
    return block[self[0]].? + self[1..-1].mapsum(&block)
  end
end

class Taxpayer
  attr_accessor :student_record, :jobs, :tax_deductibles,
  :tax_allowance, :church_tax, :deduction,
  :lump_deduction, :income, :taxable_income, :tax_rate, :taxes_due

  attr_accessor :dr, :z3, :cassowary, :cassowary_2, :z3_2, :dr_2

  def inspect
    "#<Student: record: #{student_record}, jobs: #{jobs}, deductibles: #{tax_deductibles}, "\
    "allowance: #{tax_allowance}, church_tax: #{church_tax}, "\
    "lump_deduction: #{lump_deduction}, deduction: #{deduction}, "\
    "income: #{income}, taxable_income: #{taxable_income}, "\
    "tax rate: #{tax_rate}, taxes due: #{taxes_due}, "\
    "extra expenses? #{extra_expenses?}"
  end

  def initialize(jobs_, tax_deductibles_)
    @is_student = false
    @jobs = jobs_
    @tax_deductibles = tax_deductibles_
    @is_christian = false
    @has_extra_expenses = false

    @dr = DeltaRed::Solver.new
    dr.singleton_class.class_eval do
      def weight
        1000
      end
    end
    @z3 = Z3.new
    z3.singleton_class.class_eval do
      def weight
        5
      end
    end
    @cassowary = Cassowary::SimplexSolver.new
    cassowary.auto_solve = false
    cassowary.singleton_class.class_eval do
      def weight
        2
      end
    end
    @cassowary_2 = Cassowary::SimplexSolver.new
    cassowary_2.auto_solve = false
    cassowary_2.singleton_class.class_eval do
      def weight
        1
      end
    end
    @z3_2 = Z3.new
    z3_2.singleton_class.class_eval do
      def weight
        0
      end
    end
    @dr_2 = DeltaRed::Solver.new
    dr_2.singleton_class.class_eval do
      def weight
        -1
      end
    end

    always(solver: dr,
           predicate: -> { !!student_record == student? },
           methods: -> {[student? <-> { !student_record.nil? }]})

    always(solver: z3) { (student?.? ).ite(tax_allowance == 8000, tax_allowance == 4000) }
    always(solver: z3) { (christian?.? ).ite(church_tax == 10, church_tax == 0) }

    always(priority: :strong, solver: cassowary) { lump_deduction == 0 }
    always(solver: cassowary) { lump_deduction + tax_deductibles.mapsum(&:cost) == deduction }
    always(solver: cassowary) { deduction >= 1000 }
    always(solver: cassowary) { income == jobs.mapsum(&:income) }

    p "#{taxable_income} == #{income} - #{deduction} - #{tax_allowance}"
    always(solver: cassowary_2) { taxable_income == income - deduction - tax_allowance }

    # always(solver: dr_2,
    #        predicate: -> { @tax_rate == tax_rate_for(@taxable_income) },
    #        methods: -> {[@tax_rate <-> { tax_rate_for(@taxable_income) }]})

    # always(solver: nil) do
    #   self.tax_rate = tax_rate_for(taxable_income)
    #   true
    # end

    always(solver: z3_2) do
      (taxable_income.? <= 0).ite(tax_rate == 0,
                                  (taxable_income <= 8000).ite(tax_rate == 10.0,
                                                               (taxable_income <= 20_000).ite(tax_rate == 30.0, tax_rate == 50.0)))
    end
    always(solver: z3_2) { extra_expenses? == (taxable_income.? < 0) }
    always(solver: z3_2) { taxes_due == taxable_income.? * (tax_rate + church_tax.? ) / 100.0 }
  end

  def tax_rate_for(income)
    case income
    when 0...8000 then 10
    when 8000...20_000 then 30
    else income < 0 ? 0 : 50
    end
  end

  def student?
    @is_student
  end

  def christian?
    @is_christian
  end

  def christian!
    @is_christian = true
  end

  def extra_expenses?
    @has_extra_expenses
  end
end

Job = Struct.new("Job", :name, :income)
TaxDeductibleItem = Struct.new("TaxDeductibleItem", :name, :cost)

student = Taxpayer.new([], [])
student.student_record = Object.new
student.christian!
student.tax_deductibles = [TaxDeductibleItem.new("Laptop", 200)]
p student
puts "===="
student.jobs = [Job.new("Finn", 7000), Job.new("HPI", 8000)]
p student
p "#{student.taxable_income} == #{student.income} - #{student.deduction} - #{student.tax_allowance}"
p student
student.tax_deductibles = student.tax_deductibles + [TaxDeductibleItem.new("Expensive Hobby", 5000)]
p student
