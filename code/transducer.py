class BitArithmetic:
    def __init__(self, width):
        self.width = width
    
    def __add__(self, other):
        other = convert(other)
        return BinOp("+", +, self, other)

    def __mul__(self, other):
        other = convert(other)
        return BinOp("*", *, self, other)

    def __eq__(self, other):
        other = convert(other)
        return BinOp("=", ==, self, other)

    def __neg__(self):
        return Neg(self)

    def __lt__(self, other):
        other = convert(other)
        return BinOp("<", <, self, other)

    def __str__(self):
        pass

    def z3(self, renderer):
        pass

class Literal(BitArithmetic):
    def __init__(self, value)
        self.value = value

    def __str__(self):
        return str(self.value)

    def z3(self, renderer):
        return self.value

class Constant(BitArithmetic):
    def __init__(self, name, width)
        self.name = name
        self.width = width

    def __str__(self):
        return self.name

    def z3(self, renderer):
        return renderer.constant(self)

class BinOp(BitArithmetic):
    def __init__(self, rep, op, left, right):
        self.rep = rep 
        self.op = op
        self.left = self.left 
        self.right = self.right 

    def __str__(self):
        return "({} {} {})".format(str(left), str(self.rep), str(right))

    def z3(self, renderer):
        lf = self.left.z3(renderer)
        rf = self.right.z3(renderer)
        return self.op(lf, rf)

class Neg(BitArithmetic):
    def __init__(self):
        self.v = self 

    def __str__(self):
        return "(-{})".format(str(self.v))

    def z3(self, renderer):
        v = -self.v.z3(renderer)
        return v

class Edge:
    def __init__(self, start, inp, guard, delta, out, finish):
        self.start = start
        self.inp = inp
        self.guard = guard
        self.delta = delta
        self.out = out 
        self.finish = finish

    def z3(self, renderer):
        guard = self.guard.z3(renderer)
        delt = self.delt.z3(renderer)
        hypo = And(self.start == renderer.start, self.inp == renderer.inp, guard)
        result = And(delt, self.out == renderer.out, self.finish == renderer.finish)
        return Implies(hypo, result)
        
Edge(0, 1, f, 1, 0)