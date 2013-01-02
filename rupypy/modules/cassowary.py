from rupypy.module import Module, ModuleDef


class Cassowary(Module):
    moduledef = ModuleDef("Cassowary", filepath=__file__)

    @classdef.setup_class
    def setup_class(cls, space, w_cls):
        p = os.path.join(os.path.dirname(__file__), os.path.pardir, "kernel/libcassowary.rb")
        f = open_file_as_stream(p)
        try:
            contents = f.readall()
        finally:
            f.close()
        self.execute(contents, filepath=p)
