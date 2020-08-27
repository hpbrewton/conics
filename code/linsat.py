from z3 import *

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

    def dot(self, other):
        exprs = [[sum([self[i, c]*other[c, j] for c in range(self.m)]) for j in range(other.m)] for i in range(self.n)]
        return LinSat(self.n, other.m, exprs)

    def vcat(self, other):
        exprs = self.exprs + other.exprs
        return LinSat(self.n+other.n, self.m, exprs)

    def __add__(self, other):
        exprs = [[self[i,j]+other[i,j] for j in range(self.m)] for i in range(self.n)]
        return LinSat(self.n, self.m, exprs)

    def __repr__(self):
        return '\n'.join(map(str, self.exprs))

class LinSatVar(LinSat):
    def __init__(self, n, m, name="m", width=8):
        exprs = [[BitVec("{}_{}_{}".format(name, j, i), width) for i in range(m)] for j in range(n)]
        super().__init__(n, m, exprs)

def natural_iso(vs):
    size = len(vs)
    ls = [v for v in vs] 
    rs = {v : n for v, n in enumerate(ls)}
    return v.__getitem__, ls.__getitem__

class LinAutomata:
    def __init__(self, topology, c=4, r=2, width=8):
        points = {v, w for v, w in topology}
        to_nat, from_nat = natural_iso(points)
        self.state = BitVec("s", math.ciel(math.log(len(points)))+1)
        

A = LinSatVar(5, 5, "A")
x = LinSatVar(5, 1, "x")
b = LinSatVar(5, 1, "B")
v = A.dot(x)+b
print(v.vcat(v))
# b = LinSatVar(5, 1, "bs