from z3 import *

def width(max):
    if max <= 1: 
        return 1
    else:
        return math.ceil(math.log2(max))

class MachineSketch:
    def __init__(self):
        self.inputs = []
        self.outputs = []
        self.nextState = 0 
        self.start_state = None
        self.assignments = [] # Register * Pos * Edge
        self.holes = [] # String * width
        self.literals = [] # Int * width 
        self.variables = [] # String * width 
        self.registers = [] # String * width
        self.ops = [] # Pos * Rep * Pos
        self.positions = [] # K * Int
        self.examples = [] # String^2
        self.edges = [] # Int * I * Pos * O * Int

    def add_state(self):
        ret = self.nextState
        self.nextState += 1 
        return ret

    def set_start_state(self, state):
        self.start_state = state 

    def add_input(self, input):
        self.inputs.append(input)
        return len(self.inputs) - 1 

    def add_output(self, output):
        self.outputs.append(output)
        return len(self.outputs) - 1

    def add_assignment(self, register, expr, edge):
        self.assignments.append((register, expr, edge))
        return len(self.assignments) - 1

    def add_hole(self, name, width):
        self.holes.append((name, width))
        return len(self.holes) - 1 

    def add_literal(self, lit):
        self.literals.append(lit)
        return len(self.literals) - 1 

    def add_literal_pos(self, lit):
        idx = self.add_literal(lit)
        return self.add_position("literal", idx)

    def add_variable(self, name, width):
        self.variables.append((name, width))
        return len(self.variables) - 1

    def add_register(self, name, width):
        self.registers.append((name, width))
        return len(self.registers) - 1

    def add_op(self, who, left, right):
        self.ops.append((who, left, right))
        return len(self.ops) - 1

    def add_op_pos(self, who, left, right):
        idx = self.add_op(who, left, right)
        return self.add_position("operation", idx)

    def add_position(self, kind, idx):
        self.positions.append((kind, idx))
        return len(self.positions) - 1

    def add_example(self, inp, out):
        # assumes |inp| = |out|
        self.examples.append((inp, out))
        return len(self.examples) - 1 

    def add_edge(self, start, inp, guard, out, finish):
        self.edges.append((start, inp, guard, out, finish))
        return len(self.edges) - 1

    def get_machine_formula(self):
        hole_formulas = [BitVec(*args) for args in self.holes]
        literal_formulas = self.literals
        variable_formulas = [BitVec(*args) for args in self.variables]
        register_formulas = [BitVec(*args) for args in self.registers]
        registerp_formulas = [BitVec(name+"'", width) for (name, width) in self.registers]

        position_formulas = []
        for (kind, idx) in self.positions:
            if kind == "hole": position_formulas.append(hole_formulas[idx])
            elif kind == "literal": position_formulas.append(literal_formulas[idx])
            elif kind == "variable": position_formulas.append(variable_formulas[idx])
            elif kind == "register": position_formulas.append(register_formulas[idx])
            elif kind == "operation":
                (who, left, right) = self.ops[idx]
                left_f = position_formulas[left] if left != None else None 
                right_f = position_formulas[right] if right != None else None
                formula = None
                if who == "+": formula = left_f + right_f
                elif who == "*": formula = left_f * right_f
                elif who == "-": formula = -left_f
                elif who == "/\\": formula = And(left_f, right_f)
                elif who == "\\/": formula = Or(left_f, right_f)
                elif who == "==": formula = left_f  == right_f
                elif who == "!=": formula = left_f != right_f
                else: return None
                position_formulas.append(formula)
            else: return None 

        deltas_list = [list() for _ in range(len(self.edges))]
        for (reg, pos, edge) in self.assignments:
            assignment = (registerp_formulas[reg] == position_formulas[pos])
            deltas_list[edge].append(assignment)
        deltas = [And(*p_edge) for p_edge in deltas_list]

        start = BitVec("s", width(self.nextState-1))
        inp = BitVec("i", width(len(self.inputs)))
        out = BitVec("o", width(len(self.outputs)))
        target = BitVec("t", width(self.nextState-1))
        edge_formulas = [] 
        for i, (c_start, c_inp, c_guard, c_out, c_target) in enumerate(self.edges):
            hypo = And(c_start == start, c_inp == inp)
            resu = And(c_out == out, c_target == target)
            edge_formula = Implies(hypo, And(resu, deltas[i]))
            edge_formulas.append(edge_formula)

        example_formulas = []
        for (input_ex, output_ex) in self.examples:
            length = len(input_ex) #same as out length
            states = [BitVec("s_{}".format(i), width(self.nextState-1)) for i in range(length)]
            registers = [[BitVec("{}_{}".format(name, i), width) for (name, width) in self.registers] for i in range(length)]
            
            timestep_formulas = []
            for i in range(length-1):
                reg_formulas = []
                for reg in range(len(self.registers)):
                    reg_formula = And(
                        register_formulas[reg] == registers[i][reg],
                        registerp_formulas[reg] == registers[i+1][reg]
                    )
                    reg_formulas.append(reg_formula)
                timestep_body = And(
                    start == states[i],
                    inp == input_ex[i],
                    out == output_ex[i],
                    target == states[i+1],
                    And(*edge_formulas),
                    And(*reg_formulas)
                )
                timestep = Exists([start, inp, out, target, *register_formulas, *registerp_formulas], timestep_body)
                timestep_formulas.append(timestep)

            example_formula = And(states[0] == self.start_state, *timestep_formulas)
            example_formulas.append(example_formula)

sketch = MachineSketch()
"""
    m.add_edge(0, v.i != 3, And(v.o == r, m.o == 0), 0)
    m.add_edge(0, v.i == 3, And(v.o == r, m.o == 1), 0)
"""
s = sketch.add_state()
sketch.set_start_state(s)
i0 = sketch.add_input(0)
o0 = sketch.add_output(0)
o1 = sketch.add_output(1)
v = sketch.add_register("v", 5)
r = sketch.add_position("register", v)
three = sketch.add_literal_pos(3)
one = sketch.add_literal_pos(1)
g1 = sketch.add_op_pos("!=", r, three)
g2 = sketch.add_op_pos("==", r, three)
d1 = sketch.add_op_pos("+", r, one)
e1 = sketch.add_edge(s, i0, g1, o0, s)
e2 = sketch.add_edge(s, i0, g2, o1, s)
sketch.add_assignment(v, d1, e1)
sketch.add_assignment(v, d1, e2)
sketch.add_example([0, 0], [0, 0])
sketch.get_machine_formula()