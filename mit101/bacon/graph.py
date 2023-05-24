"""
graph.py

A modified implementation of a graph in order to accomodate the questions
asked in the assignment. In particular, the concept of edge values are changed
(as all are valued equally) and edges now contain references to any nodes that
it connects. Edges are re-used if they are the same movie and vertices are the
relevant actors.

It seems like duplicity was not relevant in this case, but if it was then the
solution would be to simply convert the edgeMatrix into a dict that maps into
lists containing all possible edges. It's unnecessary because the only time we
need to use more than one potential movie here is in the time we use the edges
as nodes (and thus the edges' references are more important here than the edge
matrix.)
"""
class MovieEdge():
    def __init__(self, actorA, actorB, movieID):
        """
        MovieEdge is a modification of the original Edge class that now keeps track
        of the actors it connects as a web instead. Since there is never a particular
        use for the cloud of edges as is, we can drop that and instead contain within
        this class a set of all actors present within movies.
        """
        self.contActors = {actorA, actorB}
        self.movieID = movieID

    def getValue(self):
        return self.movieID
    
    def addActors(self, actorA, actorB):
        self.contActors.update({actorA, actorB})

    def getActors(self):
        return list(self.contActors)

class BaconGraph():
    def __init__(self):
        """
        A graph is a collection of vertices and edges. Vertices represents specific
        hashable points that are referenceable while the edges represent connections
        between these vertices that can have some custom value. By default,
        an empty graph is always constructed.

        A BaconGraph is special in that it can contain a dictionary that represents
        all of the distances from a particular node. The edges used also now represent
        movies, which keep track of the actors that performed in them.
        """
        self.nodeAdjList = dict()   # A collection of nodes adjacent to a given node
        self.movieEdgeCache = dict()# A cache for movie edges to allow easy access
        self.edgeMatrix = dict()    # The collection of edges making up this graph
                                    # Takes in (vertexA, vertexB) tuples.
        
        # Bacon distance specific functions
        self.distTable = dict()     # maps actors to their bacon distance
        self.revDistTable = dict()  # maps bacon distances to sets of actors
        self.relativeNode = None

    def getVertexNames(self):
        return list(self.nodeAdjList.keys()).copy()

    def addDirectedEdge(self, actorA, actorB, movieID = None):
        """
        Adds an edge to the underlying graph that only goes in one direction.
        
        Args:
            elemA: A hashable element that points towards B
            elemB: A hashable element that is pointed to by A
        """
        if self.nodeAdjList.get(actorA, None) is None:
            self.nodeAdjList[actorA] = set()

        # adjust adjacency list
        self.nodeAdjList[actorA].add(actorB)

        # update edges by either creating it or adding actors to an existing one
        if movieID in self.movieEdgeCache:
            self.movieEdgeCache[movieID].addActors(actorA, actorB)
        else:
            self.movieEdgeCache[movieID] = MovieEdge(actorA, actorB, movieID)
        self.edgeMatrix[(actorA, actorB)] = self.movieEdgeCache[movieID]

    def addUndirectedEdge(self, actorA, actorB, movieID = None):
        """
        Adds an edge to the given undirected graph. This creates an edge in
        both directions.

        Args:
            elemA: A hashable elem that points towards B
            elemB: A hashable elem that points towards A
        """
        self.addDirectedEdge(actorA, actorB, movieID)
        self.addDirectedEdge(actorB, actorA, movieID)

    def getAdjacentNodes(self, actor):
        """
        Returns a copy of the adjacency list for the given actor.

        Args:
            elemA: The elem to return the adjacency list for.
        """
        return list(self.nodeAdjList[actor]).copy()
    
    def checkEdge(self, actorA, actorB):
        """
        Performs a simple check for a given edge pair. Returns true
        if it exists, and false otherwise.

        Args:
            elemA: A hashable element to check connectivity with B for.
            elemB: A hashable element to check connectivity with A for.
        """
        # trivial return value (every actor acted with themselves)
        if actorA == actorB:
            return True
        
        return True if self.edgeMatrix.get((actorA, actorB), None) is not None else False
    
    def computeDistancesFrom(self, actor):
        """
        Performs a BFS traversal starting from a given actor and computes
        a list of distances for the entire graph given the input. Note that
        this can take quite a bit of time depending on the size of the graph
        and the actual number of reachable elements.

        Args:
            elem: The node to calculate all distances from
        """
        # initialize our traversal and resultant dictionary
        visited = {actor}
        toVisit = [(actor, int(0))]
        distDict = {actor: 0}
        revDistDict = {0: {actor}}
        
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

                # forward
                distDict[childNode] = curDist + 1
                toVisit.append((childNode, curDist + 1))

                # reverse
                if revDistDict.get(curDist+1, None) is None:
                    revDistDict[curDist+1] = set()
                revDistDict[curDist+1].add(childNode)

        # and then save this element
        self.distTable = distDict
        self.relativeNode = actor
        self.revDistTable = revDistDict

    def getDistanceTo(self, actor):
        """
        Returns the "bacon distance" to the specific actor. Node that this function
        must be run after the above function as the above is in charge of defining
        the relative node in question. If the node does not exist in the graph by the
        time the distances were calculated, then returns None.

        Args:
            elem: The node to calculate the distance to.
        """
        # Enforce relative function order
        if self.relativeNode is None:
            raise RuntimeError("computeDistanceFrom must be run before this function...")
        
        return self.distTable.get(actor, None)
    
    def getAllActorsWithDistance(self, dist):
        """
        Returns the set of all actors within a specified distance from the node used to
        pre-compute distances. Returns None if the node is not connected.

        Args:
            dist: The specified path distance that we are interested in
        """
        if self.relativeNode is None:
            raise RuntimeError("computeDistanceFrom must be run before this function...")
        
        return self.revDistTable.get(dist, set())

    def getNeighbors(self, actor):
        """
        Returns a list of the immediately adjacent neighbors of a given actor.
        This returns a copy so that the user doesn't inadvertedly damage any
        potential objects that are hashable but noted by reference.

        Args:
            elem: The node to acquire the neighbors for.
        """
        return self.nodeAdjList[actor].copy()

    def computeSpecificPath(self, startLoc, endLoc):
        """
        Computes a path from a given actor to another actor.

        Args:
            startLoc: The location to start the traversal from.
            endLoc: The specific node to find the end for
        """
        satFunc = lambda endNode:endNode == endLoc
        return self.computeGeneralPath(startLoc, satFunc)
    
    def computeEdgePath(self, startMovie, endMovie):
        """
        Computes a path from an edge to another edge.

        Args:
            startMovie: The edge to begin traversal from
            endMovie: The edge to end traversal on
        """
        # define satisficing func for this case
        satFunc = lambda endEdge:endEdge == endMovie

        # define method of getting neighbors from edges
        def edgeNeighborFunc(curMovie):
            # find current edge and get all actors
            curEdge = self.movieEdgeCache[curMovie]
            edgeActors = curEdge.getActors()

            # populate all possible movies reachable from movie actors
            neighborMovies = set()
            for actor in edgeActors:
                nActors = self.nodeAdjList[actor]
                for nActor in nActors:
                    neighborMovies.add(self.edgeMatrix[(actor, nActor)].getValue())
                
            return list(neighborMovies)

        return self.computeGeneralPath(startMovie, satFunc, nFunc = edgeNeighborFunc)

    def computeGeneralPath(self, startLoc, satFunc, * , nFunc = None):
        """
        Computes a path to some unspecified ending location depending on what is
        passed to the satisficing function argument. This will be an iterative
        traversal if only because it's possible that the depth could exceed the max
        for our application.

        This function has been adapted to function on edges. The only difference is
        the manner in which neighbors are added.

        Args:
            startLoc: The location to start the graph traversal from.
            satFunc: A satisficing metric. AKA the testing function for the end result.
        """
        # if we have no specific neighbor func, assume actors are nodes
        if nFunc is None:
            nFunc = lambda actor:self.nodeAdjList[actor]

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
            curNeighbors = nFunc(curNode)
            for childNode in curNeighbors:
                if childNode in visited:
                    continue
                else:
                    visited.add(childNode)
                    parents[childNode] = curNode

                toVisit.append(childNode)

        # no possible path found
        return None

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

        return list(reversed(path))
    
    def computeVertexPathFromEdges(self, edges):
        """
        Like below, if we want to convert form a list of edges back into the related
        vertices, we can do that below. Unlike before, it's possible that we can have
        more than one actor shared between movies, in which case we just choose the
        first in the list.

        Args:
            edges: A list of edges that must be traversed for the path.
        """
        totPath = list()
        for edgeInd in range(len(edges)-1):
            curLMActors = set(self.movieEdgeCache[edges[edgeInd]].getActors())
            curRMActors = set(self.movieEdgeCache[edges[edgeInd+1]].getActors())

            # use the intersection of the actor lists to find a commonality
            relActor = list(curLMActors.intersection(curRMActors))
            if len(relActor) == 0:
                return None
            else:
                totPath.append(relActor[0])

        return totPath

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
            curPathTup = (vertices[vertInd], vertices[vertInd+1])
            if self.edgeMatrix.get(curPathTup, None) is None:
                return None
            else:
                totPath.append(self.edgeMatrix[curPathTup].getValue())
        
        return totPath
    
    def __str__(self):
        return "Graph with {} vertices and {} edges.".format(len(self.nodeAdjList.keys()),
                                                             len(self.edgeMatrix.keys()))