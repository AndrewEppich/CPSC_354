import math

def add(x,y):
    return x + y

def subtract(x,y):
    return x - y

def multiply(x,y):
    return x * y

def divide(x,y):
    if y == 0:
        return "Error, cannot divide by zero"
    else:
        return x/y

def exponent(x,y):
    return x**y

def square(x):
    return math.sqrt(x)

def logarithm(x,y):
    if x <= 0 or y <= 0:
        return "Error, cannot take the log of 0 or a negative number"
    else:
        return math.log(x,y)
    
def etox(x):
    return math.exp(x)

while True:
    print("Choose an operation")
    print("1. Add")
    print("2. Subtract")
    print("3. Multiply")
    print("4. Divide")
    print("5. Exponent")
    print("6. Square Root")
    print("7. Logarithm")
    print("8. Exponential Function")
    print("9. Exit")

    choice = input("Please choose a number ")

    if choice == '9':
        break

    if choice in ['1','2','3','4','5','7','9']:
            
        num1 = float(input("Enter the first number "))
        num2 = float(input("Enter the second number "))

        if choice == '1':
            print(f"The answer is: {add(num1,num2)}")
        elif choice == '2':
            print(f"The answer is: {subtract(num1,num2)}")
        elif choice == '3':
            print(f"The answer is: {multiply(num1,num2)}")
        elif choice == '4':
            print(f"The answer is: {divide(num1,num2)}")
        elif choice == '5':
            print(f"The answer is: {exponent(num1,num2)}")
        elif choice == '7':
            print(f"The answer is: {logarithm(num1,num2)}")
        elif choice == '9':
            break
        else:
            print("Invalid input")
    if choice == '6':
        num1 = float(input("Enter the number "))
        print(f"The answer is: {square(num1)}")
    elif choice == '8':
        num1 = float(input("Enter the number "))
        print(f"The answer is: {etox(num1)}")
