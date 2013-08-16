class Lead
  attr_reader :voltage, :current
  def initialize
    # set voltage and current to 0.0 for now so that they are of type Float (constraints may change it later)
    @voltage = 0.0
    @current = 0.0
  end
end

class TwoLeadedObject
  attr_reader :lead1, :lead2
  def initialize
    @lead1 = Lead.new
    @lead2 = Lead.new
    # constrain currents to be equal magnitude and opposite
    always { lead1.current + lead2.current == 0.0 }
  end
end

class Resistor < TwoLeadedObject
  attr_reader :resistance
  def initialize(resistance)
    super()
    @resistance = resistance
    # Ohm's Law constraint
    unless defined? Cassowary
      always { lead1.voltage - lead2.voltage == resistance.? * lead1.current }
    else
      # using Cassowary
      # temporarily use a fixed value for the resistance to avoid getting a nonlinear constraint error
      always { lead1.voltage - lead2.voltage == 100*lead1.current }
    end
  end
end

class Battery < TwoLeadedObject
  attr_reader :supply_voltage
  def initialize(supply_voltage)
    super()
    @supply_voltage = supply_voltage
    always { lead2.voltage - lead1.voltage == @supply_voltage.? }
  end
end

class Ground
  attr_reader :lead
  def initialize
    @lead = Lead.new
    # constrain the voltage and current to be 0
    always { lead.voltage == 0.0 }
    always { lead.current == 0.0 }
  end
end

class Wire < TwoLeadedObject
  def initialize
    super()
    always { lead1.voltage == lead2.voltage }
  end
end

module Kernel
  def connect(leads)
    return if leads.empty?
    # all voltages should be equal
    leads[1..-1].each { |a| always { a.voltage == leads[0].voltage } }
    # sum of currents has to be 0
    sum = leads.inject(0) do |memo, lead|
      Constraint.new { lead.current }.value + memo
    end
    always { sum == 0 }
  end
end
