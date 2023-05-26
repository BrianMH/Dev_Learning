"""
snekoban.py

Contains most of the logic behind the game that is used as an interface
for the user. The game will be approached similar to a lot of the AoC
game questions. The user's position will be a tuple and the rest of the
elements will be in sets/frozensets and be manipulated from there.

The class within here expects the initial descriptor to be in the following
form as an example:

[
   [["wall"],  ["wall"],  ["wall"],      ["wall"],             ["wall"], ["wall"]],
   [["wall"],  [],        ["computer"],  [],                   [],       ["wall"]],
   [["wall"],  [],        [],            ["target", "player"], [],       ["wall"]],
   [["wall"],  ["wall"],  ["wall"],      ["wall"],             ["wall"], ["wall"]]
]

In other words, the cannonical descriptor is a 2d list where each element of the 2d
list is a list that represents all objects within a particular position. There are
certain rules that can be inferred from the snekoban game, but none that are
particularly noteworth to put here right now.
"""
# This is a simple enum class to make the directions easier to parse
from enum import Enum
class GameAction(Enum):
    UP = 1
    DOWN = 2
    LEFT = 3
    RIGHT = 4


class SnekobanGame:
    # This is largely for user legibility
    posMoves = GameAction
    strMoveDict = {"up": posMoves.UP,
                    "down": posMoves.DOWN,
                    "left": posMoves.LEFT,
                    "right": posMoves.RIGHT}
    moveMapping = {posMoves.DOWN: (1, 0),
                    posMoves.UP: (-1, 0),
                    posMoves.LEFT: (0, -1),
                    posMoves.RIGHT: (0, 1)}

    def __init__(self, initDescriptor, * , lockOnWin = False):
        """
        A SnekobanGame object contains all of the elements necessary to initialize
        a Snekoban game. Note that as demanded by the lab, this class can be used in
        a memoryless method entirely through static methods.

        Args:
            initDescriptor: 2d list representation of the actual initial map. Specifics
            about how the descriptor should look are given above.
        """
        # Create the required position elements for the game
        curGame = self.convertCannonicalToNative(initDescriptor)
        self.walls : frozenset = curGame["walls"] 
        self.computers : set = curGame["boxes"]
        self.playerLoc : tuple[int, int] = curGame["player"]
        self.targets : frozenset = curGame["targets"]
        self.numRows, self.numCols = curGame["dimensions"]

        # This part just keeps track of metadata
        self.numTurns = 0
        self.curScore = 0
        self.gameFinished = False
        self.winLock = lockOnWin

        # And ensure game isn't already over
        self.updateGameState()


    def getPosActions(self):
        """
        Returns an enumeration that contains all of the possible class moves.
        """
        return list(self.posMoves)


    def makeMove(self, move):
        """
        Makes a move in the current snekoban game. This pretty much controls most of the
        central logic, but some of the checking functions will be split for readibility.
        The movement logic seems to be simple. The checks will occur as follows:

            1) Calculate the new position given the action decided.

            2) Prevent user movement if the following attributes are true:

                2.1) If there is a wall in the new position

                2.2) If there is a computer in the current position and there is
                either a wall or a computer one step ahead

            3) If user movement occurred and there was a computer in the new position,
            then move the computer along with the player. Otherwise, just move the player.

            4) Update the current round and score given the target and computer positions.

        Args:
            move: The direction to move the piece, expressed as either a string of enumeration
        """
        # Edge case (game is already over)
        if self.winLock and self.gameFinished:
            return

        # Find current move
        curMove = self._parseMove(move)
        if curMove is None:
            raise ValueError("Passed in string is not a valid input.")

        # find the new position and evaluate possible non-move situations
        moveDelta = self.moveMapping[curMove]
        newPos = self._tupAdder(self.playerLoc, moveDelta)
        lahPos = self._tupAdder(newPos, moveDelta)
        if (newPos in self.walls or 
                (newPos in self.computers and (lahPos in self.walls or lahPos in self.computers))):
            return
        
        # And then move objects that have to be moved
        self.playerLoc = newPos
        if newPos in self.computers:
            self.computers.remove(newPos)
            self.computers.add(lahPos)

        # Finally update game metadata
        self.numTurns += 1
        self.updateGameState()


    def updateGameState(self):
        """
        Given the current game state, determine the current score and whether
        the game has finished.
        """
        # Find score
        curScore = 0
        for compLoc in self.computers:
            if compLoc in self.targets:
                curScore += 1
        
        # Then update state
        self.curScore = curScore
        if len(self.targets) > 0 and curScore == len(self.computers):
            self.gameFinished = True
        else:
            self.gameFinished = False

    @classmethod
    def _parseMove(cls, move):
        """
        Helper function to convert string inputs into the desired enumeration value
        """
        if isinstance(move, GameAction):
            return move
        else:
            return cls.strMoveDict.get(move, None)
        
    @staticmethod
    def _tupAdder(tupL, tupR):
        """
        Helper function to add two tuples together
        """
        return tuple((lElem+rElem for (lElem, rElem) in zip(tupL, tupR)))
    

    def isFinished(self):
        """
        Returns whether the game has been won or not (it's only been won if all computers
        are on the right spot!)
        """
        return self.gameFinished
        

    def convertNativeToCannonical(self):
        """
        Converts the current game state's native representation into the cannonical form that is
        expected from the online version.
        """
        # initialize return array
        cannonicalForm = [[list() for _ in range(self.numCols)] for _ in range(self.numRows)]

        # and then populate with values
        for rowInd in range(self.numRows):
            for colInd in range(self.numCols):
                curLoc = (rowInd, colInd)

                # walls cannot be present with any other element
                if curLoc in self.walls:
                    cannonicalForm[rowInd][colInd].append("wall")
                    continue

                # and now place the rest of the elements
                # (Note that collisions will be detected by the API!)
                if curLoc in self.targets:
                    cannonicalForm[rowInd][colInd].append("target")
                if curLoc in self.computers:
                    cannonicalForm[rowInd][colInd].append("computer")
                if curLoc == self.playerLoc:
                    cannonicalForm[rowInd][colInd].append("player")

        return cannonicalForm


    @staticmethod
    def convertCannonicalToNative(descriptorArray):
        """
        Converts a 3d descriptor matrix into a native representation using sets and tuples
        and returns all of that in a neatly formatted dictionary.

        Args:
            descriptorArray: A 2d list representation of some given map
        """
        # Prepare the location positions for the game
        wallLocs: list[tuple[int, int]] = list()
        computerLocs: list[tuple[int, int]] = list()
        playerLoc: tuple[int, int]
        targetLocs: list[tuple[int, int]] = list()
        gameDims = tuple[int, int]

        # Parse through positions one-by-one
        for rowInd in range(len(descriptorArray)):
            for colInd in range(len(descriptorArray[0])):
                for element in descriptorArray[rowInd][colInd]:
                    match element:
                        case "wall":
                            wallLocs.append((rowInd, colInd))
                        case "computer":
                            computerLocs.append((rowInd, colInd))
                        case "target":
                            targetLocs.append((rowInd, colInd))
                        case "player":
                            playerLoc = (rowInd, colInd)
        gameDims = (len(descriptorArray), len(descriptorArray[0]))

        # Then returned a proper dictionary with desired elements
        return {"walls":frozenset(wallLocs),
                "player":playerLoc,
                "targets":frozenset(targetLocs),
                "boxes":set(computerLocs),
                "dimensions":gameDims}
    
    def __str__(self):
        """
        This makes it easier to visually debug things quickly
        """
        finalString = ""
        for rowInd in range(self.numRows):
            for colInd in range(self.numCols):
                curLoc = (rowInd, colInd)
                if curLoc in self.walls:
                    finalString += "#"
                elif curLoc == self.playerLoc:
                    finalString += "@"
                elif curLoc in self.computers:
                    finalString += "C"
                elif curLoc in self.targets:
                    finalString += "T"
                else:
                    finalString += " "
            finalString += "\n"
        return finalString
    
    ########## MEMORYLESS METHODS #########
    @classmethod
    def deriveMemorylessGameState(cls, initState):
        """
        A memoryless implementation of the game initialization method.
        """
        # Derive initial state
        curState = cls.convertCannonicalToNative(initState)

        # And now add some additional elements to maintain proper states
        curState = {**curState,
                    "curTurn": 0,
                    "curScore": 0,
                    "gameFinished" : False}
        
        # Check for initial win
        curScore = 0
        for compLoc in curState["boxes"]:
            if compLoc in curState["targets"]:
                curScore += 1
        
        # Then update state
        curState["curScore"] = curScore
        if len(curState["targets"]) > 0 and curScore == len(curState["boxes"]):
            curState["gameFinished"] = True
        
        return curState
    
    @classmethod
    def memorylessGameUpdate(cls, curState, move):
        """
        A memoryless implementation of the game update method.
        """
        # copy object to new spot for lab
        newState = {"walls": curState["walls"].copy(),
                    "player": curState["player"],
                    "targets": curState["targets"].copy(),
                    "boxes": curState["boxes"].copy(),
                    "dimensions": curState["dimensions"],
                    "curTurn": curState["curTurn"],
                    "curScore": curState["curScore"],
                    "gameFinished" : curState["gameFinished"]}

        # Find current move
        curMove = cls._parseMove(move)
        if curMove is None:
            raise ValueError("Passed in string is not a valid input.")

        # find the new position and evaluate possible non-move situations
        moveDelta = cls.moveMapping[curMove]
        newPos = cls._tupAdder(newState["player"], moveDelta)
        lahPos = cls._tupAdder(newPos, moveDelta)
        if (newPos in newState["walls"] or 
                (newPos in newState["boxes"] and (lahPos in newState["walls"] or lahPos in newState["boxes"]))):
            return newState
        
        # And then move objects that have to be moved
        newState["player"] = newPos
        if newPos in newState["boxes"]:
            newState["boxes"].remove(newPos)
            newState["boxes"].add(lahPos)

        # Finally update game metadata
        newState["curTurn"] += 1
        curScore = 0
        for compLoc in newState["boxes"]:
            if compLoc in newState["targets"]:
                curScore += 1
        
        # Then update state
        newState["curScore"] = curScore
        if len(newState["targets"]) > 0 and curScore == len(newState["boxes"]):
            newState["gameFinished"] = True
        else:
            newState["gameFinished"] = False
        return newState

    @staticmethod
    def memorylessCannonicalDump(curState):
        """
        A memoryless implementation of the native to cannonical dump method.
        """
        # initialize return array
        numRows, numCols = curState["dimensions"]
        cannonicalForm = [[list() for _ in range(numCols)] for _ in range(numRows)]

        # and then populate with values
        for rowInd in range(numRows):
            for colInd in range(numCols):
                curLoc = (rowInd, colInd)

                # walls cannot be present with any other element
                if curLoc in curState["walls"]:
                    cannonicalForm[rowInd][colInd].append("wall")
                    continue

                # and now place the rest of the elements
                # (Note that collisions will be detected by the API!)
                if curLoc in curState["targets"]:
                    cannonicalForm[rowInd][colInd].append("target")
                if curLoc in curState["boxes"]:
                    cannonicalForm[rowInd][colInd].append("computer")
                if curLoc == curState["player"]:
                    cannonicalForm[rowInd][colInd].append("player")

        return cannonicalForm
    
    @staticmethod
    def generateStateTuple(playerLoc, compLoc):
        """
        The most important aspects of the game that determine whether or not
        a state has been visited are:

            1) The player's location
        
            2) The location of the computers

        Everything else is essentially redundant as it never changes across
        objects, so we only need to cache these two elements by converting
        them into a tuple as so: (playerLoc, (comp_locs, ...))

        Args:
            playerLoc: The location of the player.
            compLoc: The location of the computers.
        """
        return (playerLoc, tuple(compLoc))