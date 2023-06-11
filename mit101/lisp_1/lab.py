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

################################
# Functions & Frame Management #
################################

class Frame():
    builtinFrame: 'Frame'
    scheme_builtins = {
        "+": sum,
        "-": lambda args: -args[0] if len(args) == 1 else (args[0] - sum(args[1:])),
        "*": lambda args: 1 if len(args) == 0 else (args[0] * Frame.scheme_builtins["*"](args[1:])),
        "/": lambda args: 1/args[0] if len(args) == 1 else (args[0] / Frame.scheme_builtins["*"](args[1:]))
    }

    def __init__(self, enclosingFrame: 'Frame' = 'global', lexicalScoping: bool = True):
        """
        A Frame is a structure that binds certain attributes to names such as variables
        and functions. A frame keeps a reference to its parent frame, which can then be used
        to implement a proper lexical scoping scheme. For now, we allow lexical scoping when
        reading variables, but not writing to them.
        """
        self.varDict = dict()
        self.parentFrame = self.builtinFrame if (isinstance(enclosingFrame, str) 
                                                 and enclosingFrame == 'global') else enclosingFrame
        self.lexicalScoping = lexicalScoping

    def __setitem__(self, key, value):
        """
        Sets the variable FOR ONLY THE CURRENT FRAME. This does nothing to the enclosing frames.
        """
        self.varDict[key] = value

    def __getitem__(self, key):
        """
        Attempts to lookup the item in the current frame, and (if lexical scoping is enabled)
        continues the search in the enclosing frame. Returns a SchemeNameError if not found.
        """
        if key not in self.varDict:
            if self.lexicalScoping and self.parentFrame is not None:
                return self.parentFrame[key]
            else:
                raise SchemeNameError("Var {} not found in any enclosing frame.".format(key))
        
        return self.varDict[key]
    
    def __contains__(self, key):
        """
        Returns whether or not a key exists in the current frame or any enclosing
        frame, if lexical scoping is enabled.
        """
        return key in self.varDict or (self.lexicalScoping and 
                                       self.parentFrame is not None and 
                                       key in self.parentFrame)
    
    def __repr__(self) -> str:
        """ Representational view for debugging. """
        return "Frame {} - Parent {} - Vars {} - LS_ON: {}".format(id(self),
                                                                   id(self.parentFrame),
                                                                   self.varDict,
                                                                   self.lexicalScoping)

    @classmethod
    def create_global_frame(cls, varLookup: dict):
        cls.builtinFrame = Frame(None)
        cls.builtinFrame.varDict = varLookup

# Sets up the default frame without cluttering global namespace
Frame.create_global_frame(Frame.scheme_builtins)

class Function():
    def __init__(self, paramNames: list[str], funcTree: list, enclosingFrame: Frame):
        """
        A function holds a list of parameter names which are then mapped
        onto a funcTree which can be evaluated in the context of the parameters.
        To make things simpler, on call the function creates a 
        """
        self.enclosingFrame = enclosingFrame
        self.funcBody = funcTree
        self.argKws = paramNames

    def __call__(self, args):
        """
        Performs the actual function operations and frame creation (etc.) upon
        being invoked.
        """
        # Error out if function is improperly passed values
        if len(args) != len(self.argKws):
            raise SchemeEvaluationError("Function expecting inputs {}".format(self.argKws) +
                                        "received incorrect argument input {}.".format(args))

        # First create frame with proper scoping and bind vars positionally
        callFrame = Frame(self.enclosingFrame)
        for argName, argVal in zip(self.argKws, args):
            callFrame[argName] = argVal

        # Evaluate function body in frame and return value
        return evaluate(self.funcBody, callFrame)

    def __repr__(self) -> str:
        """
        Representation that might help a bit with debugging functions.s
        """
        return "Function {} with input positional args {}".format(id(self), self.argKws)


##############
# Evaluation #
##############


def result_and_frame(tree, curFrame: Frame = None):
    """
    Performs the same actions as evaluate but keeps track of
    the global frame if necessary.
    """
    if curFrame is None:
        curFrame = Frame()
        return evaluate(tree, curFrame), curFrame
    else:
        return evaluate(tree, curFrame), curFrame
    

def evaluate_func(tree, curFrame: Frame):
    """
    If a tree is not a simple returnable structure, attempt to look up
    reserved keywords, or, if no keyword exists, extract a named function
    observable from the current frame with that name and return that value.

    NOTE: This can potentially be split. Having the keywords together is
          convenient, but it's likely not necessary to have all the processing
          in this one function. It may even be better to have a class dedicated
          to keyword parsing to make this more easily observable.
    """
    # First identify keywords and then default to grabbing a function
    match tree[0]:
        case 'define':  # (define NAME EXPR) <- only three elems EXPR can be list|str|int?
            if len(tree) > 3:
                raise SchemeEvaluationError("Call to define had more than three elements.")
            
            if not isinstance(tree[1], list): # VAR DEFINITION
                newVarName = tree[1]
                curFrame[newVarName] = evaluate(tree[2], curFrame)
            else: # FUNC SHORTHAND -> (define (NAME PARAM1 PARAM2 ...) EXPR)
                newVarName = tree[1][0]
                curFrame[newVarName] = evaluate(['lambda', tree[1][1:], tree[2]], curFrame)
            
            return curFrame[newVarName]
        case 'lambda': # (lambda (PARAM1 PARAM2 ...) EXPR) <- only three elements
            if len(tree) > 3:
                raise SchemeEvaluationError("Lambda structure contained more than three elements.")
            elif not isinstance(tree[1], list):
                raise SchemeEvaluationError("Lambda arguments must be contained within parenthesis.")
            
            # defines the function and returns it
            varNames = tree[1]
            func = Function(varNames, tree[2], curFrame)
            return func
        case _:
            func = evaluate(tree[0], curFrame)
            if not callable(func):
                raise SchemeEvaluationError("Attempted to call uncallable object {}.".format(repr(func)))

            # And use the other values now as the arguments
            return func([evaluate(tree[tInd], curFrame) for tInd in range(1, len(tree))])


def evaluate(tree, curFrame: Frame = None):
    """
    Evaluate the given syntax tree according to the rules of the Scheme
    language.

    Arguments:
        tree (type varies): a fully parsed expression, as the output from the
                            parse function
    """
    # if there is no current frame, create one for this calculation
    if curFrame is None:
        curFrame = Frame()

    # edge cases
    if isinstance(tree, (float, int)):
        return tree
    elif isinstance(tree, str) and not isinstance(number_or_symbol(tree), (float, int)):
        if tree not in curFrame:
            raise SchemeNameError("Attempt to make call to undefined symbol {}.".format(tree))
        return curFrame[tree]
    elif isinstance(tree, list):
        return evaluate_func(tree, curFrame)
    else:
        raise SchemeSyntaxError("Unknown expression passed into eval: {}".format(tree))


def repl(verbose=False):
    """
    Read in a single line of user input, evaluate the expression, and print 
    out the result. Repeat until user inputs "QUIT"
    
    Arguments:
        verbose: optional argument, if True will display tokens and parsed
            expression in addition to more detailed error output.
    """
    import traceback
    _, frame = result_and_frame(['+'])  # make a global frame
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
            output, frame = result_and_frame(expression, frame)
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
