Babelsberg/R
============

A [Topaz](http://www.topazruby.com)-based implementation of Babelsberg

See also [Babelsberg/JS](https://github.com/timfel/babelsberg-js)

It allows you to solve, for example, the send+more=money puzzle like this:
```ruby
require "libz3"
require "libarraysolver"

class Array
  def ins(range)
    return true if self.empty?
    self[1..-1].ins(range) &&
      self[0] >= range.first &&
      self[0] <= range.last
  end
end

# initialize each variable to an integer so that the solver knows its type
s,e,n,d,m,o,r,y = [0]*8

# each digit is between 0 and 9
always { [s,e,n,d,m,o,r,y].ins(0..9) } 
# all digits
always { [s,e,n,d,m,o,r,y].alldifferent? }

always do
            s*1000 + e*100 + n*10 + d +
            m*1000 + o*100 + r*10 + e ==
  m*10000 + o*1000 + n*100 + e*10 + y
end

# the leading digits can't be 0
always { s > 0 }
always { m > 0 }

puts ("solution: [s,e,n,d,m,o,r,y] = " + [s,e,n,d,m,o,r,y].to_s)
```

But it is also dynamic, so you can do:
```ruby
require "libcassowary"
require "iosolver" # not included in standard library

class VideoEncoder
  attr_accessor :quality
  def initialize(settings_file)
    quality_setting = FloatRWIO.new(settings_file)
    always { self.quality > 0 && self.quality < 100 }
    always { self.quality == quality_setting }
    # ...
  end

  # ... rest of the impl
end

settings_file = File.open("./settings", "w")
settings_file << 50
e = VideoEncoder.new(settings_file)
puts e.quality # 50

settings_file.rewind
settings_file << 25
puts e.quality # 25

settings_file.rewind
settings_file << 0
puts e.quality # 1 -- the constraint requires quality to be >0
settings_file.rewind
puts settings_file.read # 1 -- the constraint is bi-directional, so the file was updated
```

Basically, you can write constraints using the `always` primitive that you always want to be true,
using existing object-oriented abstractions (I am just using the accessor method for `quality` above),
and the system will maintain them. The extent to which the system is able to keep constraints
satisfied depends on the solver that is used. This implementation provides Z3, DeltaBlue, and
Cassowary.

We have used this to implement electrical simulations, a video streaming application,
puzzle solvers, and a simulation of the Lively Engine.

Papers about this implementation are forthcoming and a freely accessible technical report
will be published shortly.
