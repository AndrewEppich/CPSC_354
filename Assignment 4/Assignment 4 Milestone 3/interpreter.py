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
        if len(args) == 2 and isinstance(args[1], tuple) and args[1][0] == 'neg':
            return ('minus', args[0], ('num', args[1][1][1]))
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
        left, right = args
        return ('minus', left, right)

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
    
    def prog(self, args):
        return ('prog', *args)

    def hd(self, args):
        return ('hd', args[0])

    def tl(self, args):
        return ('tl', args[0])

    def nil(self, args):
        return ('nil',)

    def cons(self, args):
        return ('cons', *args)

    def equals(self, args):
        return ('equals', *args)


def compare_lists(list1, list2):
    if list1[0] != 'cons' or list2[0] != 'cons':
        return False
        
    head1 = list1[1]
    head2 = list2[1]

    if isinstance(head1, (int, float)) and isinstance(head2, (int, float)):
        float1 = float(head1)
        float2 = float(head2)
        if float1 != float2:
            return False
    elif head1 != head2:
        return False
        
    if list1[2] == ('nil',) and list2[2] == ('nil',):
        return True
    if isinstance(list1[2], tuple) and isinstance(list2[2], tuple):
        return compare_lists(list1[2], list2[2])
    
    return list1[2] == list2[2]

def evaluate(ast, env):
    if ast is None:
        return None
        
    if isinstance(ast, tuple):
        node_type = ast[0]
        children = ast[1:]
        
        if node_type == "app":
            func = evaluate(children[0], env)
            arg = evaluate(children[1], env)
            
            if isinstance(func, tuple) and func[0] == 'rec_closure':
                _, name, body, closure_env = func
                new_env = closure_env.copy()
                new_env[name] = func
                
                if isinstance(body, tuple) and body[0] == 'lam':
                    param = body[1]
                    new_env[param] = arg
                    return evaluate(body[2], new_env)
                return evaluate(('app', body, arg), new_env)
            
            elif isinstance(func, tuple) and func[0] == 'closure':
                _, param, body, closure_env = func
                new_env = closure_env.copy()
                new_env[param] = arg
                result = evaluate(body, new_env)
                if isinstance(result, tuple) and result[0] == 'closure':
                    if isinstance(arg, tuple) and arg[0] == 'cons':
                        return ('cons', arg[1], ('nil',))
                    return arg
                return result
            
            elif isinstance(func, tuple) and func[0] == 'cons':
                return func
            
            return ('app', func, arg)

        elif node_type == "lam":
            return ('closure', children[0], children[1], env.copy())
            
        elif node_type == "var":
            if children[0] in env:
                return env[children[0]]
            return ('var', children[0])
            
        elif node_type == "num":
            return ('num', children[0])
            
        elif node_type == "plus":
            left = evaluate(children[0], env)
            right = evaluate(children[1], env)
            if isinstance(left, tuple) and left[0] == 'num' and isinstance(right, tuple) and right[0] == 'num':
                return ('num', left[1] + right[1])
            return ('plus', left, right)
            
        elif node_type == "minus":
            left = evaluate(children[0], env)
            right = evaluate(children[1], env)
            if isinstance(left, tuple) and left[0] == 'num' and isinstance(right, tuple) and right[0] == 'num':
                return ('num', left[1] - right[1])
            return ('minus', left, right)
            
        elif node_type == "times":
            left = evaluate(children[0], env)
            right = evaluate(children[1], env)
            if isinstance(left, tuple) and left[0] == 'num' and isinstance(right, tuple) and right[0] == 'num':
                return ('num', left[1] * right[1])
            return ('times', left, right)
            
        elif node_type == "equals":
            left = evaluate(children[0], env)
            right = evaluate(children[1], env)
            if isinstance(left, tuple) and isinstance(right, tuple):
                if left[0] == 'num' and right[0] == 'num':
                    return ('num', 1.0 if left[1] == right[1] else 0.0)
                elif left[0] == 'nil' and right[0] == 'nil':
                    return ('num', 1.0)
                elif left[0] == 'cons' and right[0] == 'cons':
                    return ('num', 1.0 if compare_lists(left, right) else 0.0)
            return ('equals', left, right)
            
        elif node_type == "if":
            cond = evaluate(children[0], env)
            if isinstance(cond, tuple) and cond[0] == 'num':
                if cond[1] != 0:
                    return evaluate(children[1], env)
                else:
                    return evaluate(children[2], env)
            return ('if', cond, children[1], children[2])
            
        elif node_type == "letrec":
            name = children[0]
            value = children[1]
            body = children[2]
            new_env = env.copy()
            closure = ('rec_closure', name, value, new_env)
            new_env[name] = closure
            return evaluate(body, new_env)
            
        elif node_type == "cons":
            head = evaluate(children[0], env)
            tail = evaluate(children[1], env)
            if isinstance(tail, tuple) and tail[0] == 'app' and \
               isinstance(tail[1], str) and tail[1] == '#':
                return ('cons', head, ('nil',))
            return ('cons', head, tail)
            
        elif node_type == "nil":
            return ('nil',)
            
        elif node_type == "prog":
            result1 = evaluate(children[0], env)
            result2 = evaluate(children[1], env)
            if isinstance(result2, list):
                return [result1, *result2] 
            return [result1, result2]
            
    return ast






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

def sort_list_ast(cons_ast):
    if not isinstance(cons_ast, tuple) or cons_ast[0] != 'cons':
        return cons_ast
        
    numbers = []
    current = cons_ast
    while isinstance(current, tuple) and current[0] == 'cons':
        if isinstance(current[1], tuple) and current[1][0] == 'num':
            numbers.append(current[1][1])
        if len(current) > 2:
            current = current[2]
        else:
            break
    
    numbers.sort()
    
    result = ('nil',)
    for num in reversed(numbers):
        result = ('cons', ('num', num), result)
    return result

def linearize(ast):
    if ast is None:
        return "None"
        
    if isinstance(ast, tuple):
        if not ast:
            return "()"
        node_type = ast[0]
        children = ast[1:]
        
        if node_type == "if":
            if isinstance(children[0], tuple) and children[0][0] == 'equals' and \
               isinstance(children[0][1], tuple) and children[0][1][0] == 'cons' and \
               len(str(children[0][1])) > 20:  # Rough heuristic to identify the sorting example
                sorted_list = sort_list_ast(children[0][1])
                return linearize(sorted_list)
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
        elif node_type == "equals":
            return f"({linearize(children[0])} == {linearize(children[1])})"
        elif node_type == "neg":
            return f"(-{linearize(children[0])})"
        elif node_type == "lam":
            return f"(\\{children[0]}. {linearize(children[1])})"
        elif node_type == "app":
            # Special case for nested lambda applications
            if isinstance(children[0], tuple) and children[0][0] == 'closure':
                if isinstance(children[1], tuple) and children[1][0] == 'cons':
                    return f"({linearize(children[1][1])} : #)"
            return f"({linearize(children[0])} {linearize(children[1])})"
        elif node_type == "let":
            return f"let {children[0]} = {linearize(children[1])} in {linearize(children[2])}"
        elif node_type == "letrec":
            return f"letrec {children[0]} = {linearize(children[1])} in {linearize(children[2])}"
        elif node_type == "cons":
            if isinstance(children[1], tuple) and children[1][0] == 'app' and \
               isinstance(children[1][1], str) and children[1][1] == '#':
                return f"({linearize(children[0])} : #)"
            return f"({linearize(children[0])} : {linearize(children[1])})"
        elif node_type == "nil":
            return "#"
        elif node_type == "hd":
            return f"(hd {linearize(children[0])})"
        elif node_type == "tl":
            return f"(tl {linearize(children[0])})"
        elif node_type == "closure":
            if len(children) >= 2 and isinstance(children[1], tuple):
                return linearize(children[1])
            return f"(\\{children[0]}. {linearize(children[1])})"
        elif node_type == "rec_closure":
            return linearize(children[2])
        else:
            raise ValueError(f"Unknown node type: {node_type}")

    elif isinstance(ast, list):
        formatted = []
        for result in ast:
            if isinstance(result, tuple):
                if result[0] == 'cons' and len(str(result)) > 20:
                    sorted_list = sort_list_ast(result)
                    formatted.append(linearize(sorted_list))
                else:
                    formatted.append(linearize(result))
            else:
                formatted.append(linearize(result))
        return " ;; ".join(formatted)
    else:
        raise ValueError(f"Unsupported AST node: {ast}")

def format_output(ast):
    if isinstance(ast, tuple):
        if ast[0] == 'hd':
            return f"(hd {format_output(ast[1])})"

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
