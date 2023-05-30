"""
6.1010 Spring '23 Lab 4: Recipes
"""

import pickle
import sys

sys.setrecursionlimit(20_000)
# NO ADDITIONAL IMPORTS!


def make_recipe_book(recipes):
    """
    Given recipes, a list containing compound and atomic food items, make and
    return a dictionary that maps each compound food item name to a list
    of all the ingredient lists associated with that name.
    """
    recipeDict = dict()

    for item in recipes:
        fType, fName, fComp = item
        if fType == 'compound':
            if fName in recipeDict:
                recipeDict[fName].append(fComp.copy())
            else:
                recipeDict[fName] = [fComp.copy()]

    return recipeDict


def make_atomic_costs(recipes):
    """
    Given a recipes list, make and return a dictionary mapping each atomic food item
    name to its cost.
    """
    atomicDict = dict()

    for item in recipes:
       fType, fName, fCost = item
       if fType == 'atomic':
           atomicDict[fName] = fCost

    return atomicDict


def recursive_lowest_cost_helper(food_item, aDict, rDict, ignoreSet):
    '''
    Recursively calculates the lowest cost method for preparing a certain recipe.
    This function can return a proper cost for a found minimum or None if the 
    initial food_item passed does not exist (or no composite recipe exists, thereof)

    This function was extended to simultaneously produce the desired min recipe along
    with the lowest cost using the two helper functions designed.
    '''
    # recursive edge cases
    if food_item in ignoreSet or (food_item not in aDict and
                                    food_item not in rDict):
        return None, None
    elif food_item in aDict:
        return aDict[food_item], {food_item: 1}

    minCost = None
    minRecipe = None
    for posWays in rDict[food_item]: # list of potential recipes
        curCost = 0
        curRecipe = list()
        for subItem, dup in posWays: # each tuple of (item, count_needed)
            curItemCost, subRecipe = recursive_lowest_cost_helper(subItem, aDict,
                                                                  rDict, ignoreSet)
            
            # edge case for non-present item (reset values)
            if curItemCost is None:
                curCost = minCost
                curRecipe = list()
                break

            # if it exists then continue creating current min recipe
            curCost += dup*curItemCost
            curRecipe.append(scale_recipe(subRecipe, dup))

        # Overwrite cost if it is lower or simply the first non-None element found
        if minCost is not None:
            minRecipe = make_grocery_list(curRecipe) if curCost < minCost else minRecipe
            minCost = min(minCost, curCost)
        else:
            minCost = curCost
            minRecipe = make_grocery_list(curRecipe)

    return minCost, minRecipe


def lowest_cost(recipes, food_item, to_ignore = []):
    """
    Given a recipes list and the name of a food item, return the lowest cost of
    a full recipe for the given food item.

    Args:
        recipes: The list of recipes to search
        food_item: The item for which the lowest cost is desired 
        to_ignore: (Optional) A list containing elements we desire to ignore in the search
    """
    aDict = make_atomic_costs(recipes)
    rDict = make_recipe_book(recipes)
    ignoreSet = set(to_ignore)
    
    # Recursive method can either return None or actual cost
    recursiveCost = recursive_lowest_cost_helper(food_item, aDict, rDict, ignoreSet)[0]
    return recursiveCost


def scale_recipe(flat_recipe, n):
    """
    Given a dictionary of ingredients mapped to quantities needed, returns a
    new dictionary with the quantities scaled by n.
    """
    return {item:quantity*n for item, quantity in flat_recipe.items()}


def make_grocery_list(flat_recipes):
    """
    Given a list of flat_recipe dictionaries that map food items to quantities,
    return a new overall 'grocery list' dictionary that maps each ingredient name
    to the sum of its quantities across the given flat recipes.

    For example,
        make_grocery_list([{'milk':1, 'chocolate':1}, {'sugar':1, 'milk':2}])
    should return:
        {'milk':3, 'chocolate': 1, 'sugar': 1}
    """
    sumDict = dict()
    for rDict in flat_recipes:
        for foodItem in rDict.keys(): 
            sumDict[foodItem] = sumDict.get(foodItem, 0) + rDict[foodItem]

    return sumDict


def cheapest_flat_recipe(recipes, food_item, to_ignore = []):
    """
    Given a recipes list and the name of a food item, return a dictionary
    (mapping atomic food items to quantities) representing the cheapest full
    recipe for the given food item.

    Returns None if there is no possible recipe.
    """
    aDict = make_atomic_costs(recipes)
    rDict = make_recipe_book(recipes)
    ignoreSet = set(to_ignore)
    
    # Recursive method can either return None or actual cost
    minRecipe = recursive_lowest_cost_helper(food_item, aDict, rDict, ignoreSet)[1]
    return None if not minRecipe else minRecipe


def ingredient_mixes(flat_recipes):
    """
    Given a list of lists of dictionaries, where each inner list represents all
    the flat recipes make a certain ingredient as part of a recipe, compute all
    combinations of the flat recipes.
    """
    raise NotImplementedError


def all_flat_recipes(recipes, food_item):
    """
    Given a list of recipes and the name of a food item, produce a list (in any
    order) of all possible flat recipes for that category.

    Returns an empty list if there are no possible recipes
    """
    raise NotImplementedError


if __name__ == "__main__":
    # load example recipes from section 3 of the write-up
    with open("test_recipes/example_recipes.pickle", "rb") as f:
        example_recipes = pickle.load(f)
    # you are free to add additional testing code here!
    # Tere are 16 atomic items. And since there were 28 total items, there
    # must be 12 compound items in the list

    # Load up the datasets into their appropriate dicts
    aDict = make_atomic_costs(example_recipes)
    rDict = make_recipe_book(example_recipes)

    # 4.0.0 - Check cost of buying one of every atomic item
    print("\n========== PART 4 =========\n")
    totCost = sum(list(aDict.values()))
    print("The total cost of buying one of every atomic item is {}".format(totCost))

    # 4.0.1 - And now see how many compound food item can be made multiple ways
    dupPossCnt = sum([min(len(recipeList), 2)-1 for recipeList in rDict.values()])
    print("There are {} items that can be made more than one way in this recipe list.".format(dupPossCnt))

    # 5.0 smoke test for lowest cost using a known recipe
    print("\n========= PART 5 ==========\n")
    dairy_recipes = [
        ('compound', 'milk', [('cow', 2), ('milking stool', 1)]),
        ('compound', 'cheese', [('milk', 1), ('time', 1)]),
        ('compound', 'cheese', [('cutting-edge laboratory', 11)]),
        ('atomic', 'milking stool', 5),
        ('atomic', 'cutting-edge laboratory', 1000),
        ('atomic', 'time', 10000),
        ('atomic', 'cow', 100)]
    print("The cheapest cost for producing cheese is {}".format(lowest_cost(dairy_recipes, 'cheese')))

    # 6.0 smoke test for min recipe of a known recipe set
    print("\n========= PART 6 ==========\n")
    print("The cheapest recipe for cheese using the dairy recipes is {}".format(cheapest_flat_recipe(dairy_recipes,
                                                                                                     'cheese')))
    print("And now after forbidding usage of cows: {}".format(cheapest_flat_recipe(dairy_recipes,
                                                                                   'cheese',
                                                                                   ['cow'])))
    
    # 7.0 smoke test all flat recipe counter