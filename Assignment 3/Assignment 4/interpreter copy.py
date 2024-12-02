import sys
from lark import Lark, Transformer, Tree
import lark
import os

# run/execute/interpret source code
def interpret(source_code):
    cst = parser.parse(source_code)
    ast = LambdaCalculusTransformer().transform(cst)
    result_ast = evaluate(ast)
    result = linearize(result_ast)
    return result

# convert concrete syntax to CST
parser = Lark(open("grammar.lark").read(), parser='lalr')

# convert CST to AST
class LambdaCalculusTransformer(Transformer):
    def lam(self, args):
        name, body = args
        return ('lam', str(name), body)

    def app(self, args):
        return ('app', *args)

    def var(self, args):
        token, = args
        return ('var', str(token))

    def num(self, args):
        token, = args
        return ('num', float(token))

    def plus(self, args):
        return ('plus', *args)

    def minus(self, args):
        return ('minus', *args)

    def times(self, args):
        return ('times', *args)

    def neg(self, args):
        return ('neg', args[0])

    def parens(self, args):
        return args[0]

    def NAME(self, token):
        return str(token)



def evaluate(tree):
    if isinstance(tree, float):
        return tree
    elif tree[0] == 'app':
        e1 = evaluate(tree[1])
        if isinstance(e1, tuple) and e1[0] == 'lam':
            body = e1[2]
            name = e1[1]
            arg = evaluate(tree[2])
            rhs = substitute(body, name, arg)
            return evaluate(rhs)
        else:
            return ('app', e1, evaluate(tree[2]))
    elif tree[0] == 'plus':
        return evaluate(tree[1]) + evaluate(tree[2])
    elif tree[0] == 'minus':
        return evaluate(tree[1]) - evaluate(tree[2])
    elif tree[0] == 'times':
        return evaluate(tree[1]) * evaluate(tree[2])
    elif tree[0] == 'neg':
        return -evaluate(tree[1])
    elif tree[0] == 'num':
        return tree[1]
    elif tree[0] == 'var':
        return tree
    elif tree[0] == 'lam':
        return tree
    else:
        raise Exception('Unknown tree', tree)


# generate a fresh name 
# needed eg for \y.x [y/x] --> \z.y where z is a fresh name)
class NameGenerator:
    def __init__(self):
        self.counter = 0

    def generate(self):
        self.counter += 1
        # user defined names start with lower case (see the grammar), thus 'Var' is fresh
        return 'Var' + str(self.counter)

name_generator = NameGenerator()

# for beta reduction (capture-avoiding substitution)
# 'replacement' for 'name' in 'tree'
def substitute(tree, name, replacement):
    if isinstance(tree, float):
        return tree
    elif tree[0] == 'var':
        if tree[1] == name:
            return replacement
        else:
            return tree
    elif tree[0] == 'lam':
        if tree[1] == name:
            return tree
        else:
            fresh_name = name_generator.generate()
            return ('lam', fresh_name, substitute(substitute(tree[2], tree[1], ('var', fresh_name)), name, replacement))
    elif tree[0] == 'app':
        return ('app', substitute(tree[1], name, replacement), substitute(tree[2], name, replacement))
    elif tree[0] in ['plus', 'minus', 'times']:
        return (tree[0], substitute(tree[1], name, replacement), substitute(tree[2], name, replacement))
    elif tree[0] == 'neg':
        return ('neg', substitute(tree[1], name, replacement))
    elif tree[0] == 'num':
        return tree
    else:
        raise Exception('Unknown tree', tree)



def linearize(ast):
    if isinstance(ast, float):
        return str(ast)
    elif ast[0] == 'var':
        return ast[1]
    elif ast[0] == 'lam':
        return "(" + "\\" + ast[1] + "." + linearize(ast[2]) + ")"
    elif ast[0] == 'app':
        left = linearize(ast[1])
        right = linearize(ast[2])
        if len(ast) >= 3:
            right += " " + linearize(ast[3])
        return "(" + left + " "  + right + ")"
    else:
        return str(ast)

def main():
    import sys
    if len(sys.argv) != 2:
        sys.exit(1)

    input_arg = sys.argv[1]

    if os.path.isfile(input_arg):
        # If the input is a valid file path, read from the file
        with open(input_arg, 'r') as file:
            expression = file.read()
    else:
        # Otherwise, treat the input as a direct expression
        expression = input_arg

    result = interpret(expression)
    print(f"\033[95m{result}\033[0m")

if __name__ == "__main__":
    main()

