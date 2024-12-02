import sys
import os
from lark import Lark, Transformer, Tree

def interpret(source_code):
    cst = parser.parse(source_code)
    ast = LambdaCalculusTransformer().transform(cst)
    env = {}  # Initialize the environment
    result_ast = evaluate(ast, env)  # Pass the environment to evaluate
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

    def neg(self, args):
        return ('neg', args[0])

    def if_expr(self, args):
        return ('if', *args)

    def leq(self, args):
        return ('leq', *args)

    def eq(self, args):
        return ('eq', *args)

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

def evaluate(tree, env):
    if isinstance(tree, Tree):
        # Extract the operation (first element) and its arguments (children)
        op = tree.data
        children = tree.children
    else:
        return tree  # If the node is not a Tree, it's a value like a number or string
    
    print(f"Evaluating {tree} with environment {env}")  # Debugging print to check evaluation

    # Evaluate the tree based on its operation type
    if op == 'lam':
        # Lambda function: \x. expression
        var = children[0]
        body = children[1]
        return lambda arg: evaluate(body, {**env, var: arg})
    
    elif op == 'app':
        # Function application: (f x)
        func = evaluate(children[0], env)  # The function (should be a lambda)
        arg = evaluate(children[1], env)  # The argument
        print(f"Applying function {func} to argument {arg}")
        return func(arg)  # Apply the function
    
    elif op == 'letrec':
        # Recursive let: letrec f = \n. body in f 4
        func_name = children[0]
        func_def = children[1]  # Lambda definition of f
        body = children[2]  # Body of the function call
        
        # First, define the recursive function as a placeholder in the environment
        def recursive_func(arg):
            # We will bind the function name to itself in the local environment for recursion
            new_env = {**env, func_name: recursive_func}
            return evaluate(func_def, {**new_env, 'n': arg})

        # Bind the recursive function to the environment
        env[func_name] = recursive_func

        # Now evaluate the function call with the extended environment
        result = evaluate(body, env)  # Evaluate the body of the letrec expression
        print(f"Letrec result: {result}")  # Debugging print to check the final result
        return result
    
    elif op == 'if':
        # If expression: if condition then expr1 else expr2
        condition = evaluate(children[0], env)
        if condition != 0:  # If the condition is true (non-zero)
            return evaluate(children[1], env)
        else:
            return evaluate(children[2], env)
    
    elif op == 'equals':
        # Equality comparison: (a == b)
        left = evaluate(children[0], env)
        right = evaluate(children[1], env)
        return 1 if left == right else 0
    
    elif op == 'var':
        # Variable reference
        var_name = children[0]
        if var_name in env:
            return env[var_name]
        else:
            raise ValueError(f"Unknown variable: {var_name}")
    
    elif op == 'num':
        # Number literal
        return children[0]  # Return the number directly
    
    elif op == 'plus':
        # Addition: (a + b)
        left = evaluate(children[0], env)
        right = evaluate(children[1], env)
        return left + right
    
    elif op == 'times':
        # Multiplication: (a * b)
        left = evaluate(children[0], env)
        right = evaluate(children[1], env)
        return left * right
    
    elif op == 'minus':
        # Subtraction: (a - b)
        left = evaluate(children[0], env)
        right = evaluate(children[1], env)
        return left - right
    
    elif op == 'neg':
        # Negation: (-a)
        value = evaluate(children[0], env)
        return -value
    
    else:
        raise ValueError(f"Unknown operation: {op}")

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
    if isinstance(ast, Tree):
        # Extract tree data and children
        ast_data = ast.data
        ast_children = ast.children
    else:
        # If it's not a Tree, it should be a literal value (number, etc.)
        return str(ast)

    if ast_data == 'lam':
        # Lambda function
        return f"\\{ast_children[0]}.{linearize(ast_children[1])}"
    elif ast_data == 'app':
        # Function application
        return f"({linearize(ast_children[0])} {linearize(ast_children[1])})"
    elif ast_data == 'letrec':
        # Recursive let
        return f"letrec {ast_children[0]} = {linearize(ast_children[1])} in {linearize(ast_children[2])}"
    elif ast_data == 'var':
        # Variable
        return str(ast_children[0])
    elif ast_data == 'num':
        # Number literal
        return str(ast_children[0])
    else:
        return f"Unknown: {ast_data}"



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
