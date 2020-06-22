from z3 import *
from lark import Lark, Transformer

def width(max):
    if max <= 1: 
        return 1
    else:
        return math.ceil(math.log2(max))

parser = Lark(r"""

transducer: "transducer" CNAME "{" edges "}"

edges: [edge*]
edge: CNAME "/" CNAME "/" boolexpr "/" assigns "/" CNAME "/" CNAME ";"

boolexpr: boolexpr "&&" boolexpr -> and
    | boolexpr "||" boolexpr -> or
    | "!" boolexpr -> not
    | arithexpr "==" arithexpr -> eq
    | arithexpr "!=" arithexpr -> neq
    | arithexpr ">=" arithexpr -> gte
    | arithexpr ">" arithexpr -> gt
    | arithexpr "<=" arithexpr -> lte
    | arithexpr "<" arithexpr -> lt
    | "?" string -> boolhole

arithexpr: arithexpr "+" arithexpr -> plus
    | arithexpr "*" arithexpr -> mul
    | "-" arithexpr  -> neg
    | "$" CNAME -> register
    | "?" CNAME -> arithhole
    | CNAME -> var
    | SIGNED_NUMBER -> lit

assigns: [assign*]
guard: boolexpr
assign: CNAME "<-" arithexpr ";"
string: CNAME

%ignore WS
%import common.WS
%import common.CNAME
%import common.SIGNED_NUMBER
""", start='transducer')

result = parser.parse("""
transducer s0 {
    s0 / z / $v != 3 / v <- $v+1; / z / s0;
    s0 / z / $v == 3 / v <- $v+g; / y / s0;
}
""")

class TreeToSketch(Transformer):
    def __init__(self):
        self.nstates = 1
        self.ninputs = 1
        self.noutputs = 2
        self.width = 4
        self.start = None
        self.vars = {}
        self.registers = {}
        self.state = {}
        self.inputs = {}
        self.outputs = {}
        self.next_state = 0
        self.next_input = 0
        self.next_output = 0
        self.input = BitVec("i", width(self.ninputs))
        self.output = BitVec("o", width(self.noutputs))
        self.out = BitVec("out", width(self.nstates))
        self.to = BitVec("to", width(self.nstates))

    def _check_register(self, s):
        if s not in self.registers:
            self.registers[s] = (BitVec(s, self.width), BitVec(s, self.width))

    def get_input(self, s):
        if s not in self.inputs:
            self.inputs[s] = self.next_input
            self.next_input += 1 
        return self.inputs[s]

    def get_output(self, s):
        if s not in self.outputs:
            self.outputs[s] = self.next_output
            self.next_output += 1 
        return self.outputs[s]

    def get_state(self, s):
        if s not in self.state:
            self.state[s] = self.next_state 
            self.next_state += 1 
        return self.state[s]

    def read_register(self, s):
        self._check_register(s)
        return self.registers[s][0]

    def write_register(self, s):
        self._check_register(s)
        return self.registers[s][1]

    def examples(self, args):
        return args

    def example(self, args):
        length = int(len(args)/2)
        examples = list(map(lambda x: x[0], args))
        return (examples[:length], examples[length:])

    def transducer(self, args):
        return (args[0][0], args[1])

    def edges(self, args):
        return And(*args)

    def edge(self, args):
        hypo = And(self.out == self.get_state(args[0]), self.input == self.get_input(args[1]), args[2])
        resu = And(args[3], self.output == self.get_output(args[4]), self.to == self.get_state(args[5]))
        return Implies(hypo, resu)

    def eq(self, args):
        return args[0] == args[1]

    def neq(self, args):
        return args[0] != args[1]

    def assign(self, args):
        return self.write_register(args[0]) == args[1]

    def plus(self, args):
        return args[0] + args[1]

    def register(self, args):
        return self.read_register(args[0])

    def var(self, args):
        if args[0] not in self.vars:
            self.vars[args[0]] = BitVec(args[0], self.width)
        return self.vars[args[0]]

    def lit(self, args):
        return int(args[0])

    def assigns(self, args):
        return And(*args)

print(TreeToSketch().transform(result))