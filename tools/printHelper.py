import termcolor

RED = "red"
GREEN = "green"
YELLOW = "yellow"
BLUE = "blue"
WHITE = "white"

def printError(text):
    printRed(f"ERROR: {text}")

def printRed(text):
    print(termcolor.colored(text, RED))

def printGreen(text):
    print(termcolor.colored(text, GREEN))

def printYellow(text):
    print(termcolor.colored(text, YELLOW))

def printBlue(text):
    print(termcolor.colored(text, BLUE))

def printMulti(tuples, between=""):    
    for text, color in tuples:
        print(termcolor.colored(text, color), end=between)
    print()

def printVariable(variableName, variable):
    printMulti([(f"{variableName }: ", BLUE), (variable, YELLOW)])

