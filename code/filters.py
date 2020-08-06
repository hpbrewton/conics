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

def examples(tree):
	return [elem[1:] for elem in tree if il(elem) and elem[0] == "example"]

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
