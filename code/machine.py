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
        '''
        Creates a copy with a prefix
        '''
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
        self.examples = []

    def connect(self, pre : TimeSlice, post : TimeSlice):
        '''
        an edge checks to see if there exists an interpretation of 
        - the input
        - the starting node
        - the target node
        - the output
        - the initial and final values of the registers
        such that they match with its own logic, and the logic of progressing from one time slice to the next,
        thus the starting node should be the node at a time slice,
        and the target node should be the node at the next time slice,
        and that the input/output should be correct
        this also ensures that the registers make sense

        pre is the time slice under question
        post is the next time slice
        '''

        # make sure that the register's final value for pre is its initial value in post
        reg_next_cnxn = And(*[prer.o == postr.i for prer, postr in zip(pre.r, post.r)])

        # make sure that for that registers int he machines logic get interpreted as pre's registers
        reg_curr_cnxn = And(*[And(curr.o == m.o, curr.i == m.i) for curr, m in zip(pre.r, self.r)])

        in_reg = [r.i for r in self.r]
        out_reg = [r.o for r in self.r]

        return Exists([self.i, self.f, self.t, self.o, *in_reg, *out_reg], And(self.machine_logic(), self.i == pre.i, self.f == pre.s, self.t == post.s, self.o == pre.o, reg_curr_cnxn, reg_next_cnxn))

    def add_register(self, name, width):
        '''
        adds a register to the machine, of name and width, and returns an uniterpreted variable to it
        '''
        register = Register(name, width)
        self.r.append(register)
        return register

    def add_edge(self, frm, guard, delta, target):
        '''
        add an uinterpreted edge such if the starting node is some value,
        and the uninterpreted guard is valid,
        then it is implied that the guard is true and that delta transformation happens
        '''
        hypo = And(self.f == frm, guard)
        self.guards.append(hypo)
        result = And(self.t == target, delta)
        edge = Implies(hypo, result)
        self.edges.append(edge)

    def add_example(self, inp, out):
        self.examples.append((inp, out))

    def duplicate_registers(self, prefix):
        '''
        for each time slice it is useful to make a copy of all registers,
        here is it done, with some prefix used to properly name those copies
        '''
        return [r.duplicate(prefix) for r in self.r]

    def clear(self):
        '''
        we preserve the state and register structure,
        but we wipe the edge information.
        This is useful for synthesis of edge values where edges will change but the rest of the machine will not
        '''
        self.edges = []
        self.guards = []

    def machine_logic(self):
        '''
        This does two things:
        first it makes sure that if none of edge hypothesies pass that machine fails (thus not hypos)
        second, it conjoins all of the logic
        '''
        notOther = Not(And(*self.guards))
        return And(notOther, *self.edges) 

    def example_logic(self, inp, out):
        '''
        For some example:
        we create an expression which evaluates to truth value of whether the input, under the machine, would create the right output
        it has four steps:
        - first i creates a time slice for each input character (thus also each output character)
        - then it sets all the uninterpreted input characters and output characters to the given values
        - then it connects time slices i and i +1 as described in more detail in that function
        - finally it sets the initial values of the start state and registers
        '''
        if len(inp) != len(out): return None
        length = len(inp)
        slices = [TimeSlice(t, self.state_width, self.input_width, self.output_width, self.duplicate_registers(str(t))) for t in range(length)]

        comms = [And(slices[i].i == inp[i], slices[i].o == out[i]) for i in range(length)]

        cnxns  = [self.connect(slices[i], slices[i+1]) for i in range(length-1)] # 1 less than length as there is no connection from the last time slice

        start = slices[0].s == 0
        reg = slices[0].r[0].i == 1 # TODO this should be setting all register start values
        return And(And(*comms), And(*cnxns), start, reg) 

    def formula(self):
        '''
        After having all the examples, we can judge whether a machine correctly takes all inputs to all outputs
        '''
        return And(*[self.example_logic(inp, out) for inp, out in self.examples])

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

