import lark
from lark import Tree, Token

def parse(source):
	# this is pretty close to norm EBNF
	# however, the lark package library will be useful to get more detail here
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

	tree = parser.parse(source)

	# this is to get rid of all the lark structures... gross
	def tree_to_sexpr(tree):
		if type(tree) == Tree:
			return [tree.data] + [tree_to_sexpr(child) for child in tree.children]
		elif type(tree) == Token:
			return source[tree.pos_in_stream:tree.end_pos] 
	return tree_to_sexpr(tree)