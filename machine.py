from z3 import *
import math

def width(max):
    if max <= 1: 
        return 1
    else:
        return math.ceil(math.log2(max))

class TimeSlice:
    def __init__(self, time, state_width, input_width, output_width, registers):
        time_str = str(time)
        self.i = BitVec("input_{}".format(time_str), input_width)
        self.s = BitVec("state_{}".format(time_str), state_width)
        self.o = BitVec("output_{}".format(time_str), output_width)
        self.r = registers

class Register:
    def __init__(self, name, width):
        self.name = name 
        self.width = width
        self.i = BitVec("{}_in".format(name), width)
        self.o = BitVec("{}_out".format(name), width)

    def duplicate(self, prefix):
        return Register("{}:{}".format(prefix, self.name), self.width)

class Machine:
    def __init__(self, nstates, ninputs, nouputs):
        self.state_width = width(nstates)
        self.input_width = width(ninputs)
        self.output_width = width(nouputs)
        self.i = BitVec("input", self.input_width)
        self.f = BitVec("from", self.state_width)
        self.t = BitVec("target", self.state_width)
        self.o = BitVec("output", self.output_width)
        self.r = []
        self.guards = []
        self.edges = []

    def connect(self, pre : TimeSlice, post : TimeSlice):
        # first create connections between registers
        reg_next_cnxn = And(*[prer.o == postr.i for prer, postr in zip(pre.r, post.r)])
        reg_curr_cnxn = And(*[And(curr.o == m.o, curr.i == m.i) for curr, m in zip(pre.r, self.r)])
        in_reg = [r.i for r in self.r]
        out_reg = [r.o for r in self.r]
        return Exists([self.i, self.f, self.t, self.o, *in_reg, *out_reg], And(self.logic(), self.i == pre.i, self.f == pre.s, self.t == post.s, self.o == pre.o, reg_curr_cnxn, reg_next_cnxn))

    def add_register(self, name, width):
        register = Register(name, width)
        self.r.append(register)
        return register

    def add_edge(self, frm, guard, delta, target):
        hypo = And(self.f == frm, guard)
        self.guards.append(hypo)
        result = And(self.t == target, delta)
        edge = Implies(hypo, result)
        self.edges.append(edge)

    def logic(self):
        notOther = Not(And(*self.guards))
        return And(notOther, *self.edges) 

    def clear(self):
        self.edges = []

    def duplicate_registers(self, prefix):
        return [r.duplicate(prefix) for r in self.r]

    def example(self, inp, out):
        if len(inp) != len(out): return None
        length = len(inp)
        slices = [TimeSlice(t, self.state_width, self.input_width, self.output_width, self.duplicate_registers(str(t))) for t in range(length)]
        comms = [And(slices[i].i == inp[i], slices[i].o == out[i]) for i in range(length)]
        cnxns  = [self.connect(slices[i], slices[i+1]) for i in range(length-1)] # 1 less than length as there is no connection from the last time slice
        start = slices[0].s == 0
        reg = slices[0].r[0].i == 1
        return And(And(*comms), And(*cnxns), start, reg) 

def synthesize(depth, base):
    items = [base]
    for i in range(depth):
        generation = []
        for right in items[-1]:
            for item in items:
                for left in item:
                    generation.append(left + right)
                    generation.append(left * right)
        items.append(generation)
    for item in items:
        for elem in item:
            yield elem

"""
we want to synthesize some r such that the machine m agrees to the trace ([0, 0, 0, 0], [0, 0, 1, 0])
where v is a register and the machine starts at state zero and proceeds:
(0, in == 1, v = r /\ out == 0, 0)
(0, in == 0, v = r /\ out == 1, 0)

we synthesise through a simple grammar of linear arithmetic:
    expr -> expr + expr | expr * expr | - expr | v | c
    c is just a bit vector variable
"""
c = BitVec("c", 2)
m = Machine(1, 2, 2)
v = m.add_register("v", 2)
for r in synthesize(2, [v.i, c]):
    m.add_edge(0, v.i != 3, And(v.o == r, m.o == 0), 0)
    m.add_edge(0, v.i == 3, And(v.o == r, m.o == 1), 0)
    f = m.example([0, 0, 0, 0], [0, 0, 1, 0])
    s = Solver()
    s.add(f)
    if unsat != s.check():
        print(r)
        print(s.model())
        break
    m.clear()
