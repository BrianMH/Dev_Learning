"""
6.1010 Spring '23 Lab 4: Snekoban Game
"""

import json
import typing

# NO ADDITIONAL IMPORTS!
from snekoban import SnekobanGame


def new_game(level_description):
    """
    Given a description of a game state, create and return a game
    representation of your choice.

    The given description is a list of lists of lists of strs, representing the
    locations of the objects on the board (as described in the lab writeup).

    For example, a valid level_description is:

    [
        [[], ['wall'], ['computer']],
        [['target', 'player'], ['computer'], ['target']],
    ]

    The exact choice of representation is up to you; but note that what you
    return will be used as input to the other functions.
    """
    return SnekobanGame.deriveMemorylessGameState(level_description)


def victory_check(game):
    """
    Given a game representation (of the form returned from new_game), return
    a Boolean: True if the given game satisfies the victory condition, and
    False otherwise.
    """
    return game["gameFinished"]


def step_game(game, direction):
    """
    Given a game representation (of the form returned from new_game), return a
    new game representation (of that same form), representing the updated game
    after running one step of the game.  The user's input is given by
    direction, which is one of the following: {'up', 'down', 'left', 'right'}.

    This function should not mutate its input.
    """
    return SnekobanGame.memorylessGameUpdate(game, direction)


def dump_game(game):
    """
    Given a game representation (of the form returned from new_game), convert
    it back into a level description that would be a suitable input to new_game
    (a list of lists of lists of strings).

    This function is used by the GUI and the tests to see what your game
    implementation has done, and it can also serve as a rudimentary way to
    print out the current state of your game for testing and debugging on your
    own.
    """
    return SnekobanGame.memorylessCannonicalDump(game)


def backtrackMoves(game, parentDict):
    """
    Given the final state and a dictionary containing references to all parent
    states, calculates the moves required to reach the final state from the
    origin state.
    """
    # Find the path first
    curNode = sWrapper(game)
    path = [curNode[0]]
    while parentDict.get(curNode, None) is not None:
        path.append(parentDict[curNode][0])
        curNode = parentDict[curNode]
    winPath = list(reversed(path))

    # And then convert that into a list of moves to make
    findDelta = lambda lPos, rPos: tuple((rElem-lElem for (lElem, rElem) in zip(lPos, rPos)))
    revDeltaLookup = {(-1, 0): "up",
                      (1, 0): "down",
                      (0, 1): "right",
                      (0, -1): "left"}
    return [revDeltaLookup[findDelta(winPath[pInd], winPath[pInd+1])] for pInd in range(len(winPath)-1)]


def sWrapper(game):
    """
    Small wrapper over tuple indicator that is in the snekoban class
    """
    return SnekobanGame.generateStateTuple(game["player"], game["boxes"])


def solve_puzzle(game):
    """
    Given a game representation (of the form returned from new game), find a
    solution.

    Return a list of strings representing the shortest sequence of moves ("up",
    "down", "left", and "right") needed to reach the victory condition.

    If the given level cannot be solved, return None.
    """
    # if game is finished, no point in trying
    if game["gameFinished"]:
        return []

    stateQueue = [game]
    visited = {sWrapper(game)}
    parents = dict()

    while stateQueue:
        curState = stateQueue.pop(0)

        for neighborMove in ["up", "down", "left", "right"]:
            nState = SnekobanGame.memorylessGameUpdate(curState, neighborMove)
            if sWrapper(nState) in visited:
                continue
            
            # otherwise if unvisited...
            visited.add(sWrapper(nState))
            parents[sWrapper(nState)] = sWrapper(curState)
            stateQueue.append(nState)

            # just in case we can short circuit for the win here
            if nState["gameFinished"]:
                return backtrackMoves(nState, parents)
            
    # no possible path found
    return None

if __name__ == "__main__":
    # Trivially smoke tests the game.
    with open("./test_levels/unit_victory_double_target.json", "rb") as inLevel:
        initState = json.load(inLevel)
    curGame = new_game(initState)
    
    # And now test if solving works at all
    res = solve_puzzle(curGame)
    print(res)