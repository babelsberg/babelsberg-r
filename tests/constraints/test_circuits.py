import py

from ..base import BaseTopazTest

CircuitClasses = """
require "libcassowary"

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
    # temporarily use a fixed value for the resistance to avoid getting a nonlinear constraint error
    # always { lead1.voltage - lead2.voltage == resistance*lead1.current }
    always { lead1.voltage - lead2.voltage == 100*lead1.current }
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

"""

class TestCircuits(BaseTopazTest):
    def execute(self, space, code, *libs):
        return [space.execute("""
                require "%s"

                %s
                """ % (lib, code)) for lib in libs]

    def test_ground(self, space):
        w_res = space.execute(CircuitClasses + """
          g = Ground.new
          return [ g.lead.voltage, g.lead.current] """)
        assert self.unwrap(space, w_res) == [0.0, 0.0]

    def test_twoleadedobject(self, space):
        w_res = space.execute(CircuitClasses + """
          t = TwoLeadedObject.new
          always { t.lead1.voltage == 20.0 }
          always { t.lead1.current == 12.0 }
          return [ t.lead1.voltage, t.lead1.current, t.lead2.current, ] """)
        assert self.unwrap(space, w_res) == [20.0, 12.0, -12.0]

    def test_battery_setup(self, space):
        w_res = space.execute(CircuitClasses + """
          b = Battery.new(5.0)
          return [ b.lead2.voltage-b.lead1.voltage, b.lead1.current, b.lead2.current ] """)
        assert self.unwrap(space, w_res) == [5.0, 0.0, 0.0]

    def test_battery_simple(self, space):
        w_res = space.execute(CircuitClasses + """
          b = Battery.new(5.0)
          always { b.lead1.voltage == 20.0 }
          always { b.lead1.current == 12.0 }
          return [ b.lead1.voltage, b.lead1.current,
                   b.lead2.voltage, b.lead2.current ] """)
        assert self.unwrap(space, w_res) == [20.0, 12.0, 25.0, -12.0]

    def test_resistor(self, space):
        w_res = space.execute(CircuitClasses + """
          # CAUTION!  Note that the resistor class temporarily has 100 ohms hardwired
          r = Resistor.new(100.0)
          always { r.lead1.voltage == 10.0 }
          always { r.lead2.voltage == 5.0 }
          return [ r.lead1.voltage, r.lead1.current, r.lead2.voltage, r.lead2.current ] """)
        assert self.unwrap(space, w_res) == [10.0, 0.05, 5.0, -0.05]

    def test_wire(self, space):
        w_res = space.execute(CircuitClasses + """
          w = Wire.new
          always { w.lead1.voltage == 10.0 }
          always { w.lead1.current == 2.0 }
          return [ w.lead1.voltage, w.lead1.current, w.lead2.voltage, w.lead2.current ] """)
        assert self.unwrap(space, w_res) == [10.0, 2.0, 10.0, -2.0]

    def test_connect0(self, space):
        w_res = space.execute(CircuitClasses + """
          connect []
          return 10  """)
        assert self.unwrap(space, w_res) == 10

    def test_connect1(self, space):
        w_res = space.execute(CircuitClasses + """
          a = Lead.new
          always { a.voltage == 7.0 }
          connect [a]
          return [a.voltage, a.current]  """)
        assert self.unwrap(space, w_res) == [7.0, 0.0]

    def test_connect2(self, space):
        w_res = space.execute(CircuitClasses + """
          a = Lead.new
          b = Lead.new
          always { a.voltage == 7.0 }
          always { a.current == 3.0 }
          connect [a,b]
          return [a.voltage, a.current, b.voltage, b.current]  """)
        assert self.unwrap(space, w_res) == [7.0, 3.0, 7.0, -3.0]
   
    def test_connect3(self, space):
        w_res = space.execute(CircuitClasses + """
          a = Lead.new
          b = Lead.new
          c = Lead.new
          always { a.voltage == 7.0 }
          always { a.current == 3.0 }
          always { b.current == 5.0 }
          connect [a,b,c]
          return [a.voltage, a.current, b.voltage, b.current, c.voltage, c.current]  """)
        assert self.unwrap(space, w_res) == [7.0, 3.0, 7.0, 5.0, 7.0, -8.0]

    def test_connect4(self, space):
        w_res = space.execute(CircuitClasses + """
          a = Lead.new
          b = Lead.new
          c = Lead.new
          d = Lead.new
          always { a.voltage == 7.0 }
          always { a.current == 3.0 }
          always { b.current == 5.0 }
          always { d.current == 1.5 }
          connect [a,b,c,d]
          return [a.voltage, a.current, b.voltage, b.current, c.voltage, c.current, d.voltage, d.current]  """)
        assert self.unwrap(space, w_res) == [7.0, 3.0, 7.0, 5.0, 7.0, -9.5, 7.0, 1.5]
   
    def test_battery_resistor(self, space):
        w_res = space.execute(CircuitClasses + """
          g = Ground.new
          # CAUTION!  Note that the resistor class temporarily has 100 ohms hardwired
          r = Resistor.new(100.0)
          b = Battery.new(5.0)
          connect [g.lead, r.lead1, b.lead1]
          connect [r.lead2, b.lead2]
          return [ r.lead1.voltage, r.lead1.current, r.lead2.voltage, r.lead2.current,
                   b.lead1.voltage, b.lead1.current, b.lead2.voltage, b.lead2.current, b.supply_voltage,
                   g.lead.voltage, g.lead.current] """)
        assert self.unwrap(space, w_res) == [0.0, -0.05, 5.0, 0.05, 0.0, 0.05, 5.0, -0.05, 5.0, 0.0, 0.0]

    def test_wheatstone_bridge(self, space):
        w_res = space.execute(CircuitClasses + """
          g = Ground.new
          b = Battery.new(5.0)
          # CAUTION!  Note that the resistor class temporarily has 100 ohms hardwired
          # Unfortunately this makes the Wheatstone bridge not very interesting yet
          r1 = Resistor.new(100.0)
          r2 = Resistor.new(100.0)
          r3 = Resistor.new(100.0)
          r4 = Resistor.new(100.0)
          w = Wire.new
          connect [g.lead, b.lead1, r3.lead2, r4.lead2]
          connect [b.lead2, r1.lead1, r2.lead1]
          connect [r1.lead2, r3.lead1, w.lead1]
          connect [r2.lead2, r4.lead1, w.lead2]
          return [ b.lead1.voltage, b.lead1.current, b.lead2.voltage, b.lead2.current, b.supply_voltage,
                   g.lead.voltage, g.lead.current,
                   r1.lead1.voltage, r1.lead1.current, r1.lead2.voltage, r1.lead2.current,
                   r2.lead1.voltage, r2.lead1.current, r2.lead2.voltage, r2.lead2.current,
                   r3.lead1.voltage, r3.lead1.current, r3.lead2.voltage, r3.lead2.current,
                   r4.lead1.voltage, r4.lead1.current, r4.lead2.voltage, r4.lead2.current,
                   w.lead1.voltage, w.lead1.current, w.lead2.voltage, w.lead2.current      ]  """)
                   
        assert self.unwrap(space, w_res) == [0.0, 0.05, 5.0, -0.05, 5.0,
                                             0.0, 0.0,
                                             5.0, 0.025, 2.5, -0.025, 
                                             5.0, 0.025, 2.5, -0.025, 
                                             2.5, 0.025, 0, -0.025, 
                                             2.5, 0.025, 0, -0.025, 
                                             2.5, 0.0, 2.5, 0.0]



