from lark import Lark, Transformer
import sys
import math


with open('grammar.lark', 'r') as grammar_file:
    grammar = grammar_file.read()

parser = Lark(grammar, parser='lalr')


class Calculator(Transformer):
    def plus(self, items):
        return ('plus', items[0], items[1])

    def minus(self, items): 
        return ('minus', items[0], items[1])

    def times(self, items):
        return ('times', items[0], items[1])
    
    def power(self, items):
        return ('power', items[0], items[1])

    def neg(self, items):
        return ('neg', items[0])

    def log(self, items):
        return ('log', items[0], items[1])

    def num(self, items):
        return float(items[0])

    def parens(self, items):
        return items[0]
    


def evaluate(ast):
    if isinstance(ast, tuple):

        if ast[0] == 'plus':
            return evaluate(ast[1]) + evaluate(ast[2])
        elif ast[0] == 'minus':
            return evaluate(ast[1]) - evaluate(ast[2])
        elif ast[0] == 'times':
            return evaluate(ast[1]) * evaluate(ast[2])
        elif ast[0] == 'power':
            return evaluate(ast[1]) ** evaluate(ast[2])
        elif ast[0] == 'neg':
            return -evaluate(ast[1])
        elif ast[0] == 'log':
            return math.log(evaluate(ast[1]), evaluate(ast[2]))
        else:
            raise ValueError(f"Unknown operation: {ast[0]}")
    else:
        return ast 


if __name__ == '__main__':
    calc_transformer = Calculator()
    input_string = sys.argv[1]  
    tree = parser.parse(input_string) 
    ast = calc_transformer.transform(tree)  
    result = evaluate(ast)  
    print(f"Result: {result}") 
