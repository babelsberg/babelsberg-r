# -*- coding: utf-8 -*-
# class A
#   BAR = 1
#   def self.bar
#     puts BAR
#   end
# end
# A.bar

# module A
#   puts Object.constants
# end

# class A < Numeric
#   def to_i; 1; end
# end
# puts A.new.to_int

# puts [1, 2, 3].map(&:to_s)
# puts [1.send(:to_s), 1.send('+', 2)]
# puts [1, 1, 2, '3'] - [1, '3']
# puts [1, '1'] - [1, '1']

# raise nil
# TypeError.new

# puts File.new("/tmp/nsemail.eml")

# a = "hi"
# puts a
# a.clear
# puts a

# DATA = "LOCAL"
# puts DATA.read()
# __END__

# blah blah blah, this is not parsed

# if 1
#   then
#   1
# end

# $"
# $!

# @@class_var
# module M
# end

# class M::A
#   MYCONST = "a"
#   @@foo = "a"

#   def initialize
#     @foo = "a"
#   end

#   def get
#     [@foo,
#      @@foo,
#      MYCONST]
#   end
# end

# class M::B < M::A
#   MYCONST = "b"
#   @@foo = "b"

#   def initialize
#     @foo = "b"
#   end
# end

# puts M::B.new.get
# puts M::A.new.get

# class A; end
# class B < A; @@foo = "b"; end
# class C < A; @@foo = "c"; end
# class B < A; puts @@foo; end
# class C < A; puts @@foo; end
# class A; @@foo = "a"; end
# class A; puts @@foo; end
# class B < A; puts @@foo; end
# class C < A; puts @@foo; end

# class B < A
#   def get
#     @@foo
#   end
# end

# puts B.new.get

# class A
#   def self.get
#     @@foo
#   end
#   def get
#     @@foo
#   end
#   @@foo = 'a'
# end

# class B < A
#   def self.get
#     @@foo
#   end
#   def get
#     @@foo
#   end
# end

# # puts [A.get, A.new.get, B.get]
# B.get

# class A
#   @foo = 1
#   puts @foo
# end

# class B
#   puts @foo
# end

# class A
#   puts @foo
# end

# puts 1
# class A; end
# class B < A
#   @@foo = "B"
#   def get; @@foo; end
# end
# class C < A
#   @@foo = "C"
#   def get; @@foo; end
# end
# puts [B.object_id, C.object_id]
# in_subclasses = [B.new.get, C.new.get]

# class A; @@foo = "A overrides all"; end
# puts in_subclasses + [B.new.get, C.new.get]

# a = 1
# class Fixnum
#   def set
#     @foo = "A"
#   end
#   def get
#     @foo
#   end
# end
# a.set

# # b = 1
# # puts b.get
# class A
#   def self.get()
#     puts 1
#   end
# end
# class B < A; end
# # puts B.singleton_class.ancestors
# B.get
# Exception
# File
# puts Object.constants
# puts Exception.constants
# puts File.constants
# # Object::FOO
# # Object.const_missing :FOO

# class A
#   def method_missing(name, *args, &block)
#     puts name
#     puts args
#     puts block
#   end
# end

# A.new.foo('blah', 2)

# OPT_TABLE = {}
# OPT_TABLE["a"] = "b"

# puts $LOADED_FEATURES
# require "test_req"
# puts $LOADED_FEATURES

# class A
#   CONST = 5
#   def self.m
#     CONST
#   end
# end

# puts A.m

# __LINE__ = 1
# puts __LINE__

# private
# def f(*a)
#   puts "hi"
# end

# f "hello", "world"

# puts "\w"
# puts /\w/

# def f(h, *a)
#   h
# end

# puts f "hello", "world"

# foo = "foo"
# a = <<EOF
# def #{foo}(*args)
#   super(*fu_update_option(args, :verbose => true))
# end
# EOF
# puts a

# puts ENV
# puts Topaz::EnvironmentVariables
# class Foo
#   def self.c
#     @config ||= 'a'
#   end
# end
# Foo.c

# puts [1,2,3].pop(2)
# puts "abc"[1]

# h = {}
# h[:option] = 1
# puts h[:option]

# puts "\012" == "\n"
# puts "\0" == "\x0"
# ?\012

# puts "\342\234\224" == "✔"

# def broken
#   each {
#     saved_env = 1
#     each { saved_env }
#     each { saved_env }
#   }
# end

# if nil
#   puts "shouldn't print"
# elsif nil
#   puts "shouldn't print"
# else
#   puts "should print"
# end

# self.each do end

# a = [1]
# a[1] = 2
# puts a[0, -1]
# [][0..-2]

# begin
#   Process.exit(1)
# rescue SystemExit => e
#   puts e.success?
#   puts e.status
# end
# Process.exit(1)

# puts Dir.home

# exec(["/usr/bin/du", "du"], "-s")

# at_exit do
# end

# [65] * 3

# "now's  the time".split(/ /)

# puts [65].pack("C")

# class A
#   CONST = "a"
#   def get
#     CONST
#   end
# end

# class B < A
#   CONST = "b"
# end

# puts A.new.get == B.new.get # => should return true

# class X
#   class Y
#   end
# end

# class A < X
#   module M; end

#   include M

#   puts Y.object_id
#   class Y < X::Y
#     puts self.object_id
#     include M
#   end
#   puts Y.object_id
# end

# require 'pp'
# puts $>
# puts $stdout
# pp false
# pp true
# pp 1
# pp Kernel
# pp Symbol
# pp []
# pp (1..2)
# pp({"1" => "2"})
# Thread.current["a"]

# class Bar
#   module M
#   end
# end

# class Y
#   FRIZZ = 1
# end

# class X < Y
#   module M
#     FOO = 5
#   end

#   class Foo < Bar
#     def f
#       M::FOO
#     end
#   end
# end

# class X::Foo
#   def g
#     M::FOO
#   end
# end

# puts X::Foo.new.f
# puts X::Foo.new.g


# for i in []; end
# puts i

# i = 5
# puts i
# for i in [1] do
#   bbb = "hello"
#   puts bbb
# end
# puts bbb
# puts i

# j = 5
# puts j
# [1].each {|j| puts j }
# puts j

# i = 0
# for i, *rest, b in [1, 2, 3] do
#   bbb = "hello"
# end
# puts i.inspect, rest.inspect, b.inspect, bbb.inspect

# puts ([1,2,3].each {|i, *b| puts i.inspect, b.inspect }).inspect

# class A
#   def hello
#   end
#   undef_method :hello
# end
# A.new.hello

# a = []
# i = 0
# for a[i], i in [[1, 1], [2, 2]]; end
# puts a, i

# def foo(&block)
#   for block, in [[1, 1], [2, 2]]; end
#   block
# end

# puts foo

# foo = 1
# puts defined? foo

# a = 1

# puts defined?(foo.bar),
#      defined?(a)
# puts defined?(Foo::FAS),
#      defined?(Object)
# puts defined?($aaa),
#      defined?($")
# puts defined?(a = 1)
# puts defined?(x[y]),
#      defined?([]),
#      defined?([][1])
# puts defined?({}),
#      defined?({a: 2}[:a])
# puts defined?(for i in a; puts 1; end)
# puts defined?(Object.new(b))
# puts defined?(Object.new(1))

# class A
#   def each
#     [1, 2, 3]
#   end
# end
# puts defined? i
# for i in A.new; end
# puts defined? i
# puts i

# for a in []; end
# puts defined?(a)
# a = 1
# puts defined?(a)

# for Const in []; end; puts Const

# 2 ** 'hallo'

# instance_eval("")

# puts `echo 1`
# a = "a"
# a.freeze
# a.taint

# puts 'hello'.gsub("he", "ha")
# puts 'hello'.gsub(/(.)/, "ha")
# puts 'hello'.gsub(/(.)/, "ha\\1ho")
# puts 'hello'.gsub(/(.)/) { |e| e + "1" }

# puts "hello\n".chomp

# load "fileutils"
# puts FileUtils
# puts $LOADED_FEATURES

# def []=(idx, value)
#   @foo = [idx, value]
# end

# def [](idx)
#   @foo
# end

# self[1] = 2
# self[1]
# puts @foo

# replacements = [1, 2]
# puts 'helloo'.gsub("l", Hash.new { |h, k| replacements.pop() })

# puts a

# a = Cassowary::Variable.new name: 'a', value: 1
# b = Cassowary::Variable.new name: 'b', value: 1
# s = Cassowary::SimplexSolver.new
# s.add_constraint a + b == 1
# puts a.value
# puts b.value


require File.expand_path("../lib-ruby/libcassowary.rb", __FILE__)

# def always(constraint)
#   constraint
# end

a = @a = @@b = 2
puts a, @a, @@b
constrain { a + @@b == 10 }
puts a, @a, @@b
constrain { @@b == @a * 2 }
puts a, @a, @@b
constrain { @a > 1 }
puts a, @a, @@b
constrain { @a == 5 }
puts a, @a, @@b


class Point
  def x
    @x
  end

  def y
    @y
  end

  def initialize(x, y)
    @x = x
    @y = y
    constrain { @x >= 0 }
    constrain { @y >= 0 }
    constrain { @x < 640 }
    constrain { @y < 480 }
  end

  def to_s
    "#{@x}@#{@y}"
  end
  alias inspect to_s
end

pt1 = Point.new(-1, 10)
pt2 = Point.new(20, 20)
puts pt1
puts pt2
constrain { pt1.x == pt2.x }
puts pt1
puts pt2
constrain { pt1.x == 5 }
puts pt1
puts pt2

class HorizontalLine
  def start
    @start
  end

  def end
    @end
  end

  def initialize(pt1, pt2)
    @start = pt1
    @end = pt2
    constrain { pt1.y == pt2.y }
  end

  def length
    @end.x - @start.x
  end

  def to_s
    "#{@start.inspect}->#{@end.inspect}"
  end
  alias inspect to_s
end

h = HorizontalLine.new(Point.new(1, 1), Point.new(2, 2))
puts h, h.length
constrain { h.length >= 100 }
puts h, h.length
