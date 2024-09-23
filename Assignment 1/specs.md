## Parenthesis.py

* parenthesis.py takes the command line arguement and passes it into a variable called expression
* next it creates a stack. Then it iterates through the expression using a for loop
* next it adds any instance of "(" to the stack. Next if there is a ")" it pops a "(" off the stack
* once it iterates through the entire expression it checks the stack and if there is still soemthing on it
* then there is an opened parenthesis, if not then all of them are closed

## Calculator.py

* First, calculator.py defines the operators with the function operators. It returns a number 1 through 3 based on the operation
* Next, evalutate_expression initializes 2 stacks, one for operators and one for numbers.
* Next it iterates through the expressions and adds operators to the operator stack and numbers to the values stack
* It accounts for parenthesis and spaces
* Next, it calls the apply_operator method which pops 2 numbers and an operator off the stack and computes the operation
* Next, it appends the values stack to the answer to the operation it did
* It continues until there is an answer