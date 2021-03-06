# This file loads all the ruby kernel code in its directory

lib_topaz = File.dirname(__FILE__)
load_bootstrap = proc do |file|
  load(File.join(lib_topaz, file))
end

load_bootstrap.call("topaz.rb")
load_bootstrap.call("array.rb")
load_bootstrap.call("class.rb")
load_bootstrap.call("comparable.rb")
load_bootstrap.call("dir.rb")
load_bootstrap.call("enumerable.rb")
load_bootstrap.call("enumerator.rb")
load_bootstrap.call("env.rb")
load_bootstrap.call("errno.rb")
load_bootstrap.call("file.rb")
load_bootstrap.call("fixnum.rb")
load_bootstrap.call("hash.rb")
load_bootstrap.call("integer.rb")
load_bootstrap.call("io.rb")
load_bootstrap.call("kernel.rb")
load_bootstrap.call("matchdata.rb")
load_bootstrap.call("numeric.rb")
load_bootstrap.call("process.rb")
load_bootstrap.call("range.rb")
load_bootstrap.call("random.rb")
load_bootstrap.call("regexp.rb")
load_bootstrap.call("string.rb")
load_bootstrap.call("struct.rb")
load_bootstrap.call("symbol.rb")
load_bootstrap.call("thread.rb")
load_bootstrap.call("time.rb")
load_bootstrap.call("top_self.rb")
load_bootstrap.call("method.rb")
load_bootstrap.call("rational.rb")
load_bootstrap.call("file_test.rb")

load_bootstrap.call("constraint_variable.rb")
load_bootstrap.call("constraint.rb")

# ffi
load_bootstrap.call("ffitopaz/pointer.rb")
load_bootstrap.call("ffitopaz/errors.rb")
load_bootstrap.call("ffitopaz/ffi.rb")
