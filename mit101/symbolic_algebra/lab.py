"""
6.1010 Spring '23 Lab 10: Symbolic Algebra
"""

import doctest


# NO ADDITIONAL IMPORTS ALLOWED!
# You are welcome to modify the classes below, as well as to implement new
# classes and helper functions as necessary.

# NOTE: Tester seems to evaluate "entangled-ness" by making sure that the
#       function performs only one task per class, but in doing so the call to
#       the function is a bit more annoying to deal with if dealing with the
#       function completely recursively using a helper function. A nested function
#       would work but it's not worth decreasing the legibility of the class.

class Symbol:
    """
    The parent class for all symbols. A symbol is a representation of
    a function that may contain variables and numbers.
    """
    precedence = float("inf")
    right_parens = False
    left_parens = False

    def simplify(self):
        """ Variables and numbers simply return themselves. """
        return self.simplify_helper()[0]
    
    def simplify_helper(self) -> tuple['Symbol', bool]:
        """ The purpose of this helper is to return the proper instance
            along with a boolean value representing if it's a Num class """
        raise NotImplementedError("Subclass method not implemented properly.")

    def __add__(self, exprY):
        """ Computes the sum of two symbols X(self)+Y """
        return Add(self, exprY)
    
    def __radd__(self, exprX):
        """ Computes the sum of two symbols X+Y(self) """
        return Add(exprX, self)
    
    def __sub__(self, exprY):
        """ Computes the difference of two symbols X(self)-Y """
        return Sub(self, exprY)
    
    def __rsub__(self, exprX):
        """ Computes the difference of two symbols X-Y(self) """
        return Sub(exprX, self)
    
    def __mul__(self, exprY):
        """ Computes the product of two symbols X(self)*Y """
        return Mul(self, exprY)
    
    def __rmul__(self, exprX):
        """ Computes the product of two symbols X*Y(self) """
        return Mul(exprX, self)
    
    def __truediv__(self, exprY):
        """ Computes the division of two symbols X(self)/Y """
        return Div(self, exprY)
    
    def __rtruediv__(self, exprX):
        """ Computes the division of two symbols X/Y(self) """
        return Div(exprX, self)
    
    def __pow__(self, exprY):
        """ Computes the exponential of two symbols X(self)**Y """
        return Pow(self, exprY)

    def __rpow__(self, exprX):
        """ Computes the exponential of two symbols X**Y(self) """
        return Pow(exprX, self)


class Var(Symbol):
    def __init__(self, n):
        """
        Initializer.  Store an instance variable called `name`, containing the
        value passed in to the initializer.
        """
        self.name = n

    def simplify_helper(self):
        """ Variables do not need simplification. """
        return self, False

    def eval(self, lookupDict: dict[str, float|int]) -> float|int:
        """ Returns the variable value from a lookup dict if possible. """
        if self.name not in lookupDict:
            raise NameError("No valid value passed for the variable {}".format(self.name))
        
        return lookupDict[self.name]
    
    def deriv(self, wrtSymbol: str):
        """ Derivative of a linear symbol is 1 if in respect to that otherwise, 0 """
        if self.name != wrtSymbol:
            return Num(0)
        
        return Num(1)
    
    def __eq__(self, other) -> bool:
        return isinstance(other, type(self)) and other.name == self.name

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"Var('{self.name}')"


class Num(Symbol):
    def __init__(self, n):
        """
        Initializer.  Store an instance variable called `n`, containing the
        value passed in to the initializer.
        """
        self.n = n

    def simplify_helper(self):
        """ Nums do not need simplification, but can be simplified later. """
        return self, True

    def eval(self, *_) -> float|int:
        """ Evaluating a constant simply returns its value. """
        return self.n
    
    def deriv(self, *_):
        """ Derivative of any constant is 0 """
        return Num(0)
    
    def __eq__(self, other) -> bool:
        return isinstance(other, type(self)) and other.n == self.n

    def __str__(self) -> str:
        return str(self.n)

    def __repr__(self) -> str:
        return f"Num({self.n})"
    

class BinOp(Symbol):
    def __init__(self, left, right):
        """
        A binary operator is an operator that performs some sort of
        binary operation between two elements. Each subclass is
        expected to implement their personal (op) operator and their
        string representation as class attributes.
        """
        if isinstance(left, str):
            self.left = Var(left)
        elif isinstance(left, float) or isinstance(left, int):
            self.left = Num(left)
        else:
            self.left = left

        if isinstance(right, str):
            self.right = Var(right)
        elif isinstance(right, float) or isinstance(right, int):
            self.right = Num(right)
        else:
            self.right = right

    def eval(self, lookupDict: dict[str, float|int]) -> float|int:
        """
        Given a lookup dictionary, replace all unknown values with numerical
        representations and evaluate any given expression.
        """
        return self._op_(self.left.eval(lookupDict), self.right.eval(lookupDict))

    @classmethod
    def _op_(self, left, right):
        """ Performs a pre-specified operation between two values. """
        raise NotImplementedError("Subclass operation not properly implemented.")
    
    def __eq__(self, other) -> bool:
        """ Recursively implements equality checking on the operation. """
        return (isinstance(other, type(self)) and 
                self.left == other.left and
                self.right == other.right)

    def __str__(self) -> str:
        lStr = "("+str(self.left)+")" if ((self.left.precedence < self.precedence) or
                                          (self.left.precedence == self.precedence and self.left_parens)) else str(self.left)
        rStr = "("+str(self.right)+")" if ((self.right.precedence < self.precedence) or
                                           (self.right.precedence == self.precedence and self.right_parens)) else str(self.right)
        return lStr + " " + self.OP_VAL + " " + rStr

    def __repr__(self) -> str:
        return "{}({}, {})".format(self.__class__.__name__, 
                                  self.left.__repr__(),
                                  self.right.__repr__())


class Add(BinOp):
    """
    Binary operator that represents the addition function.
    """
    OP_VAL = "+"
    precedence = 2

    def simplify(self):
        """ Wrapper to return proper outputs from the helper """
        return __class__.simplify_helper(self)[0]
    
    def simplify_helper(self):
        """ Simplifies terms with unnecessary zeroes within the element. """
        newLeft, lIsNum = self.left.simplify_helper()
        newRight, rIsNum = self.right.simplify_helper()

        if lIsNum and rIsNum:
            return Num(self._op_(newLeft.eval(), newRight.eval())), True
        elif lIsNum and newLeft.eval() == 0:
            return newRight, False
        elif rIsNum and newRight.eval() == 0:
            return newLeft, False
        
        return Add(newLeft, newRight), False

    @classmethod
    def _op_(cls, left, right) -> float|int:
        return left + right
    
    def deriv(self, wrtSymbol: str):
        """ f'(x+y) = f'(x) + f'(y) """
        return Add(self.left.deriv(wrtSymbol), self.right.deriv(wrtSymbol))


class Sub(BinOp):
    """
    Binary operator that represents the subtraction function.
    """
    OP_VAL = "-"
    precedence = 2
    right_parens = True

    def simplify(self):
        """ Wrapper to return only the symbol part of the helper. """
        return __class__.simplify_helper(self)[0]

    def simplify_helper(self):
        """ Removes unnecessary zeroes within subtraction ops """
        newLeft, lIsNum = self.left.simplify_helper()
        newRight, rIsNum = self.right.simplify_helper()

        if lIsNum and rIsNum:
            return Num(self._op_(newLeft.eval(), newRight.eval())), True
        elif rIsNum and newRight.eval() == 0:
            return newLeft, False
            
        return Sub(newLeft, newRight), False

    @classmethod
    def _op_(cls, left, right) -> float|int:
        return left - right

    def deriv(self, wrtSymbol: str):
        """ f'(x-y) = f'(x) - f'(y) """
        return Sub(self.left.deriv(wrtSymbol), self.right.deriv(wrtSymbol))


class Mul(BinOp):
    """
    Binary operator that represents the multiplication function.
    """
    OP_VAL = "*"
    precedence = 3

    def simplify(self):
        """ Wrapper around the helper to return only the symbol. """
        return __class__.simplify_helper(self)[0]

    def simplify_helper(self):
        """ Removes unnecessary ones and zeroes from multiplication ops """
        newLeft, lIsNum = self.left.simplify_helper()
        newRight, rIsNum = self.right.simplify_helper()

        if lIsNum and rIsNum:
            return Num(self._op_(newLeft.eval(), newRight.eval())), True
        elif lIsNum and newLeft.eval() == 1:
            return newRight, False
        elif rIsNum and newRight.eval() == 1:
            return newLeft, False
        elif ((lIsNum and newLeft.eval() == 0) or
                (rIsNum and newRight.eval() == 0)):
            return Num(0), True
        
        return Mul(newLeft, newRight), False

    @classmethod
    def _op_(cls, left, right) -> float|int:
        return left * right
    
    def deriv(self, wrtSymbol: str):
        """ f'(xy) = x*f'(y)+y*f'(x) """
        return Add(Mul(self.left, self.right.deriv(wrtSymbol)), Mul(self.right, self.left.deriv(wrtSymbol)))


class Div(BinOp):
    """
    Binary operator that represents the division function.
    """
    OP_VAL = "/"
    precedence = 3
    right_parens = True

    def simplify(self):
        """ Wrapper around the helper to return only the symbol. """
        return __class__.simplify_helper(self)[0]
    
    def simplify_helper(self):
        """ Removes unnecessary zeroes and ones from division ops """
        newLeft, lIsNum = self.left.simplify_helper()
        newRight, rIsNum = self.right.simplify_helper()

        if lIsNum and rIsNum:
            return Num(self._op_(newLeft.eval(), newRight.eval())), True
        elif lIsNum and newLeft.eval() == 0:
            return Num(0), True
        elif rIsNum and newRight.eval() == 1:
            return newLeft, False
            
        return Div(newLeft, newRight), False

    @classmethod
    def _op_(cls, left, right) -> float|int:
        return left / right
    
    def deriv(self, wrtSymbol: str):
        """ f'(x/y) = [yf'(x) - xf'(y)]/[y*y] """
        return Div(Sub(Mul(self.right, self.left.deriv(wrtSymbol)), 
                       Mul(self.left, self.right.deriv(wrtSymbol))),
                   Mul(self.right, self.right))
    
class Pow(BinOp):
    """
    Binary operator that represents exponentiation.
    """
    OP_VAL = "**"
    precedence = 4
    left_parens = True

    def simplify(self):
        """ Wrapper around the helper to return only the symbol. """
        return __class__.simplify_helper(self)[0]
    
    def simplify_helper(self) -> tuple[Symbol, bool]:
        """ Removes unnecessary ones and zeroes from exponentiation ops """
        newLeft, lIsNum = self.left.simplify_helper()
        newRight, rIsNum = self.right.simplify_helper()

        if lIsNum and rIsNum:
            return Num(self._op_(newLeft.eval(), newRight.eval())), True
        elif rIsNum and newRight.eval() == 0:
            return Num(1), True
        elif rIsNum and newRight.eval() == 1:
            return newLeft, False
        elif lIsNum and newLeft.eval() == 0:
            return Num(0), True
        
        return Pow(newLeft, newRight), False
    
    @classmethod
    def _op_(cls, left, right) -> float|int:
        return left**right
    
    def deriv(self, wrtSymbol: str):
        """ f'(u**n) = n*u**(n-1) * f'(u) """
        if not isinstance(self.right, Num):
            raise TypeError("Exponential value is not numerical. Derivative cannot be calculated")
        
        return Mul(Mul(self.right, Pow(self.left, Sub(self.right, 1))), 
                   self.left.deriv(wrtSymbol))
    

def expression(inStr: str):
    """
    Given an input expression, returns a symbolic form representation of
    the input by doing a little bit of preprocessing.
    """
    return parse(tokenize(inStr))


def extractSubexpr(inList: list[str], sInd: int) -> list[str]:
    """
    Given the known list of tokens, find the entire subexpression
    starting from a known "(" instance by finding the corresponding
    ")" instance.
    """
    parenDepth = 1
    subExpr = list()
    while parenDepth > 0:
        sInd += 1

        if inList[sInd] == ")":
            parenDepth -= 1
        elif inList[sInd] == "(":
            parenDepth += 1
        
        subExpr.append(inList[sInd])
    
    return subExpr[:-1]


def parse(inList: list[str]) -> Symbol:
    """
    Converts a list of tokens into an appropriate symbol.
    """
    opDict = {"*": Mul, "-": Sub, "+": Add, "/": Div, "^": Pow}
    
    # prepare for recursive assignment of symbols
    curOp, leftTerm, rightTerm = None, None, None
    newTok = None   # holder for assignment
    sInd = 0
    while sInd < len(inList):
        if inList[sInd] == "(": # extract subexpression and process rest
            subexpr = extractSubexpr(inList, sInd)
            newTok = parse(subexpr)
            sInd += len(subexpr) + 1
        elif inList[sInd] in opDict:
            curOp = opDict[inList[sInd]]
        elif inList[sInd].isalpha():
            newTok = Var(inList[sInd])
        else:  # must be a number
            newTok = (Num(float(inList[sInd])) if "." in inList[sInd]
                        else Num(int(inList[sInd])))
            
        # Assign new term to new spot
        if newTok and leftTerm is None:
            leftTerm = newTok
        elif newTok and rightTerm is None:
            rightTerm = newTok
        
        # then move to next potential candidate
        sInd += 1
        newTok = None

    return curOp(leftTerm, rightTerm) if curOp is not None else leftTerm


def tokenize(inStr: str) -> list[str]:
    """
    Takes in a string input that is expected to be a proper symbolic
    representation and returns a list representing the specific tokens
    within the string.
    """
    specialToks = {"(", ")", "+", "/", "*", "^"}
    negRelToks = specialToks.difference({")"})|{"-"}
    negTok = "-"

    # parse string
    unformatted = inStr.replace(" ", "") # get rid of whitespace in string
    unformatted = unformatted.replace("**", "^") # allows us to identify exponents easily
    curTok = ""
    tokList = list()
    foundNeg = False
    for sInd in range(len(unformatted)):
        if unformatted[sInd] in specialToks: # immediately add to list is operator
            if curTok != "":
                tokList.append(negTok*foundNeg+curTok)  # and add any parsed variables/numbers
                foundNeg = False
                curTok = ""
            tokList.append(unformatted[sInd])
        elif unformatted[sInd] == negTok:
            if curTok: # negative found after a token, must be subtraction
                tokList.append(negTok*foundNeg+curTok)
                tokList.append(negTok)
                foundNeg = False
                curTok = ""
            elif not tokList or tokList[-1] in negRelToks:  # negative in other cases
                foundNeg = True
            else:                                   # otherwise just treat as subtraction
                tokList.append(unformatted[sInd])
        elif unformatted[sInd].isalpha():
            tokList.append(unformatted[sInd])
        elif unformatted[sInd].isdigit() or unformatted[sInd]==".":
            curTok += unformatted[sInd]
        else:   # this shouldn't happen with any terms unless algo is wrong
            raise ValueError("Passed strong contains unknown symbols.")
        
    # Add final value if necessary
    if curTok:
        tokList.append(negTok*foundNeg+curTok)
    
    return tokList


if __name__ == "__main__":
    doctest.testmod()

