class Z3_renderer:
    def __init__(self):
        self.constants = {}

    def constant(self, cons):
        if not (cons in self.constants):
            self.constants[cons] = BitVec(cons.name, cons.width)
        return self.constants[cons]
            