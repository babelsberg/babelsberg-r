require "libdeltablue"
require "libz3"
require "libcassowary"

class Array
  def mapsum(&block)
    return 0 if self.empty?
    return block[self[0]] + self[1..-1].mapsum(&block)
  end
end

class Taxpayer
  attr_accessor :student_record, :jobs, :tax_deductibles,
  :tax_allowance, :church_tax, :deduction,
  :lump_deduction, :income, :taxable_income, :tax_rate, :taxes_due

  attr_accessor :dr, :z3, :cassowary, :cassowary_2, :z3_2

  def inspect
    "#<Student: record: #{student_record}, jobs: #{jobs}, deductibles: #{tax_deductibles}, "\
    "allowance: #{tax_allowance}, church_tax: #{church_tax}, "\
    "lump_deduction: #{lump_deduction}, deduction: #{deduction}, "\
    "income: #{income}, taxable_income: #{taxable_income}, "\
    "tax rate: #{tax_rate}, taxes due: #{taxes_due}, "\
    "extra expenses? #{extra_expenses?}"
  end

  def initialize(jobs, tax_deductibles)
    @is_student = false
    @jobs = jobs
    @tax_deductibles = tax_deductibles
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

    always(solver: dr, predicate: -> { student_record.nil? or student? }) do
      [
       # student_record <-> do
       #   # Called when `student?' changes
       #   puts "You have to hand in a student record, otherwise you cannot apply for student status"
       #   nil
       # end,
       student? <-> { !student_record.nil? }]
    end

    always(solver: z3) { student?.ite(tax_allowance == 8000, tax_allowance == 4000) }
    always(solver: z3) { christian?.ite(church_tax == 10, church_tax == 0) }

    always(priority: :strong, solver: cassowary) { lump_deduction == 0 }
    always(solver: cassowary) { lump_deduction + tax_deductibles.mapsum(&:cost) == deduction }
    always(solver: cassowary) { deduction >= 1000 }
    always(solver: cassowary) { income == jobs.mapsum(&:income) }

    always(solver: cassowary_2) { taxable_income == income.? - deduction.? - tax_allowance.? }

    always(solver: nil) do
      tax_rate = case taxable_income
                 when 0...8000
                   10
                 when 8000...20_000
                   30
                 else
                   if taxable_income < 4000
                     0
                   else
                     50
                   end
                 end
      true # re-run this
    end

    always(solver: z3_2) { extra_expenses? == (taxable_income < 0) }
    always(solver: z3_2) { taxes_due == taxable_income * (tax_rate.? + church_tax) }
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
p student
student.christian!
p "Christ!"
p student
student.student_record = Object.new
p "Student!"
p student.student?
p student
student.jobs = [Job.new("Finn", 5000), Job.new("Hpi", 4000)]
p "I'm employed!"
p student
student.tax_deductibles = [TaxDeductibleItem.new("laptop", 200), TaxDeductibleItem.new("konto", 16)]
p "I have expenses"
p student
student.jobs.first.income = 10_000
p "I earn a lot"
p student

student = Taxpayer.new([Job.new("Finn", 9000), Job.new("Hpi", 4000)], [TaxDeductibleItem.new("laptop", 200), TaxDeductibleItem.new("konto", 16)])
p student
student.christian!
