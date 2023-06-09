"""
6.1010 Spring '23 Lab 11: LISP Interpreter Part 1
"""
#!/usr/bin/env python3

import sys
import doctest

sys.setrecursionlimit(20_000)

# NO ADDITIONAL IMPORTS!

#############################
# Scheme-related Exceptions #
#############################


class SchemeError(Exception):
    """
    A type of exception to be raised if there is an error with a Scheme
    program.  Should never be raised directly; rather, subclasses should be
    raised.
    """

    pass


class SchemeSyntaxError(SchemeError):
    """
    Exception to be raised when trying to evaluate a malformed expression.
    """

    pass


class SchemeNameError(SchemeError):
    """
    Exception to be raised when looking up a name that has not been defined.
    """

    pass


class SchemeEvaluationError(SchemeError):
    """
    Exception to be raised if there is an error during evaluation other than a
    SchemeNameError.
    """

    pass


############################
# Tokenization and Parsing #
############################


def number_or_symbol(value):
    """
    Helper function: given a string, convert it to an integer or a float if
    possible; otherwise, return the string itself

    >>> number_or_symbol('8')
    8
    >>> number_or_symbol('-5.32')
    -5.32
    >>> number_or_symbol('1.2.3.4')
    '1.2.3.4'
    >>> number_or_symbol('x')
    'x'
    """
    try:
        return int(value)
    except ValueError:
        try:
            return float(value)
        except ValueError:
            return value


def clean_comments(source: str, comment_delimiter: str = ";") -> str:
    """
    Given an input that is potentially more than one line long, covert it
    to an equivalent input that removes any comments denoted by the comment
    delimiter in any line it is present. This also standardizes all inputs
    to have spaces on the left and right of parentheses, which makes input
    extraction significantly cleaner.

    >>> clean_comments(";This is a comment string")
    ''
    >>> clean_comments("No comments means string is unchanged.")
    'No comments means string is unchanged.'
    """
    endRes = ""
    inComment = False
    padSet = {"(", ")"}
    for curChar in source:
        # skips comments 
        if curChar == comment_delimiter:
            inComment = True
        elif curChar == "\n":
            inComment = False
        if inComment:
            continue

        # simplify parentheses by adding spaces if needed
        if curChar in padSet:
            endRes += " " + curChar + " "
        else:
            endRes += curChar

    return endRes


def tokenize(source):
    """
    Splits an input string into meaningful tokens (left parens, right parens,
    other whitespace-separated values).  Returns a list of strings.

    Arguments:
        source (str): a string containing the source code of a Scheme
                      expression

    >>> tokenize("(cat (dog (tomato)))")
    ['(', 'cat', '(', 'dog', '(', 'tomato', ')', ')', ')']
    >>> tokenize("literal")
    ['literal']
    >>> tokenize("")
    []
    """
    return clean_comments(source).split()


def parse(tokens):
    """
    Parses a list of tokens, constructing a representation where:
        * symbols are represented as Python strings
        * numbers are represented as Python ints or floats
        * S-expressions are represented as Python lists

    Arguments:
        tokens (list): a list of strings representing tokens

    >>> parse(['2'])
    2
    >>> parse(['x'])
    'x'
    >>> parse(['(', '+', '2', '(', '-', '5', '3', ')', '7', '8', ')'])
    ['+', 2, ['-', 5, 3], 7, 8]
    """
    # Otherwise begin parsing the s string
    retList = list()
    depthLookup = {0: retList}
    curDepth = 0
    for curTok in tokens:
        if curTok == "(":
            curDepth += 1

            # create new reference for inner list to use
            newSFunc = list()
            depthLookup[curDepth-1].append(newSFunc)
            depthLookup[curDepth] = newSFunc
        elif curTok == ")":
            curDepth -= 1
        else:
            depthLookup[curDepth].append(number_or_symbol(curTok))
    
        # can't have extra statements at depth 0 (not S-expr or literal)
        # and negative depths imply ill-formed parenthesis arrangement
        if len(retList) > 1 or curDepth < 0:
            raise SchemeSyntaxError("Improper token depth found.")

    # Ensure the string is actually properly formed
    if curDepth != 0:
        raise SchemeSyntaxError("Expression is ill-formed.")

    return retList[0]

######################
# Built-in Functions #
######################


scheme_builtins = {
    "+": sum,
    "-": lambda args: -args[0] if len(args) == 1 else (args[0] - sum(args[1:])),
}


##############
# Evaluation #
##############


def evaluate(tree):
    """
    Evaluate the given syntax tree according to the rules of the Scheme
    language.

    Arguments:
        tree (type varies): a fully parsed expression, as the output from the
                            parse function
    """
    raise NotImplementedError


def repl(verbose=False):
    """
    Read in a single line of user input, evaluate the expression, and print 
    out the result. Repeat until user inputs "QUIT"
    
    Arguments:
        verbose: optional argument, if True will display tokens and parsed
            expression in addition to more detailed error output.
    """
    import traceback

    while True:
        input_str = input("in> ")
        if input_str == "QUIT":
            return
        try:
            token_list = tokenize(input_str)
            if verbose:
                print("tokens>", token_list)
            expression = parse(token_list)
            if verbose:
                print("expression>", expression)
            output = evaluate(expression)
            print("  out>", output)
        except SchemeError as e:
            if verbose:
                traceback.print_tb(e.__traceback__)
            print("Error>", repr(e))

if __name__ == "__main__":
    # code in this block will only be executed if lab.py is the main file being
    # run (not when this module is imported)
    
    # uncommenting the following line will run doctests from above
    doctest.testmod()
    repl(True)
