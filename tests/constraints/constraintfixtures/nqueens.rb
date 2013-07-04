# puts "The eight queens puzzle is the problem of placing eight chess"
# puts "queens on an 8x8 chessboard so that no two queens attack each"
# puts "other. Thus, a solution requires that no two queens share the"
# puts "same row, column, or diagonal."

require "libz3"

class EightQueens
  class Queen
    attr_accessor :row, :column

    def initialize(row, column)
      self.row = row
      self.column = column
      always do
        self.row >= 0 && self.row <= 7 &&
          self.column >= 0 && self.column <= 7
      end
    end

    def diagonal
      row - column - 1
    end

    def inspect
      "#<Queen: #{row}x#{column}>"
    end
  end

  attr_reader :queens

  def initialize
    @queens = 8.times.map do
      Queen.new(0, 0)
    end

    @queens.each do |queen1|
      @queens.each do |queen2|
        if queen1 != queen2
          always do
            queen1.row != queen2.row &&
              queen1.column != queen2.column &&
              queen1.diagonal != queen2.diagonal
          end
        end
      end
    end
  end

  def inspect
    @queens.inspect
  end
end

q = EightQueens.new
q.queens.each do |queen|
  q.queens.each do |other|
    unless queen == other
      raise "Wrong solution" if queen.row == other.row || queen.column == other.column || queen.diagonal == other.diagonal
    end
  end
end
puts "Right solution"
