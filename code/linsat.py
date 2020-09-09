from z3 import *
import math

class LinSat:
    def __init__(self, n, m, exprs):
        self.n = n 
        self.m = m 
        self.exprs = exprs

    def __getitem__(self, pos):
        r,c=pos
        return self.exprs[r][c]

    # is greater than or equal to zero
    def is_gtez(self):
        return And(*[self[i, j] >= 0 for j in range(self.m) for i in range(self.n)])

    def is_zero(self):
        return And(*[self[i, j] == 0 for j in range(self.m) for i in range(self.n)])

    def dot(self, other):
        exprs = [[sum([self[i, c]*other[c, j] for c in range(self.m)]) for j in range(other.m)] for i in range(self.n)]
        return LinSat(self.n, other.m, exprs)

    def vcat(self, other):
        exprs = self.exprs + other.exprs
        return LinSat(self.n+other.n, self.m, exprs)

    def __add__(self, other):
        exprs = [[self[i,j]+other[i,j] for j in range(self.m)] for i in range(self.n)]
        return LinSat(self.n, self.m, exprs)

    def __eq__(self, other):
        return And(*[self[i, j] == other[i, j] for i in range(self.n) for j in range(self.m)])

    def __repr__(self):
        return '\n'.join(map(str, self.exprs))

class LinSatVar(LinSat):
    def __init__(self, n, m, name="m", width=8):
        exprs = [[Int("{}_{}_{}".format(name, j, i)) for i in range(m)] for j in range(n)]
        super().__init__(n, m, exprs)

class LinSatConstVec(LinSat):
    def __init__(self, lst, name="m", width=8):
        exprs = [[lst[i]] for i in range(len(lst))]
        super().__init__(len(lst), 1, exprs)


def width(n):
    return math.ceil(math.log(n))+1

def problem(n, c, r, inp, out, examples):
    gm = [[LinSatVar(c, r+inp, name="gm{}_{}".format(i, j)) for j in range(n)] for i in range(n)]
    gv = [[LinSatVar(c, 1, name="gv{}_{}".format(i, j)) for j in range(n)] for i in range(n)]
    om = [[LinSatVar(out, r, name="om{}_{}".format(i, j)) for j in range(n)] for i in range(n)]
    ov = [[LinSatVar(out, 1, name="ov{}_{}".format(i, j)) for j in range(n)] for i in range(n)]
    um = [[LinSatVar(r, r, name="um{}_{}".format(i, j)) for j in range(n)] for i in range(n)]
    uv = [[LinSatVar(r, 1, name="uv{}_{}".format(i, j)) for j in range(n)] for i in range(n)]

    def edge_and_hypo(s, sp, reg, regp, inp, out):
        hypos = []
        edges = []
        # positive edge
        for i, j in [(0, 0), (0, 1)]:
            in_state_match = s == i 
            guard_match = (gm[i][j].dot(reg.vcat(inp)) + gv[i][j]).is_gtez()
            out_match = out == om[i][j].dot(reg)+ov[i][j]
            reg_match = regp == um[i][j].dot(reg)+uv[i][j]
            out_state_match = sp == j 
            hypo = And(in_state_match, guard_match)
            logic = Implies(hypo, And(out_match, reg_match, out_state_match))
            edges.append(logic)
            hypos.append(hypo)
        negative_edge = Implies(Not(Or(*hypos)), False)
        edges.append(negative_edge)
        return And(*edges)

    s = BitVec("s", width(n))
    sp = BitVec("sp", width(n))
    reg = LinSatVar(r, 1, name="r")
    regp = LinSatVar(r, 1, name="rp")
    inp = LinSatVar(inp, 1, name="i")
    out = LinSatVar(out, 1, name="o")

    i = 0
    examples_logic = []
    for inpr, outr in examples:
        inp = list(map(LinSatConstVec, inpr))
        out = list(map(LinSatConstVec, outr))
        sz = len(inp)+1
        states = [BitVec("s_{}_{}".format(i, t), width(n)) for t in range(sz)]
        regitsters = [LinSatVar(r, 1, name="r_{}_{}".format(i, t)) for t in range(sz)]
        example_logic = []
        for t in range(1, sz):
            example_logic.append(edge_and_hypo(
                states[t-1], 
                states[t],
                regitsters[t-1],
                regitsters[t],
                inp[t-1],
                out[t-1],
            ))
            example_logic.append(ULT(states[t], n))
        example_logic.append(states[0]==0)
        example_logic.append(regitsters[0].is_zero())
        examples_logic.append(And(*example_logic))
        i += 1
    return And(*examples_logic)


examples = [
    ([], []),
    ([[0]], [[0]]),
    ([[1], [0]], [[0], [1]]),
    ([[1], [1], [1], [0]], [[0], [0], [0], [3]]),
    # ([[1], [1], [1], [1], [1], [0]], [[0], [0], [0], [0], [0], [5]]),
    # ([[1], [1], [1], [1], [1], [1], [0]], [[0], [0], [0], [0], [0], [0], [6]]),
    # ([[1], [1], [1], [1], [1], [1], [1], [0]], [[0], [0], [0], [0], [0], [0], [0], [7]]),
    # ([[1], [1], [1], [1], [1], [1], [1], [1], [0]], [[0], [0], [0], [0], [0], [0], [0], [0], [8]]),
    # ([[1], [1], [1], [1], [1], [1], [1], [1], [1], [0]], [[0], [0], [0], [0], [0], [0], [0], [0], [0], [9]]),
    # ([[1], [1], [1], [1], [1], [1], [1]], [[0], [0], [0], [0], [0], [0], [0]]),
    # # ([[1], [1], [0], [1], [0]], [[0], [0], [2], [0], [1]]),
    # ([[1], [1], [0], [1], [1], [1], [1], [0]], [[0], [0], [2], [0], [0], [0], [0], [4]]),
]

m = problem(2, 1, 1, 1, 1, examples)
print(m)
s = Solver()
s.add(m)
if unsat == s.check():
    print(":(")
else:
    print(s.model())

# b = LinSatVar(5, 1, "bs