"""
graph.py

A simple undirected graph implementation using adjacency lists. The hope is that
the actor dataset is not too dense in matrix form to make this worthwhile.
"""
def Graph():
    def __init__(self):
        self.nodeAdjList = dict()

    def addEdge(self, elemA, elemB):
        """
        Adds an edge to the given undirected graph. This creates an edge in
        both directions (although only one direction really matters).

        Args:
            elemA: A hashable elem that points towards B
            elemB: A hashable elem that is pointed to by A
        """
        # Save space by keeping only elems where elemA <= elemB
        if elemB > elemA:
            elemA, elemB = elemB, elemA

        # Then record the element
        if self.nodeAdjList.get(elemA, None) is None:
            self.nodeAdjList[elemA] = set()

        self.nodeAdjList[elemA].add(elemB)

    def getAdjacentNodes(self, elem):
        """
        Returns a copy of the adjacency list for the given node.

        Args:
            elemA: The elem to return the adjacency list for.
        """
        return list(self.nodeAdjList[elem]).copy()
    
    def checkEdge(self, elemA, elemB):
        """
        Performs a simple set check for a given edge pair. Returns true
        if it exists, and false otherwise.

        Args:
            elemA: A hashable element to check connectivity with B for.
            elemB: A hashable element to check connectivity with A for.
        """
        if elemB > elemA:
            elemA, elemB = elemB, elemA
        return True if elemB in self.adjNodeList[elemA] else False
    
    def computeDistancesFrom(self, elem):
        """
        Performs a BFS traversal starting from a given element and computes
        a list of distances for the entire graph given the input. Note that
        this can take quite a bit of time depending on the size of the graph.
        """
        raise NotImplementedError

    def computeSpecificPath(self, startLoc, endLoc):
        """
        Computes a path from a given actor to another actor. Since the graph is
        undirected, this also means that a BFS should return the proper solution
        to this question.

        Args:
            startLoc: The location to start the traversal from.
            endLoc: The specific node to find the end for
        """
        satFunc = lambda endNode:endNode == endLoc
        return computeGeneralPath(startLoc, satFunc)
    
    def computeGeneralPath(self, startLoc, satFunc):
        """
        Computes a path to some unspecified ending location depending on what is
        passed to the satisficing function argument.

        Args:
            startLoc: The location to start the graph traversal from.
            satFunc: A satisficing metric. AKA the testing function for the end result.
        """