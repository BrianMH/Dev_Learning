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

    for clause in reversed(formula):
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
        for term in clause:
            curClauseSet.add(term)
        newFormula.append(tuple(curClauseSet))

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


def satisfying_assignment(formula: CNF, solTerms:dict = dict(), cleanCNF: bool = True) -> dict:
    """
    Find a satisfying assignment for a given CNF formula.
    Returns that assignment if one exists, or None otherwise.

    >>> satisfying_assignment([])
    {}
    >>> x = satisfying_assignment([[('a', True), ('b', False), ('c', True)]])
    >>> x.get('a', None) is True or x.get('b', None) is False or x.get('c', None) is True
    True
    >>> satisfying_assignment([[('a', True)], [('a', False)]])
    """
    # cleans the CNF on firsr run
    if cleanCNF:
        formula = remove_redundancy(formula)

    # attempt to short-circuit arguments by finding singleton terms until no longer possible
    sc_working = True
    while sc_working:
        sc_terms, formula, sc_working = short_circuit_formula(formula)
        solTerms.update(sc_terms)

    # edge cases with trivially True/False statements
    if len(formula) == 0:
        return solTerms
    elif any([len(clause) == 0 for clause in formula]):
        return None

    # make an assumption about the CNF and recurse on the values
    for pot_var, pot_value in candidate_generator(formula):
        potSol = satisfying_assignment(update_formula_with_assumption(formula, [(pot_var, pot_value)]), 
                                       {**solTerms, pot_var:pot_value},
                                       False)
        if potSol is not None:
            return potSol

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


def sudoku_board_to_sat_formula(sudoku_board):
    """
    Generates a SAT formula that, when solved, represents a solution to the
    given sudoku board.  The result should be a formula of the right form to be
    passed to the satisfying_assignment function above.
    """
    raise NotImplementedError


def assignments_to_sudoku_board(assignments, n):
    """
    Given a variable assignment as given by satisfying_assignment, as well as a
    size n, construct an n-by-n 2-d array (list-of-lists) representing the
    solution given by the provided assignment of variables.

    If the given assignments correspond to an unsolvable board, return None
    instead.
    """
    raise NotImplementedError


if __name__ == "__main__":
    _doctest_flags = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS
    doctest.testmod(optionflags=_doctest_flags)