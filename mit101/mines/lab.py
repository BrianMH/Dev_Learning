"""
6.1010 Spring '23 Lab 7: Mines
"""

#!/usr/bin/env python3

import typing
import doctest

# NO ADDITIONAL IMPORTS ALLOWED!


def dump(game):
    """
    Prints a human-readable version of a game (provided as a dictionary)
    """
    for key, val in sorted(game.items()):
        if isinstance(val, list) and val and isinstance(val[0], list):
            print(f"{key}:")
            for inner in val:
                print(f"    {inner}")
        else:
            print(f"{key}:", val)


# 2-D IMPLEMENTATION


def new_game_2d(num_rows, num_cols, bombs):
    """
    Start a new game.

    Return a game state dictionary, with the 'dimensions', 'state', 'board' and
    'hidden' fields adequately initialized.

    Parameters:
       num_rows (int): Number of rows
       num_cols (int): Number of columns
       bombs (list): List of bombs, given in (row, column) pairs, which are
                     tuples

    Returns:
       A game state dictionary

    >>> dump(new_game_2d(2, 4, [(0, 0), (1, 0), (1, 1)]))
    board:
        ['.', 3, 1, 0]
        ['.', '.', 1, 0]
    dimensions: (2, 4)
    hidden:
        [True, True, True, True]
        [True, True, True, True]
    state: ongoing
    toDigCnt: 5

    """
    return new_game_nd((num_rows, num_cols), bombs)

def get_deltas_ndgame(num_dims):
    '''
    Given an n-dimensional game, generates the necessary deltas to check
    any appropriate number of neighbors. As expected, this generates
    (3^n)-1 coordinates (-1 due to the current loc delta (0, ...) not being
    counted)

    Args:
        num_dims: The number of dimensions for the current game

    Returns:
        A list of size (3^n)-1 containing all possible neighbor creating deltas

    >>> get_deltas_ndgame(1)
    [(-1,), (1,)]

    >>> get_deltas_ndgame(2)
    [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    '''
    relVals = [-1, 0, 1]
    finCombs = [(-1,), (0,), (1,)]

    for _ in range(num_dims-1):
        tempCombs = list()
        for relVal in relVals:
            tempCombs.extend([prevComb+(relVal,) for prevComb in finCombs])
        finCombs = tempCombs

    # remove the non-move delta as it's useless for this game
    finCombs.remove((0,)*num_dims)

    return finCombs

def get_neighbor_coords(dimensions, curPos):
    '''
    Given the game, returns a list of tuples representing the neighbors that
    need to be checked given a certain position. (This can technically be
    cached, but I imagine we aren't going to be creating massively large
    mine fields.)

    Args:
        game: The current game structure being played
        row: The current row of the position to acquire neighbors for
        col: The current column of the position to find neighbors for

    Returns:
        A generator with the neighbors of the current position.
    '''
    def isValid(posTuple):
        for dimInd in range(len(dimensions)):
            if not (0 <= posTuple[dimInd] < dimensions[dimInd]):
                return False
        return True

    tupAdder = lambda tupL, tupR: tuple([lElem+rElem for (lElem, rElem) in zip(tupL, tupR)])
    gameDeltas = get_deltas_ndgame(len(dimensions))
    unfilteredTups = [tupAdder(curPos, curDelta) for curDelta in gameDeltas]

    return [loc for loc in unfilteredTups if isValid(loc)]


def dig_2d(game, row, col):
    """
    Reveal the cell at (row, col), and, in some cases, recursively reveal its
    neighboring squares.

    Update game['hidden'] to reveal (row, col).  Then, if (row, col) has no
    adjacent bombs (including diagonally), then recursively reveal (dig up) its
    eight neighbors.  Return an integer indicating how many new squares were
    revealed in total, including neighbors, and neighbors of neighbors, and so
    on.

    The state of the game should be changed to 'defeat' when at least one bomb
    is revealed on the board after digging (i.e. game['hidden'][bomb_location]
    == False), 'victory' when all safe squares (squares that do not contain a
    bomb) and no bombs are revealed, and 'ongoing' otherwise.

    Parameters:
       game (dict): Game state
       row (int): Where to start digging (row)
       col (int): Where to start digging (col)

    Returns:
       int: the number of new squares revealed

    >>> game = {'dimensions': (2, 4),
    ...         'board': [['.', 3, 1, 0],
    ...                   ['.', '.', 1, 0]],
    ...         'hidden': [[True, False, True, True],
    ...                  [True, True, True, True]],
    ...         'state': 'ongoing',
    ...         'toDigCnt': 4}
    >>> dig_2d(game, 0, 3)
    4
    >>> dump(game)
    board:
        ['.', 3, 1, 0]
        ['.', '.', 1, 0]
    dimensions: (2, 4)
    hidden:
        [True, False, False, False]
        [True, True, False, False]
    state: victory
    toDigCnt: 0

    >>> game = {'dimensions': [2, 4],
    ...         'board': [['.', 3, 1, 0],
    ...                   ['.', '.', 1, 0]],
    ...         'hidden': [[True, False, True, True],
    ...                  [True, True, True, True]],
    ...         'state': 'ongoing',
    ...         'toDigCnt': 4}
    >>> dig_2d(game, 0, 0)
    1
    >>> dump(game)
    board:
        ['.', 3, 1, 0]
        ['.', '.', 1, 0]
    dimensions: [2, 4]
    hidden:
        [False, False, True, True]
        [True, True, True, True]
    state: defeat
    toDigCnt: 4
    """
    return dig_nd(game, (row, col))


def render_2d_locations(game, xray=False):
    """
    Prepare a game for display.

    Returns a two-dimensional array (list of lists) of '_' (hidden squares),
    '.' (bombs), ' ' (empty squares), or '1', '2', etc. (squares neighboring
    bombs).  game['hidden'] indicates which squares should be hidden.  If
    xray is True (the default is False), game['hidden'] is ignored and all
    cells are shown.

    Parameters:
       game (dict): Game state
       xray (bool): Whether to reveal all tiles or just the that are not
                    game['hidden']

    Returns:
       A 2D array (list of lists)

    >>> render_2d_locations({'dimensions': (2, 4),
    ...         'state': 'ongoing',
    ...         'board': [['.', 3, 1, 0],
    ...                   ['.', '.', 1, 0]],
    ...         'hidden':  [[True, False, False, True],
    ...                   [True, True, False, True]]}, False)
    [['_', '3', '1', '_'], ['_', '_', '1', '_']]

    >>> render_2d_locations({'dimensions': (2, 4),
    ...         'state': 'ongoing',
    ...         'board': [['.', 3, 1, 0],
    ...                   ['.', '.', 1, 0]],
    ...         'hidden':  [[True, False, True, False],
    ...                   [True, True, True, False]]}, True)
    [['.', '3', '1', ' '], ['.', '.', '1', ' ']]
    """
    return render_nd(game, xray)


def render_2d_board(game, xray=False):
    """
    Render a game as ASCII art.

    Returns a string-based representation of argument 'game'.  Each tile of the
    game board should be rendered as in the function
        render_2d_locations(game)

    Parameters:
       game (dict): Game state
       xray (bool): Whether to reveal all tiles or just the ones allowed by
                    game['hidden']

    Returns:
       A string-based representation of game

    >>> render_2d_board({'dimensions': (2, 4),
    ...                  'state': 'ongoing',
    ...                  'board': [['.', 3, 1, 0],
    ...                            ['.', '.', 1, 0]],
    ...                  'hidden':  [[False, False, False, True],
    ...                            [True, True, False, True]]})
    '.31_\\n__1_'
    """
    curMat = render_2d_locations(game, xray)
    rowStrings = ["".join(curRow) for curRow in curMat]
    return "\n".join(rowStrings)


# N-D IMPLEMENTATION

def create_nd_array(dimensions, init_value):
    '''
    Creates an n-dimensional array with a given initialization value. Note that
    the initialized value should be an immutable one (string/integer) to avoid
    pointer issues.
    '''
    arr = list()
    innerRefs = arr
    for dimInd, dimLen in enumerate(dimensions):
        if dimInd == len(dimensions)-1:
            for innerElem in innerRefs:
                innerElem.extend([init_value for _ in range(dimLen)])
        elif dimInd == 0:
            newRefs = [list() for _ in range(dimLen)]
            arr.extend(newRefs)
            innerRefs = newRefs
        else:
            newInnerRefs = list()
            for innerElem in innerRefs:
                newRefs = [list() for _ in range(dimLen)]
                innerElem.extend(newRefs)
                newInnerRefs.extend(newRefs)
            innerRefs = newInnerRefs

    return arr


def get_element(mat, pos_tuple):
    '''
    Given an n-dimensional matrix and a positional tuple of size equivalent 
    to the matrix, return the element at the specific index.
    '''
    curElem = mat
    for posInd in pos_tuple:
        curElem = curElem[posInd]

    return curElem


def set_element(mat, pos_tuple, new_value):
    '''
    Same as above but we now set the value of the relevant element.
    '''
    curElem = mat
    for posInd in pos_tuple[:-1]:
        curElem = curElem[posInd]

    # Then change the final element through its array index
    curElem[pos_tuple[-1]] = new_value


def get_nd_pos_generator(dimensions):
    '''
    Creates a generator that yields all possible position tuples given
    the input dimensions of the matrix.
    '''
    curPos = [0]*len(dimensions)
    maxLims = [dim-1 for dim in dimensions]

    while curPos != maxLims:
        yield tuple(curPos)

        # augment the value if possible from least significant loc
        curPos[-1] += 1
        for oflowInd in reversed(range(len(dimensions))):
            if curPos[oflowInd] > maxLims[oflowInd]:
                curPos[oflowInd] = 0
                curPos[oflowInd-1] += 1

    # yield final tuple afterward
    yield tuple(maxLims)


def reduce(iterable, func, initial = None):
    '''
    A pretty lazy implementation of the reduce function already available in a Python
    package. Pretty much does what it says: reduces the list down to a single value 
    given a function and potentially including an initial value.
    '''
    lVal, rVal = None, None
    if initial is not None:
        lVal = initial

    for val in iterable:
        # if lval is empty, load it and do nothing until rval is also loaded
        if lVal is None:
            lVal = val
            continue
        elif rVal is None:
            rVal = val
        
        lVal = func(lVal, rVal)
        rVal = None

    return lVal


def new_game_nd(dimensions, bombs):
    """
    Start a new game.

    Return a game state dictionary, with the 'dimensions', 'state', 'board' and
    'hidden' fields adequately initialized.


    Args:
       dimensions (tuple): Dimensions of the board
       bombs (list): Bomb locations as a list of tuples, each an
                     N-dimensional coordinate

    Returns:
       A game state dictionary

    >>> g = new_game_nd((2, 4, 2), [(0, 0, 1), (1, 0, 0), (1, 1, 1)])
    >>> dump(g)
    board:
        [[3, '.'], [3, 3], [1, 1], [0, 0]]
        [['.', 3], [3, '.'], [1, 1], [0, 0]]
    dimensions: (2, 4, 2)
    hidden:
        [[True, True], [True, True], [True, True], [True, True]]
        [[True, True], [True, True], [True, True], [True, True]]
    state: ongoing
    toDigCnt: 13
    """
    # First create our arrays for future use
    hidden = create_nd_array(dimensions, True)
    hidden_nonbombs = reduce(dimensions, lambda x, y: x*y)

    # And then initialize our bomb board with bomb positions
    board = create_nd_array(dimensions, 0)
    for bombPos in bombs:
        set_element(board, bombPos, '.')
        hidden_nonbombs -= 1
    
    # And update the neighbor counters accordingly
    for posTup in get_nd_pos_generator(dimensions):
        # Skip any points that aren't necessary to fill
        if not get_element(board, posTup) == 0:
            continue

        for neighbor in get_neighbor_coords(tuple(dimensions), posTup):
            if get_element(board, neighbor) == ".":
                set_element(board, posTup, 1 + get_element(board, posTup))
    
    return {
        "dimensions": dimensions,
        "board": board,
        "hidden": hidden,
        "state": "ongoing",
        "toDigCnt": hidden_nonbombs,
    }


def dig_nd(game, coordinates):
    """
    Recursively dig up square at coords and neighboring squares.

    Update the hidden to reveal square at coords; then recursively reveal its
    neighbors, as long as coords does not contain and is not adjacent to a
    bomb.  Return a number indicating how many squares were revealed.  No
    action should be taken and 0 returned if the incoming state of the game
    is not 'ongoing'.

    The updated state is 'defeat' when at least one bomb is revealed on the
    board after digging, 'victory' when all safe squares (squares that do
    not contain a bomb) and no bombs are revealed, and 'ongoing' otherwise.

    Args:
       coordinates (tuple): Where to start digging

    Returns:
       int: number of squares revealed

    >>> g = {'dimensions': (2, 4, 2),
    ...      'board': [[[3, '.'], [3, 3], [1, 1], [0, 0]],
    ...                [['.', 3], [3, '.'], [1, 1], [0, 0]]],
    ...      'hidden': [[[True, True], [True, False], [True, True],
    ...                [True, True]],
    ...               [[True, True], [True, True], [True, True],
    ...                [True, True]]],
    ...      'state': 'ongoing',
    ...      'toDigCnt': 13}
    >>> dig_nd(g, (0, 3, 0))
    8
    >>> dump(g)
    board:
        [[3, '.'], [3, 3], [1, 1], [0, 0]]
        [['.', 3], [3, '.'], [1, 1], [0, 0]]
    dimensions: (2, 4, 2)
    hidden:
        [[True, True], [True, False], [False, False], [False, False]]
        [[True, True], [True, True], [False, False], [False, False]]
    state: ongoing
    toDigCnt: 5
    >>> g = {'dimensions': (2, 4, 2),
    ...      'board': [[[3, '.'], [3, 3], [1, 1], [0, 0]],
    ...                [['.', 3], [3, '.'], [1, 1], [0, 0]]],
    ...      'hidden': [[[True, True], [True, False], [True, True],
    ...                [True, True]],
    ...               [[True, True], [True, True], [True, True],
    ...                [True, True]]],
    ...      'state': 'ongoing',
    ...      'toDigCnt': 13}
    >>> dig_nd(g, (0, 0, 1))
    1
    >>> dump(g)
    board:
        [[3, '.'], [3, 3], [1, 1], [0, 0]]
        [['.', 3], [3, '.'], [1, 1], [0, 0]]
    dimensions: (2, 4, 2)
    hidden:
        [[True, False], [True, False], [True, True], [True, True]]
        [[True, True], [True, True], [True, True], [True, True]]
    state: defeat
    toDigCnt: 13
    """
    # Game already finished
    if game["state"] in {"defeat", "victory"}:
        return 0

    # Check if we landed on a bomb or selected something already shown
    if get_element(game["board"], coordinates) == ".":
        set_element(game["hidden"], coordinates, False)
        game["state"] = "defeat"
        return 1
    elif not get_element(game["hidden"], coordinates):
        return 0

    # Mine current position and neighbors to reveal any new points
    set_element(game["hidden"], coordinates, False)
    revealed = 1
    game["toDigCnt"] -= 1

    if get_element(game["board"], coordinates) == 0:
        for neighbor in get_neighbor_coords(game["dimensions"], coordinates):
            revealed += dig_nd(game, neighbor)

    # After that, we can check for a win given the toDigCnt
    if game["toDigCnt"] == 0:
        game["state"] = "victory"

    return revealed


def render_nd(game, xray=False):
    """
    Prepare the game for display.

    Returns an N-dimensional array (nested lists) of '_' (hidden squares), '.'
    (bombs), ' ' (empty squares), or '1', '2', etc. (squares neighboring
    bombs).  The game['hidden'] array indicates which squares should be
    hidden.  If xray is True (the default is False), the game['hidden'] array
    is ignored and all cells are shown.

    Args:
       xray (bool): Whether to reveal all tiles or just the ones allowed by
                    game['hidden']

    Returns:
       An n-dimensional array of strings (nested lists)

    >>> g = {'dimensions': (2, 4, 2),
    ...      'board': [[[3, '.'], [3, 3], [1, 1], [0, 0]],
    ...                [['.', 3], [3, '.'], [1, 1], [0, 0]]],
    ...      'hidden': [[[True, True], [True, False], [False, False],
    ...                [False, False]],
    ...               [[True, True], [True, True], [False, False],
    ...                [False, False]]],
    ...      'state': 'ongoing'}
    >>> render_nd(g, False)
    [[['_', '_'], ['_', '3'], ['1', '1'], [' ', ' ']],
     [['_', '_'], ['_', '_'], ['1', '1'], [' ', ' ']]]

    >>> render_nd(g, True)
    [[['3', '.'], ['3', '3'], ['1', '1'], [' ', ' ']],
     [['.', '3'], ['3', '.'], ['1', '1'], [' ', ' ']]]
    """
    outArr = create_nd_array(game["dimensions"], '_')
    for coord in get_nd_pos_generator(game["dimensions"]):
        if xray or not get_element(game["hidden"], coord):
            curElem = str(get_element(game["board"], coord))
            curElem = " " if curElem == "0" else curElem
            set_element(outArr, coord, curElem)

    return outArr

if __name__ == "__main__":
    # Test with doctests. Helpful to debug individual lab.py functions.
    _doctest_flags = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS
    doctest.testmod(optionflags=_doctest_flags)  # runs ALL doctests

    # Alternatively, can run the doctests JUST for specified function/methods,
    # e.g., for render_2d_locations or any other function you might want.  To
    # do so, comment out the above line, and uncomment the below line of code.
    # This may be useful as you write/debug individual doctests or functions.
    # Also, the verbose flag can be set to True to see all test results,
    # including those that pass.
    #
    #doctest.run_docstring_examples(
    #    render_2d_locations,
    #    globals(),
    #    optionflags=_doctest_flags,
    #    verbose=False
    # )

    # Tests some matrix operations using our custom matrix implementation
    print("\nSmoke testing matrix operations...\n")
    print("Creating array of size (2, 4, 2) with intiailizataion \".\" yields: ")
    newMat = create_nd_array((2, 4, 2), ".")
    print(newMat, end = '\n\n')

    print("And then setting and asserting the changed values yields...")
    toSet = {(0, 0, 1), (0, 1, 0), (1, 0, 0), (1, 0, 1), (1, 1, 0), (0, 1, 1)}
    for pos in toSet:
        set_element(newMat, pos, "test")
        assert(get_element(newMat, pos) == "test")
    print(newMat)

    # Test the generator for proper generator control
    print("\nSmoke testing the matrix loc generator...\n")
    all_pos_tuples = get_nd_pos_generator((2, 4, 2))
    assert len(list(all_pos_tuples)) == 2*4*2, "Generator produces wrong ouputs!"

    # Tests our silly version of the reduce function that exists
    print("\nSmoke testing the reduce function...")
    relList = [1, 2, 3, 4, 5, 6, 7]
    assert reduce(relList, lambda x, y: x+y) == reduce(relList, lambda x, y: x+y, initial = 0) == sum(relList)
    assert reduce(relList, lambda x, y: x*y) == reduce(relList, lambda x, y: x*y, initial = 1) == (7*6*5*4*3*2)