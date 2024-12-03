import sys
import os
from lark import Lark, Transformer, Tree

def interpret(source_code):
    cst = parser.parse(source_code)
    ast = LambdaCalculusTransformer().transform(cst)
    env = {} 
    result_ast = evaluate(ast, env)
    result = linearize(result_ast)
    return result

parser = Lark(open("grammar.lark").read(), parser='lalr', debug=True)

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

    def let(self, args):
        name, value, body = args
        return ('let', str(name), value, body)

    def letrec(self, args):
        name, value, body = args
        return ('letrec', str(name), value, body)

    def fix(self, args):
        return ('fix', args[0])

    def parens(self, args):
        return args[0]

    def NAME(self, token):
        return str(token)
    
    def leq(self, args):
        return ('leq', *args)

    def eq(self, args):
        return ('eq', *args)

    def neg(self, args):
        return ('neg', args[0])

    def if_expr(self, args):
        return ('if', *args)


def evaluate(ast, env):
    if isinstance(ast, Tree):
        node_type = ast.data
        children = ast.children
        
        if node_type == "if":
            condition = evaluate(children[0], env)
            if condition:
                return evaluate(children[1], env)
            else:
                return evaluate(children[2], env)
        elif node_type == "num":
            return float(children[0])
        elif node_type == "var":
            var_name = children[0]
            if var_name in env:
                return env[var_name]
            else:
                raise ValueError(f"Undefined variable: {var_name}")
        elif node_type == "lam":
            param = children[0]
            body = children[1]
            return ("lam", param, body, env)
        elif node_type == "app":
            func = evaluate(children[0], env)
            arg = evaluate(children[1], env)
            if func[0] == "lam":
                param = func[1]
                body = func[2]
                func_env = func[3]
                new_env = func_env.copy()
                new_env[param] = arg
                return evaluate(body, new_env)
            else:
                raise ValueError(f"Trying to apply a non-function: {func}")
        elif node_type == "let":
            var_name = children[0]
            var_value = evaluate(children[1], env)
            body = children[2]
            new_env = env.copy()
            new_env[var_name] = var_value
            return evaluate(body, new_env)
        
        elif node_type == "letrec":
            func_name = children[0]
            func_lambda = children[1]
            func_body = func_lambda[1]
            new_env = env.copy()
            new_env[func_name] = ("lam", func_lambda[0], func_body, new_env)
            print(f"letrec environment for {func_name}: {new_env}")
            result = evaluate(children[2], new_env)
            print(f"letrec result for {func_name}: {result}")
            return result
        elif node_type == "plus":
            # Evaluate both sides of the plus operation
            left = evaluate(children[0], env)
            right = evaluate(children[1], env)
            return left + right
        elif node_type == "minus":
            # Evaluate both sides of the minus operation
            left = evaluate(children[0], env)
            right = evaluate(children[1], env)
            return left - right
        elif node_type == "times":
            # Evaluate both sides of the times operation
            left = evaluate(children[0], env)
            right = evaluate(children[1], env)
            return left * right
        elif node_type == "less_or_equal":
            left = evaluate(children[0], env)
            right = evaluate(children[1], env)
            return left <= right
        elif node_type == "equals":
            left = evaluate(children[0], env)
            right = evaluate(children[1], env)
            return left == right
        elif node_type == "greater_or_equal":
            left = evaluate(children[0], env)
            right = evaluate(children[1], env)
            return left >= right
        elif node_type == "greater_than":
            left = evaluate(children[0], env)
            right = evaluate(children[1], env)
            return left > right
        elif node_type == "less_than":
            left = evaluate(children[0], env)
            right = evaluate(children[1], env)
            return left < right
        else:
            raise ValueError(f"Unknown node type: {node_type}")

    elif isinstance(ast, tuple):
        node_type = ast[0]
        children = ast[1:]

        if node_type == "if":
            condition = evaluate(children[0], env)
            if condition:
                return evaluate(children[1], env)
            else:
                return evaluate(children[2], env)
        elif node_type == "num":
            return float(children[0])
        elif node_type == "var":
            var_name = children[0]
            if var_name in env:
                return env[var_name]
            else:
                raise ValueError(f"Undefined variable: {var_name}")
        elif node_type == "let":
            var_name = children[0]
            var_value = evaluate(children[1], env)
            body = children[2]
            new_env = env.copy()
            new_env[var_name] = var_value
            return evaluate(body, new_env)
        elif node_type == "lam":
            param = children[0]
            body = children[1]
            return ("lam", param, body, env)
        elif node_type == "app":
            func = evaluate(children[0], env)
            arg = evaluate(children[1], env)
            if func[0] == "lam":
                param = func[1]
                body = func[2]
                func_env = func[3]
                new_env = func_env.copy()
                new_env[param] = arg
                return evaluate(body, new_env)
            
        elif node_type == "letrec":
            func_name = children[0]
            print(f"{func_name}")
            func_lambda = children[1]
            print(f"{func_lambda}")
            func_body = func_lambda[1]
            print(f"{func_lambda[1]}")
            new_env = env.copy()
            print(f"{new_env}")
            new_env[func_name] = ("lam", func_lambda[0], func_body, new_env)
            print(f"{new_env}")
            print(f"letrec environment for {func_name}: {new_env}")
            result = evaluate(children[2], new_env)
            print(f"letrec result for {func_name}: {result}")
            return result
        elif node_type == "plus":
            # Evaluate both sides of the plus operation
            left = evaluate(children[0], env)
            right = evaluate(children[1], env)
            return left + right
        elif node_type == "minus":
            # Evaluate both sides of the minus operation
            left = evaluate(children[0], env)
            right = evaluate(children[1], env)
            return left - right
        elif node_type == "times":
            # Evaluate both sides of the times operation
            left = evaluate(children[0], env)
            right = evaluate(children[1], env)
            return left * right
        else:
            raise ValueError(f"Unsupported tuple node: {ast}")






class NameGenerator:
    def __init__(self):
        self.counter = 0

    def generate(self):
        self.counter += 1
        return 'Var' + str(self.counter)

name_generator = NameGenerator()

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
    elif tree[0] in ['app', 'plus', 'minus', 'times', 'leq', 'eq']:
        return (tree[0], substitute(tree[1], name, replacement), substitute(tree[2], name, replacement))
    elif tree[0] == 'neg':
        return ('neg', substitute(tree[1], name, replacement))
    elif tree[0] == 'if':
        return ('if', substitute(tree[1], name, replacement), substitute(tree[2], name, replacement), substitute(tree[3], name, replacement))
    elif tree[0] == 'let':
        if tree[1] == name:
            return tree
        else:
            return ('let', tree[1], substitute(tree[2], name, replacement), substitute(tree[3], name, replacement))
    elif tree[0] == 'letrec':
        if tree[1] == name:
            return tree
        else:
            return ('letrec', tree[1], substitute(tree[2], name, replacement), substitute(tree[3], name, replacement))
    elif tree[0] == 'fix':
        return ('fix', substitute(tree[1], name, replacement))
    elif tree[0] == 'num':
        return tree
    else:
        raise Exception('Unknown tree', tree)

def linearize(ast):
    if ast is None:
        raise ValueError(f"Unsupported AST node: None")
    if isinstance(ast, Tree):
        node_type = ast.data
        children = ast.children

        if node_type == "if":
            return f"if {linearize(children[0])} then {linearize(children[1])} else {linearize(children[2])}"
        elif node_type == "var":
            return children[0]
        elif node_type == "num":
            return str(children[0])
        elif node_type == "plus":
            return f"({linearize(children[0])} + {linearize(children[1])})"
        elif node_type == "minus":
            return f"({linearize(children[0])} - {linearize(children[1])})"
        elif node_type == "times":
            return f"({linearize(children[0])} * {linearize(children[1])})"
        elif node_type == "leq":
            return f"({linearize(children[0])} <= {linearize(children[1])})"
        elif node_type == "eq":
            return f"({linearize(children[0])} == {linearize(children[1])})"
        elif node_type == "neg":
            return f"(-{linearize(children[0])})"
        elif node_type == "lam":
            return f"(\\{children[0]}. {linearize(children[1])})"
        elif node_type == "app":
            return f"({linearize(children[0])} {linearize(children[1])})"
        elif node_type == "let":
            return f"let {children[0]} = {linearize(children[1])} in {linearize(children[2])}"
        elif node_type == "letrec":
            print(f"letrec {children[0]} = {linearize(children[1])} in {linearize(children[2])}")
            return f"letrec {children[0]} = {linearize(children[1])} in {linearize(children[2])}"
        else:
            raise ValueError(f"Unknown node type: {node_type}")

    elif isinstance(ast, tuple):
        # Handle tuples as nodes
        node_type = ast[0]
        children = ast[1:]

        if node_type == "if":
            return f"if {linearize(children[0])} then {linearize(children[1])} else {linearize(children[2])}"
        elif node_type == "less_or_equal":
            return f"({linearize(children[0])} <= {linearize(children[1])})"
        elif node_type == "let":
            return f"let {children[0]} = {linearize(children[1])} in {linearize(children[2])}"
        elif node_type == "lam":
            return f"(\\{children[0]}. {linearize(children[1])})"
        elif node_type == "app":
            return f"({linearize(children[0])} {linearize(children[1])})"
        elif node_type == "num":
            return str(children[0])
        elif node_type == "var":
            return children[0]
        else:
            raise ValueError(f"Unsupported tuple node: {ast}")

    elif isinstance(ast, str):  # Handle string values directly
        return ast
    elif isinstance(ast, (int, float)):  # Handle numeric literals
        return str(ast)
    else:
        raise ValueError(f"Unsupported AST node: {ast}")


def main():
    if len(sys.argv) != 2:
        sys.exit(1)

    input_arg = sys.argv[1]

    if os.path.isfile(input_arg):
        with open(input_arg, 'r') as file:
            expression = file.read()
    else:
        expression = input_arg

    result = interpret(expression)
    print(f"\033[95m{result}\033[0m")

if __name__ == "__main__":
    main()
