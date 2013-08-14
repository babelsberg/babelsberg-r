require "libcassowary"
require "libarraysolver"

class Array
  def ensure_blocks
    (@ensure_blocks ||= []).tap { |b| b.uniq! }
  end

  def sum
    return 0 if empty?
    self[0] + self[1..-1].sum
  end

  def upto(item)
    self[0..(self.index(item) || -1)]
  end

  def rows
    # just for readability. if timeSeries were a database series, the
    # rows would be created on demand, i.e., when we call rows
    self
  end

  # just for readability
  alias each_row each

  def ensure(&block)
    ensure_blocks << block
    run_ensure(block)
  end

  def run_ensure(blk)
    self.each do |item|
      always do
        blk[item]
      end
    end
  end

  alias push_wo_ensure push
  def push(*args)
    r = push_wo_ensure(*args)
    self.sort_by!(&:ddate)
    r
  end

  def map_sum(symbol)
    return 0 if empty?
    self[0].send(symbol).? + self[1..-1].map_sum(symbol)
  end
end

def try_add(series, row)
  series.push(row)
  true
rescue Exception => e
  p e
  false
ensure
  series.pop if series.last.equal?(row)
end

class ScheduledItem
  attr_accessor :ddate, :qty
  def initialize(ddate, qty)
    self.ddate = ddate.to_int
    self.qty = qty.to_int
  end

  def inspect
    "#{ddate}: #{qty}"
  end
end

def candidates(timeSeries, scheduleLines)
  scheduleLines.sort_by(&:ddate).each_row.select do |row|
    try_add(timeSeries, row)
  end
end

series = [ScheduledItem.new(0, 10000),
          ScheduledItem.new(10, -2000),
          ScheduledItem.new(15, -2000),
          ScheduledItem.new(25, -6000)]

always { series.map_sum(:qty) >= 0 }

p series
p int = candidates(series, [ScheduledItem.new(5, 1000)])
p series
p out = candidates(series, [ScheduledItem.new(5, -1000)])
p series
p out = candidates(series, [ScheduledItem.new(5, -1000)])
p series
