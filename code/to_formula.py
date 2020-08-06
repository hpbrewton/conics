from z3 import *
from filters import *

def width(x):
	return 1+math.ceil(math.log2(x))

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
		if tree in reg_in:
			return reg_in[tree[0]]
		if tree in variables:
			return variables[tree]
	c = [expression(child, reg_in, variables) for child in tree[1:]]
	if tree[0] == "eq": return (c[0] == c[1])
	elif tree[0] == "neq": return (c[0] != c[1])
	elif tree[0] == "lte": return (c[0] <= c[1])
	elif tree[0] == "gt": return (c[0] > c[1])
	elif tree[0] == "add": return (c[0] + c[1])
	elif tree[0] == "mul": return (c[0] * c[1])
	elif tree[0] == "varb": 
		return c[0]
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