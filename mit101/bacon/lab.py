"""
6.1010 Spring '23 Lab 3: Bacon Number
"""

#!/usr/bin/env python3

import pickle
from graph import BaconGraph

# NO ADDITIONAL IMPORTS ALLOWED!


def transform_data(raw_data, * , relativeActor = None, verbose = False):
    # convert the data into a graph representational data
    datGraph = BaconGraph()
    for datPoint in raw_data:
        datGraph.addUndirectedEdge(datPoint[0], datPoint[1], datPoint[2])
    
    # pre-calculates all the distances with respect to kevin bacon
    if relativeActor is not None:
        if verbose:
            print("==> Precomputing distances from specified actor...")
        datGraph.computeDistancesFrom(relativeActor)

    return datGraph


def acted_together(transformed_data, actor_id_1, actor_id_2):
    return transformed_data.checkEdge(actor_id_1, actor_id_2)


def actors_with_bacon_number(transformed_data, n):
    # Perform precompute if necessary
    if transformed_data.relativeNode is None:
        transformed_data.computeDistancesFrom(4724)
    
    return transformed_data.getAllActorsWithDistance(n)


def bacon_path(transformed_data:BaconGraph, actor_id, * , from_id = 4724):
    # likewise
    if transformed_data.relativeNode is None:
        transformed_data.computeDistancesFrom(4724)

    return transformed_data.computeSpecificPath(from_id, actor_id)


def actor_to_actor_path(transformed_data, actor_id_1, actor_id_2):
    return transformed_data.computeSpecificPath(actor_id_1, actor_id_2)


def actor_path(transformed_data, actor_id_1, goal_test_function):
    return transformed_data.computeGeneralPath(actor_id_1, goal_test_function)


def actors_connecting_films(transformed_data, film1, film2):
    edgePath = transformed_data.computeEdgePath(film1, film2)
    return transformed_data.computeVertexPathFromEdges(edgePath)


if __name__ == "__main__":
    # loads small db
    with open("resources/small.pickle", "rb") as f:
        smalldb = pickle.load(f)

    # additional code here will be run only when lab.py is invoked directly
    # (not when imported from test.py), so this is a good place to put code
    # used, for example, to generate the results for the online questions.
    with open("resources/names.pickle", "rb") as f:
        nameDict = pickle.load(f)

    # And then just figure out the general structure of the file
    print("=========STRUCTURE EVALUATION=========")
    print("Names file is of type {}".format(type(nameDict)))
    print("\tThe name data is organized into tuples as follows: {}".format(list(nameDict.items())[0]))
    print("\tThe actor data is organized into tuples as follows: {}".format(smalldb[0]), end="\n\n")

    # Then we can answer the questiosn on the page given this information.
    print("=========BASIC QUESTIONS========")
    print("The ID number of Paul Borghese is {}".format(nameDict['Paul Borghese']))
    revLookupNameDict = {ID:name for name, ID in nameDict.items()}
    print("The actor with the ID 15186 is {}".format(revLookupNameDict[15186]), end="\n\n")

    # Transform data and answer some simple graph questions
    testGraph = transform_data(smalldb, relativeActor = nameDict['Kevin Bacon'])
    print("Have the following pairs of actors acted together...")
    print("\tAnya Benton and Ewa Froling?\t\t{}".format(acted_together(testGraph, 
                                                                        nameDict['Anya Benton'], 
                                                                        nameDict['Ewa Froling'])))
    print("\tEvan Glenn and Neve Campbell?\t\t{}\n".format(acted_together(testGraph, 
                                                                        nameDict['Evan Glenn'], 
                                                                        nameDict['Neve Campbell'])))
    
    # Look at the tinydb for a bit to hand-calculate a few elements
    print("=====GRABBING RESOURCE FROM TINYDB=====")
    with open("resources/small.pickle", "rb") as f:
        tinydb = pickle.load(f)
    tinyGraph = transform_data(tinydb, relativeActor = nameDict['Kevin Bacon'])
    print(tinyGraph.getAdjacentNodes(4724))
    print(tinyGraph.getAdjacentNodes(1640), end='\n\n')
    # PATH: 4724 -> 2876 -> 1640
    
    # And now we can evalute on the larger db and test bacon numbers with value 6
    print("====== TESTING LARGE DB =========")
    with open("resources/large.pickle", "rb") as f:
        largedb = pickle.load(f)

    largeGraph = transform_data(largedb, relativeActor = nameDict['Kevin Bacon'], verbose = True)
    res5 = {revLookupNameDict[aVal] for aVal in actors_with_bacon_number(largeGraph, 6)}
    print("Set of actors with Bacon number equal to 6: {}".format(res5))

    # And now evaluate a path using the larger db
    res6 = [revLookupNameDict[aID] for aID in bacon_path(largeGraph, nameDict['Hywel Bennett'])]
    print("Path from Kevin Bacon to Hywell Benett: {}".format(res6))

    # and also an arbitrary path while we're at it
    res7 = [revLookupNameDict[aID] for aID in actor_to_actor_path(largeGraph, 
                                                                  nameDict['Ben Kacon'], 
                                                                  nameDict['Apichart Chusakul'])]
    print("Path from Ben Kacon to Apichart Chusakul: {}".format(res7))

    # We are now interested in some of the movies, so we load up the movie ID lookup now
    with open("resources/movies.pickle", "rb") as f:
        movieDict = pickle.load(f)
    revMovieDict = {mID:name for (name, mID) in movieDict.items()}
    
    res8IDPath = actor_to_actor_path(largeGraph, 
                                     nameDict['Kate Jennings Grant'],
                                     nameDict['Iva Ilakovac'])
    res8 = [revMovieDict[mID] for mID in largeGraph.computeEdgePathFromVertices(res8IDPath)]
    print("Movies forming a path between Kate Jennings Grant to Iva Ilakovac: {}".format(res8), end='\n\n')

    # Finally, we deal with movie paths, which require a bit of refactoring about
    # how we detail edges in this graph. For this, we can either invert the meaning
    # between the graphs and create an entirely new object, or we can manipulate the
    # current graph to compute something like a BFS on edges instead.
    print("====== TESTING MOVIES AS NODES ======")
    res9 = actors_connecting_films(largeGraph, 
                                   movieDict['Frost/Nixon'], 
                                   movieDict['It Ends with the Taste of Smoke'])
    res9Human = [revLookupNameDict[aID] for aID in res9]
    print("Actors forming a path between Frost/Nixon and It Ends with the Taste of Smoke: {}".format(res9Human))