from rupypy.objects.objectobject import W_Root


class BaseCell(W_Root):
    pass


class LocalCell(BaseCell):
    def get(self, frame, pos):
        stackpos = frame.localsstack_w[pos]
        if stackpos is not None:
            return frame.localsstack_w[pos][0]
        else:
            return None

    def get_prev(self, frame, pos):
        stackpos = frame.localsstack_w[pos]
        if stackpos is not None:
            return frame.localsstack_w[pos][1]
        else:
            return None

    def set(self, frame, pos, w_value):
        if frame.localsstack_w[pos] is not None:
            frame.localsstack_w[pos][0] = w_value
        else:
            frame.localsstack_w[pos] = [w_value, None]

    def advance_time(self, frame, pos):
        if frame.localsstack_w[pos] is not None:
            frame.localsstack_w[pos][1] = frame.localsstack_w[pos][0]

    def upgrade_to_closure(self, frame, pos):
        frame.cells[pos] = result = ClosureCell(self.get(frame, pos), self.get_prev(frame, pos))
        return result


class ClosureCell(BaseCell):
    def __init__(self, w_value, w_prev = None):
        self.w_value = [w_value, w_prev]

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
