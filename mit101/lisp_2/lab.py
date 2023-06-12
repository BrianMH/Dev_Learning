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


###############################################
# Intrinsic Objects and List Helper Functions #
###############################################

class Pair():
    def __init__(self, args):
        """
        A pair represents a tuple that holds two values. In this scheme system,
        since a pair can hold any value, these internal variables are also able
        to hold other pairs (which allows the system to implement what is 
        functionally a linked list.)
        """
        if len(args) != 2:
            raise SchemeEvaluationError("Cons received incorrect number of input arguments.")

        self.car, self.cdr = args

    @staticmethod
    def consGetCar(args):
        """ Returns the first element of the pair. (Type-safe static method) """
        if len(args) != 1 or not isinstance(args[0], Pair):
            raise SchemeEvaluationError("Object is not a proper cons object.")
        return args[0].car
    
    @staticmethod
    def consGetCdr(args):
        """ Returns the second element of the pair. (Type-safe static method) """
        if len(args) != 1 or not isinstance(args[0], Pair):
            raise SchemeEvaluationError("Object is not a proper cons object.")
        return args[0].cdr

    def __repr__(self) -> str:
        return "(cons (i:{}) {} {})".format(id(self), repr(self.car), repr(self.cdr))

    def __str__(self) -> str:
        return "(cons {} {})".format(str(self.car), str(self.cdr))


class Nil:    
    def __init__(self):
        """ A Nil object is similar to a None object in python. It has
            no intrinsic value, it can be compared to other objects but
            has no qualifying features other than not being equivalent to
            any other object. """
        
    def __eq__(self, other):
        return isinstance(other, type(self))
    
    def __neq__(self, other):
        return not isinstance(other, type(self))
    
    def __repr__(self) -> str:
        return "nil"
    
    def __str__(self) -> str:
        return "nil"
    

def listPresenceHelper(inList):
    """ 
    Returns True if the input is a list. False, otherwise. 
        
    ARG_DEFINITION: (list? OBJECT)
    """
    if isinstance(inList, list):
        if len(inList) > 1:
            raise SchemeEvaluationError("Passed in more than one argument into (length?).")
        inList = inList[0]

    if isinstance(inList, Nil):
        return True
    elif not isinstance(inList, Pair):
        return False
    
    return listPresenceHelper(inList.cdr)

def listLengthHelper(inList):
    """ 
    Determines the length of a passed in list. Raises an exception if
    the input is not a proper list.

    ARG_DEFINITION: (length LIST)
    """
    if not listPresenceHelper(inList):
        raise SchemeEvaluationError("Input was malformed or not a list.")
    
    listLen = 0
    curNode = inList[0]
    while not isinstance(curNode, Nil):
        curNode = curNode.cdr
        listLen += 1
    
    return listLen

def listIndexHelper(args):
    """ 
    Finds the specific index of a list. Raises an exception if certain
    attributes don't make sense or the index passed is larger than the 
    size of the list.

    ARG_DEFINITION: (list-ref LIST INDEX)
    """
    if len(args) != 2:
        raise SchemeEvaluationError("list-ref received more than two inputs.")
    
    listInput = args[0]
    indexInput = args[1]
    isList = listPresenceHelper(listInput)
    if not isList and isinstance(listInput, Pair):
        if indexInput == 0:
            return listInput.car
        else:
            raise SchemeEvaluationError("Cannot retreive non-zero indices of non-list cons.")
    elif not isList:
        raise SchemeEvaluationError("list-ref receive unknown object type.")
    else:
        # iterate until we hit the right element
        curNode = listInput
        for _ in range(indexInput):
            if isinstance(curNode, Nil):
                break
            curNode = curNode.cdr
        
        # enforce that current node exists
        if isinstance(curNode, Nil):
            raise SchemeEvaluationError("List index out of bounds.")
        
        return curNode.car


def listConcatHelper(args):
    """
    Concatenates all lists passed into the argument. All elements
    must be lists or the method will throw an exception.

    ARG_DEFINITION: (append LIST1 LIST2 LIST3 LIST4 ...)
    """
    finList = Nil()
    curNode = None

    for listInd in range(len(args)):
        # Ensure input is a list befor eappending
        if not listPresenceHelper(args[listInd]):
            raise SchemeEvaluationError("Input passed to append was not a proper list.")
        
        # Then copy elements while not nil
        curCopyElem = args[listInd]
        while not isinstance(curCopyElem, Nil):
            if isinstance(finList, Nil):
                finList = Pair([curCopyElem.car, Nil()])
                curNode = finList
            else:
                curNode.cdr = Pair([curCopyElem.car, Nil()])
                curNode = curNode.cdr
            
            curCopyElem = curCopyElem.cdr

    # finally, return list head
    return finList


def listMap(args):
    """
    Like a typical map function, this map applies a given passed function to
    each element of the list individually.

    ARG_DEFINITION: (map FUNCTION LIST)
    """
    # extract values and verify inputs
    func = args[0]
    curListElem = args[1]
    if len(args) != 2:
        raise SchemeEvaluationError("More than two arguments passed to map function.")
    elif not listPresenceHelper(curListElem):
        raise SchemeEvaluationError("Map LIST argument must be a proper list.")

    # Then proceed to apply the function to create a new list
    retList = Nil()
    retListElem = None
    while not isinstance(curListElem, Nil):
        if isinstance(retList, Nil):
            retList = Pair([func([curListElem.car]), Nil()])
            retListElem = retList
        else:
            retListElem.cdr = Pair([func([curListElem.car]), Nil()])
            retListElem = retListElem.cdr

        curListElem = curListElem.cdr
    
    return retList


def listFilter(args):
    """
    Again, like a typical filter function, this only copies elements from the passed list
    to another list ONLY if the predicate function evaluated with the current list value
    is True.

    ARG_DEFINITION: (filter FUNCTION LIST)
    """
    # extract values and verify inputs
    filterFunc = args[0]
    curListElem = args[1]
    if len(args) != 2:
        raise SchemeEvaluationError("More than two arguments passed to filter function.")
    elif not listPresenceHelper(curListElem):
        raise SchemeEvaluationError("Filter LIST argument must be a proper list.")

    # Then proceed to filter the given list to create a new list
    retList = Nil()
    retListElem = None
    while not isinstance(curListElem, Nil):
        if filterFunc([curListElem.car]):   # only copy when TRUE
            if isinstance(retList, Nil):
                retList = Pair([curListElem.car, Nil()])
                retListElem = retList
            else:
                retListElem.cdr = Pair([curListElem.car, Nil()])
                retListElem = retListElem.cdr

        curListElem = curListElem.cdr   # but still investigate other entries
    
    return retList


def listReduce(args):
    """
    Finally, our reduce takes a given list and applies a function collectively and 
    cummulatively across all of the list given some initial value.

    ARG_DEFINITION: (reduce FUNCTION LIST INITVAL)
    """
    # extract values and verify inputs
    redFunc = args[0]
    curListElem = args[1]
    curVal = args[2]
    if len(args) != 3:
        raise SchemeEvaluationError("More than three arguments passed to map function.")
    elif not listPresenceHelper(curListElem):
        raise SchemeEvaluationError("Reduce LIST argument must be a list.")
    
    # Then proceed to process reduction of values
    while not isinstance(curListElem, Nil):
        curVal = redFunc([curVal, curListElem.car])
        curListElem = curListElem.cdr

    return curVal


################################
# Functions & Frame Management #
################################

class LogicFunctions():
    """
    A namespace for logic evaluation functions that would normally clutter
    the global namespace. Allows us to create built-in funcs that support exception
    throwing within the global frame and implement short-circuiting.
    """
    @staticmethod
    def external_not(args):
        """
        Given a list input (args) containing only a single element, return the logical
        NOT of that value.
        """
        if len(args) != 1:
            raise SchemeEvaluationError("Function not can only receive a single value.")
        
        return not args[0]
    
    @staticmethod
    def recursive_comparator(args, func):
        """ 
        Implements a comparator for args (A1, A2, ...) of logical related form
        func(A1, A2) AND func(A2, A3) AND func(A3, A4) AND ...

        This is used to keep the repetition to a minimum for short-circuitable logical
        operators.
        """
        for eInd in range(len(args)-1):
            if not func(args[eInd], args[eInd+1]):
                return False
            
        return True
    

class Frame():
    builtinFrame: 'Frame'
    scheme_builtins = {
        # arithmetic constructs
        "+": sum,
        "-": lambda args: -args[0] if len(args) == 1 else (args[0] - sum(args[1:])),
        "*": lambda args: 1 if len(args) == 0 else (args[0] * Frame.scheme_builtins["*"](args[1:])),
        "/": lambda args: 1/args[0] if len(args) == 1 else (args[0] / Frame.scheme_builtins["*"](args[1:])),

        # Cons object creation and manipulation
        "cons": lambda args: Pair(args),
        "car": lambda cons: Pair.consGetCar(cons),
        "cdr": lambda cons: Pair.consGetCdr(cons),

        # List object creation and related methods
        "list": lambda args: Nil() if len(args) == 0 else Pair([args[0], 
                                                                Frame.scheme_builtins["list"](args[1:])]),
        "list?": lambda args: listPresenceHelper(args),
        "length": lambda args: listLengthHelper(args),
        "list-ref": lambda args: listIndexHelper(args),
        "append": lambda args: listConcatHelper(args),
        "map": lambda args: listMap(args),
        "filter": lambda args: listFilter(args),
        "reduce": lambda args: listReduce(args),

        # Logical operators
        "equal?": lambda args: True if len(args) == 1 else ((args[0] == args[1]) and 
                                                            Frame.scheme_builtins["equal?"](args[1:])),
        ">": lambda args: LogicFunctions.recursive_comparator(args, lambda x,y:x>y),
        ">=": lambda args: LogicFunctions.recursive_comparator(args, lambda x,y:x>=y),
        "<": lambda args: LogicFunctions.recursive_comparator(args, lambda x,y:x<y),
        "<=": lambda args: LogicFunctions.recursive_comparator(args, lambda x,y:x<=y),
        "not": lambda args: LogicFunctions.external_not(args),

        # Basic constants
        "#t": True,
        "#f": False,
        "nil": Nil()
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
        To make things simpler, on call the function creates the necessary references
        to create the call frame when invoking the function.
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
        Representation that might help a bit with debugging functions.
        """
        return "Function {} with input positional args {}".format(id(self), self.argKws)


##############
# Evaluation #
##############

class Keywords:
    """
    Represents the collection of functions that is used by our scheme program to 
    implement some keyword functionalities. This is just a container class as there
    is no functional use for separating these functions into a class of their own.
    This is just moving stuff around to function almost like an imported module.

    This class' processor can be automatically initialized to evaluate to any defined
    methods by properly calling the updateMethods function, which reads the class
    methods and adds them to the processor.
    """
    @staticmethod
    def _define(tree, curFrame):
        if len(tree) > 3:
            raise SchemeEvaluationError("Call to define had more than three elements.")
        
        if not isinstance(tree[1], list): # VAR DEFINITION
            newVarName = tree[1]
            curFrame[newVarName] = evaluate(tree[2], curFrame)
        else: # FUNC SHORTHAND -> (define (NAME PARAM1 PARAM2 ...) EXPR)
            newVarName = tree[1][0]
            curFrame[newVarName] = evaluate(['lambda', tree[1][1:], tree[2]], curFrame)
        
        return curFrame[newVarName]
    
    @staticmethod
    def _lambda(tree, curFrame):
        if len(tree) > 3:
            raise SchemeEvaluationError("Lambda structure contained more than three elements.")
        elif not isinstance(tree[1], list):
            raise SchemeEvaluationError("Lambda arguments must be contained within parenthesis.")
        
        # defines the function and returns it
        varNames = tree[1]
        func = Function(varNames, tree[2], curFrame)
        return func
    
    @staticmethod
    def _if(tree, curFrame):
        if len(tree) != 4:
            raise SchemeEvaluationError("Special form IF did not receive exactly three inputs.")
        
        if evaluate(tree[1], curFrame):
            return evaluate(tree[2], curFrame)
        else:
            return evaluate(tree[3], curFrame)
    
    @staticmethod
    def _and(tree, curFrame):
        toRet = True
        for subExpr in tree[1:]:
            if not toRet:
                break
            toRet &= evaluate(subExpr, curFrame)

        return toRet        

    @staticmethod
    def _or(tree, curFrame):
        toRet = False
        for subExpr in tree[1:]:
            if toRet:
                break
            toRet |= evaluate(subExpr, curFrame)
        
        return toRet


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
    # empty tree
    if len(tree) == 0:
        raise SchemeEvaluationError("Empty structure detected.")

    # First identify keywords and then default to grabbing a function
    if isinstance(tree[0], str) and hasattr(Keywords, '_'+tree[0]):
        return getattr(Keywords, '_'+tree[0])(tree, curFrame)
    else:
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
