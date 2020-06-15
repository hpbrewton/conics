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
m.add_example([0, 0, 0, 0], [0, 0, 1, 0])
m.add_example([0, 0, 1, 0], [0, 0, 2, 0])
for r in synthesize(3, [v.i, c]):
    m.add_edge(0, v.i != 3, And(v.o == r, m.o == 0), 0)
    m.add_edge(0, v.i == 3, And(v.o == r, m.o == 1), 0)
    s = Solver()
    f = m.formula()
    s.add(f)
    if unsat != s.check():
        print(r)
        print(s.model())
        break
    m.clear()
else:
    print("no model")