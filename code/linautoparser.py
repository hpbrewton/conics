from lark import Lark

with open("code/linauto.lark") as f:
    grammar = ''.join(f.readlines())
    parser = Lark(grammar, start='expr')
    with open("benchmarks/ex") as e:
        source = ''.join(e.readlines())
        ast = parser.parse(source)
        print(ast)