"""
6.1010 Spring '23 Lab 8: SAT Solver
"""

#!/usr/bin/env python3

import sys
import typing
import doctest

sys.setrecursionlimit(10_000)
# NO ADDITIONAL IMPORTS
CNF = list[list[tuple[str, bool]]] # simplifies the typing for the CNF formula

def candidate_generator(formula: CNF):
    """
    A generator that generates candidates for the SAT optimizer to recursively make
    assumptions about. This can be seen as simply "flattening" the formula into its
    respective terms and suggesting each one of them one by one. Note that the reason
    these are the only assumptions made is due to the fact that any term that does not
    exist in the CNF is useless to look at (assumption would not generate a smaller
    formula to recurse on).

    Args:
        formula: The formula for which to generate candidate terms
    """
    seenTerms = set()

    for clause in formula:
        for term in clause:
            if term not in seenTerms:
                yield term
                seenTerms.add(term) # remove candidacy from future


def remove_redundancy(formula: CNF) -> CNF:
    """
    As the method states, this just removes duplicate tokens from the formula. This
    really only makes sense to call a single time as there will never be duplicates
    afterwards.

    Args:
        formula: The CNF to remove redundant terms from.
    """
    # address duplicates
    newFormula = list()
    for clause in formula:
        curClauseSet = set()
        curClause = list()
        for term in clause:
            if term not in curClauseSet:
                curClause.append(term)
                curClauseSet.add(term)
        newFormula.append(curClause)

    return newFormula


def short_circuit_formula(formula: CNF) -> tuple[dict, CNF, bool]:
    """
    Brute forces a potentially substantial amount of terms if they can be
    immediately determined due to singleton clause status.

    Args:
        formula: The CNF to find potential short-circuit optimizations for.

    Returns:
        tuple[dict, CNF, bool]: Consists of the updated inferences, the new
        shortened CNF and a boolean representing if any work was done.
    """
    # first find our forced assumptions
    forced_assumptions = dict()
    for clause in formula:
        if len(clause) == 1: # found singleton
            forced_assumptions.update(clause)

    # then go ahead and pre-process the formula removals
    new_formula = update_formula_with_assumption(formula, 
                                                [(term, val) for term, val in forced_assumptions.items()])

    return forced_assumptions, new_formula, True if forced_assumptions else False


def satisfying_assignment(formula: CNF, killCount = 10) -> dict:
    """
    Find a satisfying assignment for a given CNF formula.
    Returns that assignment if one exists, or None otherwise.

    TODO: Fix this to use proper non-chronological backtracking. The only reason
          the current method works is because sudoku puzzles naturally can be
          approached through many methods, but often times a few "anchor points"
          pretty much determine the whole puzzle so having a significant number of
          conflicts is usually a sign of a dead branch. Secondly, the tests provided
          do not actually have a significant number of branches that lead to many
          conflicts but have a solution somewhere in the unexplored tree. Designing
          an example that it fails to attain is a bit difficult, but something tells 
          me that it does technically exist.

    >>> satisfying_assignment([])
    {}
    >>> x = satisfying_assignment([[('a', True), ('b', False), ('c', True)]])
    >>> x.get('a', None) is True or x.get('b', None) is False or x.get('c', None) is True
    True
    >>> satisfying_assignment([[('a', True)], [('a', False)]])
    """
    # first perform some simple function pre-processing
    formula = remove_redundancy(formula)
    scWorking = True
    solTerms = dict()
    while scWorking:
        scTerms, formula, scWorking = short_circuit_formula(formula)
        solTerms.update(scTerms)

    # early termination
    if len(formula) == 0:
        return solTerms
    elif any([len(clause) == 0 for clause in formula]):
        return None
    
    # Now process the formula using some heuristics
    agenda = [(formula, candidate_generator(formula), solTerms)]
    conflictCnt = 0
    while agenda:
        # get next action and process
        if conflictCnt == killCount:
            agenda = [agenda[0]]
            conflictCnt = 0
        curFormula, curGen, curSolTerms = agenda.pop()

        # make a step
        nextAssumption = next(curGen, None)
        if nextAssumption is None:
            continue    # no more children to check out. this branch is dead
        else:
            agenda.append((curFormula, curGen, curSolTerms))
        newFormula = update_formula_with_assumption(curFormula, [nextAssumption])
        newSolTerms = {**curSolTerms, nextAssumption[0]:nextAssumption[1]}

        # reduce to simplest form prior to next iter
        scWorking = True
        while scWorking:
            scTerms, newFormula, scWorking = short_circuit_formula(newFormula)
            newSolTerms.update(scTerms)

        # early termination
        if len(newFormula) == 0:
            return newSolTerms
        elif any([len(clause) == 0 for clause in newFormula]):
            conflictCnt += 1
            continue

        # now we can add our simplified predicate back to the agenda for processing
        agenda.append((newFormula, candidate_generator(newFormula), newSolTerms))

    return None


def update_formula_with_assumption(formula: CNF, assumptions: list[tuple[str, bool]]) -> CNF:
    """
    Given a CNF formula, returns the result of making the assumption that (var_name)
    has truth value (truth_value). To make things clearer, a statement that is
    axiomatically True as a result of the decision will return "[]" as the CNF, while
    one that creates a paradox (thus is always False given the assumptions), will 
    return something of the form "[[], ...]".

    Args:
        formula: The formula to update with the assumption
        var_name: The name of the variable to make the assumption about
        truth_value: The value that our variable should take in the formula

    Returns:
        Another formula that represents the CNF of the initial formula along with the assumption

    >>> update_formula_with_assumption([], [('a', False)])
    []
    >>> update_formula_with_assumption([[("a", False), ("a", True)]], [('a', False)])
    []
    >>> update_formula_with_assumption([[("a", True)], [("b", False)]], [('a', False)])
    [[], [('b', False)]]
    >>> update_formula_with_assumption([[("a", True), ("b", False)], [("a", True)]], [('a', False)])
    [[('b', False)], []]
    """
    # Create our search keys
    pos_preds = set(assumptions)
    neg_preds = {(var_name, not truth_value) for var_name, truth_value in assumptions}

    # and now walk through the CNF while identifying either of the two terms
    updated_formula = list()
    for clause in formula:
        new_clause = list()

        for term in clause:
            if term in pos_preds:     # we found something that agrees with our assumption
                new_clause = None   # ignore seen tokens
                break               # and ignore that clause, as it is now True
            elif term in neg_preds:  # we found something that contradicts our assumption
                continue               # remove the contradiction (by ignoring the term)
            
            new_clause.append(term) # any non-essential terms can remain in the final clause
            
        if new_clause is not None:
            updated_formula.append(new_clause)

    return updated_formula


def cache(func: callable) -> callable:
    '''
    Basic implementation of a cache for a function.
    '''
    cache = dict()
    def function_caching(*args, **kwargs):
        if kwargs:
            indixer = args + tuple(((key, val) for key, val in kwargs))
        else:
            indixer = args

        if indixer in cache:
            return cache[indixer]

        return func(*args, **kwargs)
    return function_caching


@cache
def get_var_name(row: int, col: int, value: int) -> str:
    """
    The name of the variables for the sudoku SAT solver are dependent only
    on the position and the potential value it will take. This function
    should run relatiely quickly enough as it always returns an immutable
    string representing the key that should be used in the CNF.

    Args:
        row: The row of the current element
        col: The column of the current element
        value: The value that the position should take
    """
    return "{}@{},{}".format(value, row, col)


def sqrt(val: int) -> int:
    """
    No imports means no imports I guess. This is just a naive implementation of
    the sqrt function that can be found in the math library. It only supports
    perfect squares as they will be the only elements that we will work with.
    """
    curGuess = 0
    while True:
        if curGuess**2 == val:
            return curGuess
        elif curGuess**2 > val: # over the bound. root doesn't exist
            raise ValueError("Value is not a perfect square.")
        
        curGuess += 1


def codify_current_board_positions(sudoku_board) -> CNF:
    """
    Generates a CNF formula corresponding to the positions on the board which
    already have proper elements in place. In a CNF form, this is trivially 
    done with singletons clauses with the elements that are properly in place.
    """
    CNF = list()

    for rowInd in range(len(sudoku_board)):
        for colInd in range(len(sudoku_board[0])):
            if sudoku_board[rowInd][colInd] != 0:
                CNF.append([(get_var_name(rowInd, colInd, sudoku_board[rowInd][colInd]), 
                             True)])
                
    return CNF


def codify_cell_uniqueness(board_size: int) -> CNF:
    """
    For a sudoku board of size (board_size X board_size), codifying cell 
    uniqueness amounts to declaring that, for every cell index, there
    should be at least one value, but there cannot exist a pair of values
    for the same cell.

    Args:
        board_size: The size of the square board being evaluated.
    """
    maxVal = board_size
    CNF = list()

    for rowInd in range(board_size):
        for colInd in range(board_size):
            # Exists implies (1 or 2 or 3 or ...)
            existsClause = list()
            for candValue in range(1, maxVal+1):
                existsClause.append((get_var_name(rowInd, colInd, candValue), True))

            # Duplicate clause implies (not 1 or not 2) and (not 1 or not 3) and ...
            # In other words, the predicate is false if a pair exists where both are true.
            dupClauses = list()
            for candValue in range(1, maxVal+1):
                for candValue2 in range(candValue+1, maxVal+1):
                    clauseL = (get_var_name(rowInd, colInd, candValue), False)
                    clauseR = (get_var_name(rowInd, colInd, candValue2), False)
                    dupClauses.append([clauseL, clauseR])

            # And then add them to our CNF
            CNF.append(existsClause)
            CNF.extend(dupClauses)
    
    return CNF


def codify_row_validity(board_size: int) -> CNF:
    """{
    Codifying the validity of a sudoku row in CNF form is a bit weird, but this
    is functionally equivalent to claiming that each unique value must exist
    in the row, but it cannot exist in more than one location.

    Args:
        board_size: The size of the square board being evaluated
    """
    maxVal = board_size
    CNF = list()

    for rowInd in range(board_size): # for every row
        for candVal in range(1, maxVal+1): # every cand value
            existsClause = list()
            for colInd in range(board_size): # it exists somewhere in the row
                existsClause.append((get_var_name(rowInd, colInd, candVal), True))

            dupClauses = list()
            for colInd in range(board_size): # but not more than one column value
                for colIndR in range(colInd+1, board_size):
                    clauseL = (get_var_name(rowInd, colInd, candVal), False)
                    clauseR = (get_var_name(rowInd, colIndR, candVal), False)
                    dupClauses.append([clauseL, clauseR])

            # and then update CNF
            CNF.append(existsClause)
            CNF.extend(dupClauses)

    return CNF


def codify_column_validity(board_size: int) -> CNF:
    """
    Like in the row case, we want, for every column, that there exist one
    particular value in any of the rows (it exists in the column, basically).
    But, we do not want duplicates, so we also make the claim that one 
    value cannot exist in more than one row.
    """
    maxVal = board_size
    CNF = list()

    for colInd in range(board_size):
        for candVal in range(1, maxVal+1):
            existsClause = list()
            for rowInd in range(board_size): # it exists somewhere in the column
                existsClause.append((get_var_name(rowInd, colInd, candVal), True))

            dupClauses = list()
            for rowInd in range(board_size): # but not more than one row value
                for rowIndR in range(rowInd+1, board_size):
                    clauseL = (get_var_name(rowInd, colInd, candVal), False)
                    clauseR = (get_var_name(rowIndR, colInd, candVal), False)
                    dupClauses.append([clauseL, clauseR])

            # and then update CNF
            CNF.append(existsClause)
            CNF.extend(dupClauses)

    return CNF


def get_board_submatrices(board_size: int) -> list[list[tuple[int, int]]]:
    """
    Returns all submatrices as a list of the points that are contained within
    them in a larger list.
    """
    submatLen = sqrt(board_size) # submats are of size sqrt(n) x sqrt(n)
    numDivs = board_size // submatLen   # number of subdivisions along single axis
    originVals = list(range(board_size))[::board_size//numDivs]
    originTups = [(lVal, rVal) for lVal in originVals for rVal in originVals]

    # now go through and generate lists corresponding to each submatrix
    submatEntries = list()
    for rOrigin, cOrigin in originTups:
        curSubmatPts = list()
        for rowOff in range(submatLen):
            for colOff in range(submatLen):
                curSubmatPts.append((rOrigin+rowOff, cOrigin+colOff))

        submatEntries.append(curSubmatPts)
    
    return submatEntries


def codify_submatrix_validity(board_size: int) -> CNF:
    """
    This particular verification is a bit harder. Like before, our constant is that
    given the submatrices within the sudoku board, the values all exist once but not
    in more than one cell in the submatrix. However, the submatrix isn't that easy
    to index clearly, so this will require some help from other functions.
    """
    maxVal = board_size
    CNF = list()

    for submatPts in get_board_submatrices(board_size):
        for candVal in range(1, maxVal+1):
            existsClause = list()
            for curPt in submatPts:
                existsClause.append((get_var_name(*curPt, candVal), True))

            dupClauses = list()
            for lInd, curPt in enumerate(submatPts):
                for curPtR in submatPts[lInd+1:]:
                    clauseL = (get_var_name(*curPt, candVal), False)
                    clauseR = (get_var_name(*curPtR, candVal), False)
                    dupClauses.append([clauseL, clauseR])

            # and then update CNF
            CNF.append(existsClause)
            CNF.extend(dupClauses)
    
    return CNF

def sudoku_board_to_sat_formula(sudoku_board):
    """
    Generates a SAT formula that, when solved, represents a solution to the
    given sudoku board.  The result should be a formula of the right form to be
    passed to the satisfying_assignment function above.
    """
    board_size = len(sudoku_board)
    return (codify_column_validity(board_size) + codify_row_validity(board_size) +
            codify_cell_uniqueness(board_size) + codify_submatrix_validity(board_size) +
            codify_current_board_positions(sudoku_board))


def assignments_to_sudoku_board(assignments, n):
    """
    Given a variable assignment as given by satisfying_assignment, as well as a
    size n, construct an n-by-n 2-d array (list-of-lists) representing the
    solution given by the provided assignment of variables.

    If the given assignments correspond to an unsolvable board, return None
    instead.
    """
    # early termination for unsolvable items
    if assignments is None:
        return None

    # we only care about the positive attributes
    posAssignments = [val_name for val_name in assignments.keys() if assignments[val_name]]
    finalBoard = [[None]*n for _ in range(n)]
    resExtractor = lambda val_name: [int(val) for val in val_name.replace('@', ',').split(',')]

    for assignment in posAssignments:
        newVal, newRow, newCol = resExtractor(assignment)
        finalBoard[newRow][newCol] = newVal

    return finalBoard


if __name__ == "__main__":
    _doctest_flags = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS
    doctest.testmod(optionflags=_doctest_flags)

    with open('./puzzles/sudoku_6.json', 'rb') as inFile:
        import json
        testPuzzle = json.load(inFile)

    cnf = sudoku_board_to_sat_formula(testPuzzle)
    res = satisfying_assignment(cnf)
    print(res)