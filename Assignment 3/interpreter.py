import sys
from lark import Lark, Transformer, Tree
import lark

print(f"Python version: {sys.version}")
print(f"Lark version: {lark.__version__}")


def interpret(source_code):
    cst = parser.parse(source_code)
    ast = LambdaCalculusTransformer().transform(cst)
    result_ast = evaluate(ast)
    result = linearize(result_ast)
    return result


parser = Lark(open("grammar.lark").read(), parser='lalr')


class LambdaCalculusTransformer(Transformer):
    def lam(self, args):
        name, body = args
        return ('lam', str(name), body)

    def app(self, args):
        new_args = [(arg.data, arg.children[0]) if isinstance(arg, Tree) and arg.data == 'int' else arg for arg in args]
        return ('app', *new_args)

    def var(self, args):
        token, = args
        return ('var', str(token))

    def NAME(self, token):
        return str(token)


def evaluate(tree):
    if tree[0] == 'app':
        e1 = evaluate(tree[1])
        e2 = evaluate(tree[2])

        if e1 == e2:
            return tree 

        if e1[0] == 'lam':
            body = e1[2]
            name = e1[1]
            rhs = substitute(body, name, e2)
            result = evaluate(rhs)
        else:
            result = ('app', e1, e2)
    else:
        result = tree
    return result

class NameGenerator:
    def __init__(self):
        self.counter = 0

    def generate(self):
        self.counter += 1
        return 'Var' + str(self.counter)

name_generator = NameGenerator()

def substitute(tree, name, replacement):
    if tree[0] == 'var':
        if tree[1] == name:
            return replacement
        else:
            return tree
    elif tree[0] == 'lam':
        if tree[1] == name:
            return tree
        else:
            fresh_name = name_generator.generate()
            new_body = substitute(tree[2], tree[1], ('var', fresh_name))
            result = ('lam', fresh_name, substitute(new_body, name, replacement))
            return result
    elif tree[0] == 'app':
        return ('app', substitute(tree[1], name, replacement), substitute(tree[2], name, replacement))
    else:
        raise Exception('Unknown tree', tree)

def linearize(ast):
    if ast[0] == 'var':
        return ast[1]
    elif ast[0] == 'lam':
        return "(" + "\\" + ast[1] + "." + linearize(ast[2]) + ")"
    elif ast[0] == 'app':
        return "(" + linearize(ast[1]) + " " + linearize(ast[2]) + ")"
    else:
        raise Exception('Unknown AST', ast)

def main():
    if len(sys.argv) != 2:
        print("Usage: python interpreter.py <filename>", file=sys.stderr)
        sys.exit(1)

    filename = sys.argv[1]
    with open(filename, 'r') as file:
        expression = file.read()

    result = interpret(expression)
    print(f"\033[95m{result}\033[0m")

if __name__ == "__main__":
    main()
