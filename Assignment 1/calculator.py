import sys

def precedence(op):
    if op == '+':
        return 1
    if op == '*':
        return 2
    if op == '^':
        return 3
    return 0

def apply_operator(operators, values):
    operator = operators.pop()
    right = values.pop()
    left = values.pop()
    if operator == '+':
        values.append(left + right)
    elif operator == '*':
        values.append(left * right)
    elif operator == '^':
        values.append(left ** right)

def evaluate_expression(expression):
    values = []
    operators = []
    i = 0
    while i < len(expression):
        if expression[i] == ' ':
            i += 1
            continue
        elif expression[i] == '(':
            operators.append(expression[i])
        elif expression[i].isdigit():
            val = 0
            while i < len(expression) and expression[i].isdigit():
                val = (val * 10) + int(expression[i])
                i += 1
            values.append(val)
            i -= 1
        elif expression[i] == ')':
            while operators and operators[-1] != '(':
                apply_operator(operators, values)
            operators.pop()
        else:
            while (operators and precedence(operators[-1]) >= precedence(expression[i])):
                apply_operator(operators, values)
            operators.append(expression[i])
        i += 1

    while operators:
        apply_operator(operators, values)

    return values[-1]

if __name__ == "__main__":
    expression = sys.argv[1]
    print(evaluate_expression(expression))
