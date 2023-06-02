"""
6.1010 Spring '23 Lab 9: Autocomplete
"""

# NO ADDITIONAL IMPORTS!
import doctest
from text_tokenize import tokenize_sentences


class PrefixTree:
    CHAR_LEN = 26      # used to keep count of number of potential edges from a node

    def __init__(self):
        """
        A prefix tree is essentially a (maximally) 26-ary tree where the
        edges connecting the nodes are the letters of a word and the nodes
        themselves can contain values that can be looked up and returned.
        """
        self.value = None
        self.children : dict[str, 'PrefixTree'] = dict()


    def __setitem__(self, key: str, value):
        """
        Add a key with the given value to the prefix tree,
        or reassign the associated value if it is already present.
        Raise a TypeError if the given key is not a string.
        """
        if not isinstance(key, str):
            raise TypeError
        
        curNode = self
        kInd = 0
        # traverse as far as possible without making new nodes
        while kInd < len(key) and curNode.children.get(key[kInd], None) is not None:
            curNode = curNode.children.get(key[kInd])
            kInd += 1

        # Then create however many new nodes as necessary
        for ntcInd in range(kInd, len(key)):
            curNode.children[key[ntcInd]] = PrefixTree()
            curNode = curNode.children[key[ntcInd]]
        
        # Then assign the desired value
        curNode.value = value
        

    def _getNode_(self, startNode: 'PrefixTree', edgeSeq: str) -> 'PrefixTree':
        """
        Helper function that traverses the tree starting from a given
        node while following a designated set of edges (string chars)

        Returns None if the node simply doesn't exist along the way.
        """
        curNode = startNode
        eInd = 0
        while curNode and eInd < len(edgeSeq):
            curNode = curNode.children.get(edgeSeq[eInd], None)
            eInd += 1

        return curNode

    def __getitem__(self, key: str):
        """
        Return the value for the specified prefix.
        Raise a KeyError if the given key is not in the prefix tree.
        Raise a TypeError if the given key is not a string.
        """
        if not isinstance(key, str):
            raise TypeError("PrefixTree only accepts string keys.")
        
        relNode = self._getNode_(self, key)
        if relNode is None:
            raise KeyError("Key is not found in the tree.")
        
        return relNode.value

    def __delitem__(self, key: str):
        """
        Delete the given key from the prefix tree if it exists.
        Raise a KeyError if the given key is not in the prefix tree.
        Raise a TypeError if the given key is not a string.
        """
        if not isinstance(key, str):
            raise TypeError("PrefixTree only acceps string keys.")
        elif key == "": # special case where value is assigned to root
            self.value = None
        
        # To figure out what to delete, we walk and keep a stack of touched
        # points. We begin by deleting the value intrinsic to the string, if
        # it exists, and finish by pruning the tree on the way back up if no
        # references exist that depend on that node.
        curNode = self
        kInd = 0
        nodeStack = [PrefixTree()] # dummy for deletion
        while curNode is not None and kInd < len(key):
            # add to stack and move to next node
            nodeStack.append(curNode)
            curNode = curNode.children.get(key[kInd], None)
            kInd += 1

        # Early termination
        if curNode is None or curNode.value is None:
            raise KeyError("Key is not found in the prefix tree.")
        
        # Now perform the deletion
        curNode.value = None
        parentNode = nodeStack.pop()
        while nodeStack:
            if len(curNode.children.keys()) == 0: # no children
                del parentNode.children[key[kInd-1]]

            curNode = parentNode
            parentNode = nodeStack.pop()
            kInd -= 1


    def __contains__(self, key: str):
        """
        Is key a key in the prefix tree?  Return True or False.
        Raise a TypeError if the given key is not a string.
        """
        if not isinstance(key, str):
            raise TypeError("PrefixTree only accepts string keys.")
        
        relNode = self._getNode_(self, key)
        return False if (relNode is None or relNode.value is None) else True


    def __iter__(self):
        """
        Generator of (key, value) pairs for all keys/values in this prefix tree
        and its children.  Must be a generator!
        """
        # Perform a "pre-order" traversal (not quite since children are unordered)
        nodeQueue = [(self, "")]
        while nodeQueue:
            curNode, curStr = nodeQueue.pop()

            # yield current node if it's a candidate
            if curNode.value is not None:
                yield (curStr, curNode.value)
            
            # Then iterate over children
            nodeQueue.extend([(node, curStr+char) for char, node in curNode.children.items()])


def word_frequencies(text):
    """
    Given a piece of text as a single string, create a prefix tree whose keys
    are the words in the text, and whose values are the number of times the
    associated word appears in the text.
    """
    raise NotImplementedError


def autocomplete(tree, prefix, max_count=None):
    """
    Return the list of the most-frequently occurring elements that start with
    the given prefix.  Include only the top max_count elements if max_count is
    specified, otherwise return all.

    Raise a TypeError if the given prefix is not a string.
    """
    raise NotImplementedError


def autocorrect(tree, prefix, max_count=None):
    """
    Return the list of the most-frequent words that start with prefix or that
    are valid words that differ from prefix by a small edit.  Include up to
    max_count elements from the autocompletion.  If autocompletion produces
    fewer than max_count elements, include the most-frequently-occurring valid
    edits of the given word as well, up to max_count total elements.
    """
    raise NotImplementedError


def word_filter(tree, pattern):
    """
    Return list of (word, freq) for all words in the given prefix tree that
    match pattern.  pattern is a string, interpreted as explained below:
         * matches any sequence of zero or more characters,
         ? matches any single character,
         otherwise char in pattern char must equal char in word.
    """
    raise NotImplementedError


# you can include test cases of your own in the block below.
if __name__ == "__main__":
    doctest.testmod()

    # Make some very simple test cases
    curTrie = PrefixTree()

    # assignment + iteration
    curTrie["test"] = "testing"
    assert curTrie["test"] == "testing", "Assignment failed."
    curTrie["test"] = "overwriting"
    assert curTrie["test"] == "overwriting", "Assignment + overwriting failed."
    for element in curTrie:
        assert element == ("test", "overwriting"), "Iterator provided an incorrect response."

    # deletion + iteration
    del curTrie["test"]
    for element in curTrie:
        assert False, "There must be no elements in the tree after deletion."

    # nested insertion + containment + deletion
    wordsToAdd = {'make': 'Toyota', 'model': 'Corolla', 'year': 2006, 'color': 'beige', 'storage space': ''}
    for word, val in wordsToAdd.items():
        curTrie[word] = val
        assert word in [word for word,_ in curTrie], "Failed to find \"{}\"".format(word)
        assert curTrie[word] == val, "Batch assignment failed"
        assert word in curTrie, "Could not find added word within the tree."
    for word, _ in wordsToAdd.items():
        del curTrie[word]
        assert word not in [word for word,_ in curTrie], "Iterator providing incorrect results."
        assert word not in curTrie, "Word still in trie after deletion."
    for element in curTrie:
        assert False, "There must be no elements in tree after deletion."