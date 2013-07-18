# Alternate version of send+more=money cryptarithmetic puzzle.
# In this version we use separate variables for s,e,n etc.
# This is attempting to follow the code in the SWI Prolog manual:
#  http://www.swi-prolog.org/man/clpfd.html


require "libz3"
require "libarraysolver"

# constrain each element of the array to be in the provided range
class Array
  def ins(range)
    return true if self.empty?
    self[1..-1].ins(range) &&
      self[0] >= range.first &&
      self[0] <= range.last
  end
end

s,e,n,d,m,o,r,y = [0]*8
always { [s,e,n,d,m,o,r,y].alldifferent? }

always {   s*1000 + e*100 + n*10 + d +
           m*1000 + o*100 + r*10 + e ==
 m*10000 + o*1000 + n*100 + e*10 + y }

always { [s,e,n,d,m,o,r,y].ins(0..9) } 

puts ("solution: [s,e,n,d,m,o,r,y] = " + [s,e,n,d,m,o,r,y].to_s)
