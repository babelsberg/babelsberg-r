from rpython.rlib import jit

from topaz.objects.objectobject import W_Root
from topaz.objects.intobject import W_FixnumObject, W_MutableFixnumObject


class BaseCell(W_Root):
    pass


class LocalCell(BaseCell):
    def get(self, space, frame, pos):
        return frame.localsstack_w[pos]

    def set(self, space, frame, pos, w_value):
        frame.localsstack_w[pos] = w_value

    def upgrade_to_closure(self, space, frame, pos):
        w_obj = self.get(space, frame, pos)
        if isinstance(w_obj, W_FixnumObject):
            frame.cells[pos] = result = IntCell(space.int_w(w_obj))
        else:
            frame.cells[pos] = result = ClosureCell(w_obj)
        return result

    def get_constraint(self):
        return None

    def set_constraint(self, w_value):
        raise RuntimeError("Local cells should not have constraints")


class ClosureCell(BaseCell):
    def __init__(self, w_value):
        self.w_value = w_value
        self.w_constraint = None

    def get(self, space, frame, pos):
        return self.w_value

    def set(self, space, frame, pos, w_value):
        self.w_value = w_value

    def upgrade_to_closure(self, space, frame, pos):
        return self

    def get_constraint(self):
        return jit.promote(self.w_constraint)

    def set_constraint(self, w_value):
        self.w_constraint = w_value


class IntCell(ClosureCell):
    def __init__(self, intvalue):
        ClosureCell.__init__(self, W_MutableFixnumObject(None, intvalue))

    def set(self, space, frame, pos, w_value):
        if isinstance(w_value, W_FixnumObject) and isinstance(self.w_value, W_FixnumObject):
            self.w_value.set_intvalue(w_value.intvalue)
        else:
            ClosureCell.set(self, space, frame, pos, w_value)

    def get(self, space, frame, pos):
        w_value = self.w_value
        if isinstance(w_value, W_MutableFixnumObject):
            return space.newint(space.int_w(w_value))
        else:
            return w_value
