from topaz.objects.objectobject import W_Root


class BaseCell(W_Root):
    pass


class LocalCell(BaseCell):
    def get(self, frame, pos):
        return frame.localsstack_w[pos]

    get_prev = get

    def set(self, frame, pos, w_value):
        frame.localsstack_w[pos] = w_value

    def advance_time(self, frame, pos):
        pass

    def upgrade_to_closure(self, frame, pos):
        frame.cells[pos] = result = ClosureCell(self.get(frame, pos), None)
        return result

    def get_constraint(self):
        return None

    def set_constraint(self, w_value):
        raise RuntimeError("Local cells should not have constraints")


class ClosureCell(BaseCell):
    def __init__(self, w_value, w_prev = None):
        self.w_value = [w_value, w_prev]
        self.w_constraint = None

    def get(self, frame, pos):
        return self.w_value[0]

    def get_prev(self, frame, pos):
        return self.w_value[1]

    def set(self, frame, pos, w_value):
        self.w_value[0] = w_value

    def advance_time(self, frame, pos):
        self.w_value[1] = self.w_value[0]

    def upgrade_to_closure(self, frame, pos):
        return self

    def get_constraint(self):
        return self.w_constraint

    def set_constraint(self, w_value):
        self.w_constraint = w_value
