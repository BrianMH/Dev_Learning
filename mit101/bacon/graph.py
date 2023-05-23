"""
graph.py

A simple undirected graph implementation using adjacency lists. The hope is that
the actor dataset is not too dense in matrix form to make this worthwhile.
"""
class Edge():
    def __init__(self, vertexA, vertexB, edgeVal):
        """
        An edge represents a conection between two different vertices on a graph.
        This is a directed edge so keep the directionality in mind. Value can
        potentially be extended by turning it into a list (to implement duplicity),
        but we will keep it simple for now.
        """
        self.fromNode = vertexA
        self.toNode = vertexB
        self.value = edgeVal

    def getValue(self):
        return self.value

class Graph():
    def __init__(self):
        """
        A graph is a collection of vertices and edges. Vertices represents specific
        hashable points that are referenceable while the edges represent connections
        between these vertices that can have some custom value. By default,
        an empty graph is always constructed.
        """
        self.nodeAdjList = dict()   # A collection of nodes adjacent to a given node
        self.edgeMatrix = dict()    # The collection of edges making up this graph
                                    # Takes in (vertexA, vertexB) tuples.

    def addDirectedEdge(self, elemA, elemB, edgeVal = None):
        """
        Adds an edge to the underlying graph that only goes in one direction.
        
        Args:
            elemA: A hashable element that points towards B
            elemB: A hashable element that is pointed to by A
        """
        if self.nodeAdjList.get(elemA, None) is None:
            self.nodeAdjList[elemA] = set()

        self.nodeAdjList[elemA].add(elemB)
        self.edgeMatrix[(elemA, elemB)] = Edge(elemA, elemB, edgeVal)

    def addUndirectedEdge(self, elemA, elemB, edgeVal = None):
        """
        Adds an edge to the given undirected graph. This creates an edge in
        both directions.

        Args:
            elemA: A hashable elem that points towards B
            elemB: A hashable elem that points towards A
        """
        self.addDirectedEdge(elemA, elemB, edgeVal)
        self.addDirectedEdge(elemB, elemA, edgeVal)

    def getAdjacentNodes(self, elem):
        """
        Returns a copy of the adjacency list for the given node.

        Args:
            elemA: The elem to return the adjacency list for.
        """
        return list(self.nodeAdjList[elem]).copy()
    
    def checkEdge(self, elemA, elemB):
        """
        Performs a simple check for a given edge pair. Returns true
        if it exists, and false otherwise.

        Args:
            elemA: A hashable element to check connectivity with B for.
            elemB: A hashable element to check connectivity with A for.
        """
        # trivial return value (every actor acted with themselves)
        if elemA == elemB:
            return True
        
        return True if self.edgeMatrix.get((elemA, elemB), None) is not None else False
    
    def computeDistancesFrom(self, elem):
        """
        Performs a BFS traversal starting from a given element and computes
        a list of distances for the entire graph given the input. Note that
        this can take quite a bit of time depending on the size of the graph
        and the actual number of reachable elements.
        """
        # initialize our traversal and resultant dictionary
        visited = {elem}
        toVisit = [(elem, int(0))]
        distDict = {elem: 0}
        
        # performs a simple bfs
        while toVisit:
            # Get current node and distance from visited node
            curNode, curDist = toVisit.pop(0)

            # Visit children nodes, record distance, and then queue neighbors
            for childNode in self.nodeAdjList[curNode]:
                if childNode in visited:
                    continue
                else:
                    visited.add(childNode)

                distDict[childNode] = curDist + 1
                toVisit.append((childNode, curDist + 1))

        return distDict

    def getNeighbors(self, elem):
        """
        Returns a list of the immediately adjacent neighbors of a given vertex.
        This returns a copy so that the user doesn't inadvertedly damage any
        potential objects that are hashable but noted by reference.

        Args:
            elem: The node to acquire the neighbors for.
        """
        return self.nodeAdjList[elem].copy()


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
        return self.computeGeneralPath(startLoc, satFunc)
    
    def computeGeneralPath(self, startLoc, satFunc):
        """
        Computes a path to some unspecified ending location depending on what is
        passed to the satisficing function argument. This will be an iterative
        traversal if only because it's possible that the depth could exceed the max
        for our application.

        Args:
            startLoc: The location to start the graph traversal from.
            satFunc: A satisficing metric. AKA the testing function for the end result.
        """
        # Initialize our values just like before but with the path added
        visited = {startLoc}
        parents = dict()
        toVisit = [startLoc]
        
        # performs a simple bfs
        while toVisit:
            # Get current node and then skip if already visited
            curNode = toVisit.pop(0)
            if satFunc(curNode):
                return self.backtrackPath(curNode, parents)

            # Test satisficing function and then add children to the queue
            for childNode in self.nodeAdjList[curNode]:
                if childNode in visited:
                    continue
                else:
                    visited.add(childNode)
                    parents[childNode] = curNode

                toVisit.append(childNode)

        # no possible path found
        return []

    def backtrackPath(self, endNode, parentDict):
        """
        Given a final node and the list of parents, produce the path that was
        traversed to reach this particular node.

        Args:
            endNode: The final node in the path to begin backtracking from
            parentDict: A dictionary representing the nodes taken to get to the current node.
        """
        curNode = endNode
        path = [curNode]
        while parentDict.get(curNode, None) is not None:
            path.append(parentDict[curNode])
            curNode = parentDict[curNode]

        return reversed(path)

    def computeEdgePathFromVertices(self, vertices):
        """
        Given an ordered list of verticies, calculates the edges required for traversal
        beginning from the first element that leads to the final element. If there is no
        such route, then this function simply returns an empty list (no path exists).

        Args:
            vertices: A list of vertices that must be traversed for the path.
        """
        totPath = list()
        for vertInd in range(len(vertices)-1):
            curPathTup = (vertices[vertInd], vertices[vertInd]+1)
            if self.edgeMatrix.get(curPathTup, None) is None:
                return []
            else:
                totPath.append(self.edgeMatrix[curPathTup])
        
        return totPath
    
    def __str__(self):
        return "Graph with {} vertices and {} edges.".format(len(self.nodeAdjList.keys()),
                                                             len(self.edgeMatrix.keys()))