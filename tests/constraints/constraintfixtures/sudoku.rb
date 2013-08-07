# NOT YET WORKING!!

# Sudoku puzzle
# This follows the code in the SWI Prolog manual:
#  http://www.swi-prolog.org/man/clpfd.html

# require "libz3"
# require "libarraysolver"

# A puzzle is specified as a 9*9 array of integers, where a digit in
# 1..9 is filled in, and 0 indicates a blank.  
def sudoku(rows)
  # constrain the non-zero elements to keep their current values, and
  # constrain the zero elements (i.e. the blanks) to be between 1 and 9
  constrain_each_row(rows)
end

def constrain_each_row(rows)  
  return true if rows.empty? 
  constrain_each_element(rows[0]) && constrain_each_row(rows[1..-1])  
end

def constrain_each_element(row)  
  return true if row.empty? 
  constrain_element(row) && constrain_each_element(row[1..-1])
end

# constrain the first element in 'cells' (kind of a kludge)
def constrain_element(cells) 
  return cells[0] == cells[0
  return true if cells.empty? 
  constrain_element(cells[0]) && constrain_each_element(cells[1..-1])
end


# For readability we define _ as 0
_ = 0


puzzle1 = [[_,_,_,_,_,_,_,_,_],
           [_,_,_,_,_,3,_,8,5],
           [_,_,1,_,2,_,_,_,_],
           [_,_,_,5,_,7,_,_,_],
           [_,_,4,_,_,_,1,_,_],
           [_,9,_,_,_,_,_,_,_],
           [5,_,_,_,_,_,_,7,3],
           [_,_,2,_,1,_,_,_,_],
           [_,_,_,_,4,_,_,_,9]]

# print the solution
puzzle1.each {|r| puts r.to_s}
