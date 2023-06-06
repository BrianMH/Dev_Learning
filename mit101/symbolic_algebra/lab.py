"""
6.1010 Spring '23 Lab 10: Symbolic Algebra
"""

import doctest

# NO ADDITIONAL IMPORTS ALLOWED!
# You are welcome to modify the classes below, as well as to implement new
# classes and helper functions as necessary.


class Symbol:
    """
    The parent class for all symbols. A symbol is a representation of
    a function that may contain variables and numbers.
    """
    precedence = float("inf")
    right_parens = False

    def simplify(self):
        """ Variables and numbers simply return themselves. """
        return self

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


class Var(Symbol):
    def __init__(self, n):
        """
        Initializer.  Store an instance variable called `name`, containing the
        value passed in to the initializer.
        """
        self.name = n

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

    def simplify(self):
        """ Performs a simplification of the operator given known characteristics """
        raise NotImplementedError("Subclass simplification not properly implemented.")

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
        lStr = "("+str(self.left)+")" if self.left.precedence < self.precedence else str(self.left)
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
        """ Simplifies terms with unnecessary zeroes within the element. """
        newLeft = self.left.simplify()
        newRight = self.right.simplify()

        if isinstance(newLeft, Num) and isinstance(newRight, Num):
            return Num(self._op_(newLeft.eval(), newRight.eval()))
        elif isinstance(newLeft, Num) and newLeft.eval() == 0:
            return newRight
        elif isinstance(newRight, Num) and newRight.eval() == 0:
            return newLeft
        
        return Add(newLeft, newRight)

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
        """ Removes unnecessary zeroes within subtraction ops """
        newLeft = self.left.simplify()
        newRight = self.right.simplify()

        if isinstance(newLeft, Num) and isinstance(newRight, Num):
            return Num(self._op_(newLeft.eval(), newRight.eval()))
        elif isinstance(newRight, Num) and newRight.eval() == 0:
            return newLeft
            
        return Sub(newLeft, newRight)

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
        """ Removes unnecessary ones and zeroes from multiplication ops """
        newLeft = self.left.simplify()
        newRight = self.right.simplify()

        if isinstance(newLeft, Num) and isinstance(newRight, Num):
            return Num(self._op_(newLeft.eval(), newRight.eval()))
        elif isinstance(newLeft, Num) and newLeft.eval() == 1:
            return newRight
        elif isinstance(newRight, Num) and newRight.eval() == 1:
            return newLeft
        elif ((isinstance(newLeft, Num) and newLeft.eval() == 0) or
                (isinstance(newRight, Num) and newRight.eval() == 0)):
            return Num(0)
        
        return Mul(newLeft, newRight)

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
        """ Removes unnecessary zeroes and ones from division ops """
        newLeft = self.left.simplify()
        newRight = self.right.simplify()

        if isinstance(newLeft, Num) and isinstance(newRight, Num):
            return Num(self._op_(newLeft.eval(), newRight.eval()))
        elif isinstance(newLeft, Num) and newLeft.eval() == 0:
            return Num(0)
        elif isinstance(newRight, Num) and newRight.eval() == 1:
            return newLeft
            
        return Div(newLeft, newRight)

    @classmethod
    def _op_(cls, left, right) -> float|int:
        return left / right
    
    def deriv(self, wrtSymbol: str):
        """ f'(x/y) = [yf'(x) - xf'(y)]/[y*y] """
        return Div(Sub(Mul(self.right, self.left.deriv(wrtSymbol)), 
                       Mul(self.left, self.right.deriv(wrtSymbol))),
                   Mul(self.right, self.right))


if __name__ == "__main__":
    doctest.testmod()

    test = Mul(Var('z'), Div(Num(0), Var('x'))).simplify()
    print(str(test))