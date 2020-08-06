from z3 import *
import lark
import string
from lark import Tree, Token

parser = lark.Lark('''
transducer: "transducer" CNAME [CNAME*] "{" [edge*] "}" "examples" "{" [example*] "}"

edge: CNAME "/" CNAME "/" bexpr "/" assigns "/" CNAME "/" CNAME "/"

assigns: [assign*]
assign: CNAME "=" aexpr ";"

bexpr: bexpr "||" bexpr -> or
	| bexpr "&&" bexpr -> and
	| "!" bexpr -> not
	| aexpr ">=" aexpr -> gte
	| aexpr ">" aexpr -> gt
	| aexpr "<=" aexpr -> lte
	| aexpr "<" aexpr -> lt
	| aexpr "==" aexpr -> eq 
	| aexpr "!=" aexpr -> neq
	| "??" CNAME -> boolhole

aexpr: aexpr "+" aexpr -> add
	| aexpr "*" aexpr -> mul
	| "-" aexpr -> neg
	| CNAME -> varb 
	| "??" CNAME -> arithhole
	| SIGNED_INT -> int

register: CNAME
variable: CNAME

example: word "/" word ";"
word: CNAME [("," CNAME)*] 

%import common.CNAME
%import common.SIGNED_INT
%import common.WS

%ignore WS
''', start='transducer')

example = ''.join(sys.stdin.readlines())
 
def tree_to_sexpr(source, tree):
	if type(tree) == Tree:
		return [tree.data] + [tree_to_sexpr(source, child) for child in tree.children]
	elif type(tree) == Token:
		return source[tree.pos_in_stream:tree.end_pos] 

il = lambda x: isinstance(x, list)

def edges(tree):
	return filter(lambda x: il(x) and x[0] == 'edge', tree)

def states(tree):
	return {v for edge in edges(tree) for v in (edge[1], edge[-1])}

def inputs(tree):
	return {edge[2] for edge in edges(tree)}

def outputs(tree):
	return {edge[-2] for edge in edges(tree)}

def registers(tree):
	return {item for item in tree[2:] if not il(item)}

def findall(tree, what):
	if not il(tree):
		if tree == what:
			return tree
	if tree[0] == what:
		yield tree
	for child in tree[1:]:
		for item in findall(child, what):
			yield item

def arithholes(tree):
	return { x[1] for x in findall(tree, "arithhole")}

def boolholes(tree):
	return { x[1] for x in findall(tree, "boolhole")}

def variables(tree):
	return { x[1] for x in findall(tree, "varb")}

def varbs(items):
	enumed = list(enumerate(items))
	to_num = { num : str for (num, str) in enumed}
	from_num = { str : num for (num, str) in enumed}
	return (from_num, to_num)

def bitvecs(names, prefix=""):
	return {name : BitVec("{}{}".format(name, prefix), 8) for name in names}

def expression(tree, reg_in, variables):
	if type(tree) == str:
		if tree.isnumeric():
			return int(tree)
	c = [expression(child, reg_in, variables) for child in tree[1:]]
	if tree[0] == "eq": return (c[0] == c[1])
	elif tree[0] == "neq": return (c[0] != c[1])
	elif tree[0] == "lte": return (c[0] <= c[1])
	elif tree[0] == "gt": return (c[0] > c[1])
	elif tree[0] == "add": return (c[0] + c[1])
	elif tree[0] == "mul": return (c[0] * c[1])
	elif tree[0] == "varb": return c[0]
	elif tree[0] in reg_in: return (reg_in[tree[0]])
	elif tree[0] in variables: return (variables[tree[0]])
	elif tree[0] == "int": return c[0]
	else: 
		raise Exception("{} not found".format(tree[0]))

def assignments(tree, reg_in, reg_out, variables):
	exprs = []
	for assignment in tree[1:]:
		expr = reg_out[assignment[1]] == expression(assignment[2], reg_in, variables)
		exprs.append(expr)
	return And(*exprs) 

def hypo_res(tree):
	def ret(st, inp, out, fsh, states_m, inp_m, out_m, reg_in, reg_out, variables):
		es = edges(tree)
		guards = []
		edgels = []
		for e in es:
			stl = st == states_m[e[1]]
			inpl = inp_m[inp] == inp_m[e[2]]
			guardl = expression(e[3], reg_in, variables)
			hypol = And(stl, inpl, guardl)
			guards.append(hypol)
	
			deltal = assignments(e[-3], reg_in, reg_out, variables)
			outl = out_m[out] == out_m[e[-2]]
			fshl = fsh == states_m[e[-1]]
			resul = And(deltal, outl, fshl)
			edgels.append(Implies(hypol, resul))
		return (And(*edgels, Or(*guards)))
	return ret

def examples(tree):
	return [elem[1:] for elem in tree if il(elem) and elem[0] == "example"]

def formula(tree):
	head_maker = hypo_res(tree)

	states_tn, states_fn = varbs(states(tree))
	inputs_tn, inputs_fn = varbs(inputs(tree))
	outputs_tn, outputs_fn = varbs(outputs(tree))
	vars = bitvecs(variables(tree))

	formulae = []
	for example in examples(tree):
		input = example[0][1:]
		output = example[1][1:]
		length = len(input)
		sts = [BitVec("s_{}".format(i), width(len(states(tree)))) for i in range(length+1)]
		sts_starts = sts[0] == 0
		regs = [bitvecs(registers(tree), "in_{}".format(i)) for i in range(length+1)]
		reg_starts = And(*[regs[0][key] == 0 for key in regs[0]])
	
		formulae.append(And(sts_starts, reg_starts, *[head_maker(sts[i], input[i], output[i], sts[i+1], states_tn, inputs_tn, outputs_tn, regs[i], regs[i+1], vars) for i in range(length)]))

	return And(*formulae)
		

def width(x):
	return 1+math.ceil(math.log2(x))

def scores(n, k):
	s = [0 for _ in range(k)]
	s[0] = n
	t = True
	while t:
		v = [s[i-1] - s[i] for i in range(1, k)] 
		total = sum(v)
		v.append(n-total)
		yield v
		t = False
		for i in range(k-1, 0, -1):
			if s[i] < s[i-1]:
				s[i] += 1	
				t = True
				for j in range(i+1, k):
					s[j] = 0 
				break

def fixed_numbers(k):
	i = 0
	while True:
		for v in scores(i, k):
			yield v
		i += 1

def perm_generator(g, k):
	l = []
	i = 0
	for v in g:
		l.append(v)
		for v in scores(i, k):
			yield [l[j] for j in v]
		i += 1

def fills():
	old = [["varb", "x"], ["varb", "r"]]
	newer = old
	newest = []
	for v in newer:
		yield v
	while True:
		for ni in newer:
			for oi in old:	
				a = ["add", ni, oi]
				m = ["mul", ni, oi]
				yield a
				yield m
				newest.append(a)
				newest.append(m)
		old.extend(newer)
		newer = newest
		newest = []

def kfills(k):
	return perm_generator(fills(), k)

def substitute(v, tree):
	if not il(tree):
		return tree
	elif tree[0] == "arithhole":
		return v[tree[1]]
	else:
		return [substitute(v, part) for part in tree]

def backsubstitute(regs, model, tree):
	if not il(tree):
		return tree
	elif tree[0] == "varb" and tree[1] not in regs:
		return model[tree[1]]
	else:
		return [backsubstitute(regs, model, part) for part in tree]

def synthesize(tree):
	arholes = arithholes(tree)
	nholes = len(arholes)
	for fill in kfills(nholes):
		v = {k : v for k, v in zip(arholes, fill)}
		tprime = substitute(v, tree)
		f = formula(tprime)
		s = Solver()
		s.add(f)
		if unsat != s.check():
			raw_model = s.model()
			print(f)
			model = {k.name() : raw_model[k] for k in raw_model.decls()}
			return backsubstitute(registers(tprime), model, tprime)

def display_expr(e):
	def op(f):
		return display_expr(e[1]) + " " +  f + " " + display_expr(e[2])
	if not il(e): return str(e)
	if e[0] == "neq": return op("!=")
	elif e[0] == "eq": return op("==")
	elif e[0] == "add": return op("+")
	elif e[0] == "mul": return op("*")
	elif e[0] == "varb": return e[1] 
	elif e[0] == "int": return e[1]
	elif e[0] == "assign": return op("=")
	elif e[0] == "lte": return op("<=")
	elif e[0] == "gt": return op(">")
	elif e[0] == "assigns":
		return str(*[display_expr(assign) for assign in e[1:]]) + ";"
 
def display_edges(e):
	for edge in e:
		g = display_expr(edge[3])
		d = display_expr(edge[-3])
		print("\t" + " / ".join([edge[1], edge[2], g, d, edge[-2], edge[-1]]) + " /")

def display(tree):
	for item in tree:
		if item[0] == 'edge':
			break
		print(item, end = " ")
	print("{")
	display_edges(edges(tree))
	print("}")

out = parser.parse(example)
tree = tree_to_sexpr(example, out)
display(synthesize(tree))
