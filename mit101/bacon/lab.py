"""
6.1010 Spring '23 Lab 3: Bacon Number
"""

#!/usr/bin/env python3

import pickle
from graph import Graph

# NO ADDITIONAL IMPORTS ALLOWED!


def transform_data(raw_data):
    # convert the data into a graph representational data
    datGraph = Graph()
    for datPoint in raw_data:
        datGraph.addUndirectedEdge(datPoint[0], datPoint[1], datPoint[2])

    return datGraph


def acted_together(transformed_data, actor_id_1, actor_id_2):
    return transformed_data.checkEdge(actor_id_1, actor_id_2)


def actors_with_bacon_number(transformed_data, n):
    raise NotImplementedError("Implement me!")


def bacon_path(transformed_data, actor_id):
    raise NotImplementedError("Implement me!")


def actor_to_actor_path(transformed_data, actor_id_1, actor_id_2):
    raise NotImplementedError("Implement me!")


def actor_path(transformed_data, actor_id_1, goal_test_function):
    raise NotImplementedError("Implement me!")


def actors_connecting_films(transformed_data, film1, film2):
    raise NotImplementedError("Implement me!")


if __name__ == "__main__":
    with open("resources/small.pickle", "rb") as f:
        smalldb = pickle.load(f)

    # additional code here will be run only when lab.py is invoked directly
    # (not when imported from test.py), so this is a good place to put code
    # used, for example, to generate the results for the online questions.
    with open("resources/names.pickle", "rb") as f:
        nameDict = pickle.load(f)

    # And then just figure out the general structure of the file
    print("Names file is of type {}".format(type(nameDict)))
    print("\tThe name data is organized into tuples as follows: {}".format(list(nameDict.items())[0]))
    print("\tThe actor data is organized into tuples as follows: {}".format(smalldb[0]))

    # Then we can answer the questiosn on the page given this information.
    print("The ID number of Paul Borghese is {}".format(nameDict['Paul Borghese']))
    revLookupNameDict = {ID:name for name, ID in nameDict.items()}
    print("The actor with the ID 15186 is {}".format(revLookupNameDict[15186]))

    # Test the data representation of (actor/actor/movie) tuples
    testGraph = transform_data(smalldb)
    print(len(smalldb), testGraph)

    # Evaluate 4) Acting Together
    print("Have the following pairs of actors acted together...")
    print("\tAnya Benton and Ewa Froling?\t\t{}".format(acted_together(testGraph, 
                                                                        nameDict['Anya Benton'], 
                                                                        nameDict['Ewa Froling'])))
    print("\tEvan Glenn and Neve Campbell?\t\t{}".format(acted_together(testGraph, 
                                                                        nameDict['Evan Glenn'], 
                                                                        nameDict['Neve Campbell'])))
    
    # Evaluate 5) Bacon Number
    