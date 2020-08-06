from filters import *

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