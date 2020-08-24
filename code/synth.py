from itertools import product

def permutations(n):
    fmt = "{:0" + str(n) + "b}"
    for i in range(1, 2**n):
        yield list(map(lambda v: v == '1', fmt.format(i)))

class Production:
    def __init__(self, nt, elems):
        self.nt = nt 
        self.elems = elems

def synthesize(grammar, terminals, nts):
    o = {t: [[t]] for t in terminals}
    f = {t: [[t]] for t in terminals}
    while True:
        fp = {}
        for prod in grammar:
            if prod.nt not in fp:
                fp[prod.nt] = []
            for permutation in permutations(len(prod.elems)):
                generators = []
                for i, b in enumerate(permutation):
                    if b:
                        generators.append(f.get(prod.elems[i], []))
                    else:
                        generators.append(o.get(prod.elems[i], []))
                for v in product(*generators):
                    fp[prod.nt].append([t for l in v for t in l])
        for e in product(*map(fp.get, nts)):
            yield e
        for k in f:
            if k not in o:
                o[k] = []
            for s in f[k]:
                o[k].append(s)
        f = fp 

productions = [
    Production("elem", ["(", "elem", "elem", ")"]),
    Production("elem", ["(", "elem", ")"])
]

terminals = [
    Production("elem", ["(", ")"])
]

for v in synthesize(productions, terminals, ["elem"]):
    print(list(v))
    input()