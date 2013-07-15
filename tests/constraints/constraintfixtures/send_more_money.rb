require "libz3"
require "libarraysolver"

@alphabet = [0] * 26
always { @alphabet.alldifferent? }

def w(string)
  # first letter cannot be 0
  always { @alphabet[string.downcase[0].ord - ?a.ord] > 0 }

  letters = string.downcase.each_char.each_with_index.map do |c, idx|
    off = c.ord - ?a.ord
    always { @alphabet[off] >= 0 && @alphabet[off] <= 9 }
    @alphabet[off] * (10 ** (string.size - idx - 1))
  end
  letters.inject(0) { |memo, letter| letter + memo }
end

w('send')
w('more')
w('money')
always do
  w('send') + w('more') == w('money')
end

numbers = 'sendmory'.each_char.map do |c|
  @alphabet[c.ord - ?a.ord]
end

raise unless numbers.alldifferent?
raise if w('send') + w('more') != w('money')
puts "Working solution"
