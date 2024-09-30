## Calculator_cfg.py

* First the lark grammar file is imported to the python program
* Next, the Calculator class defines all the operations and returns the answer to the operation using the Lark grammar and command line arguements
* Next, the evauluate method checks for each operater. If the operater is present it evaluates the operation
* Fianlly, the main method takes the input string and parses it to create a parsing tree. Then the calculator class is called to evaluate each ooperation of the tree. Then the result is printed