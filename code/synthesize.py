from z3 import *
from filters import *
from diag import perm_generator
from to_formula import formula

def arithfills(registers, nvars):
	old = []
	old.extend([["varb", "x{}".format(n)] for n in range(nvars)])
	old.extend([["varb", reg] for reg in registers])
	print(old)
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

def kfills(k, registers=[], nvars=0):
	return perm_generator(arithfills(registers, nvars), k)

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

'''
a simple synthesizer which produces successively more complicated expressions (see fills),
does a k-dimensional diagonal traversal over these (intuition: https://upload.wikimedia.org/wikipedia/commons/thumb/6/6f/Pairing_natural.svg/1024px-Pairing_natural.svg.png),
and checks to see if model is satisfiable
'''
def synthesize(tree):
	print(registers(tree))
	arholes = arithholes(tree)
	nholes = len(arholes)
	for fill in kfills(nholes, registers(tree), 1):
		v = {k : v for k, v in zip(arholes, fill)}
		tprime = substitute(v, tree)
		f = formula(tprime)
		s = Solver()
		s.add(f)
		if unsat != s.check():
			raw_model = s.model()
			model = {k.name() : raw_model[k] for k in raw_model.decls()}
			return backsubstitute(registers(tprime), model, tprime)

