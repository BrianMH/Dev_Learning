"""
6.1010 Spring '23 Lab 9: Autocomplete
"""

# NO ADDITIONAL IMPORTS!
import doctest
from text_tokenize import tokenize_sentences


class PrefixTree:
    def __init__(self):
        """
        A prefix tree is essentially a (maximally) 26-ary tree where the
        edges connecting the nodes are the letters of a word and the nodes
        themselves can contain values that can be looked up and returned.
        """
        self.value = None
        self.children : dict[str, 'PrefixTree'] = dict()


    def incrementValue(self, key: str, amount: int) -> None:
        """
        Increments the value of a certain key by a certain amount. Note that
        if the stored value is not a numerical value or a class that can 
        add integers to itself, this will throw an exception.
        For any key that doesn't already exist. This simply creates it.
        """
        if not isinstance(key, str):
            raise TypeError("PrefixTree only accepts string keys.")
        
        # Performs the operation in one step
        # (This can be optimized by returning the parent instead and adjusting 
        #  the subkey from that)
        relNode = self._getNode_(self, key)
        if relNode is None:
            self[key] = amount
        elif relNode.value is None:
            relNode.value = amount
        else:
            relNode.value += amount


    def __setitem__(self, key: str, value) -> None:
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

        >>> trie["test"] = "testing"
        >>> trie["test"] == "testing"
        True
        >>> trie["test"] = "overwriting"
        >>> trie["test"] == "overwriting"
        True
        >>> trie["test"] == "testing"
        False
        """
        if not isinstance(key, str):
            raise TypeError("PrefixTree only accepts string keys.")
        
        relNode = self._getNode_(self, key)
        if relNode is None or relNode.value is None:
            raise KeyError("Key is not found in the tree.")
        
        return relNode.value

    def __delitem__(self, key: str) -> None:
        """
        Delete the given key from the prefix tree if it exists.
        Raise a KeyError if the given key is not in the prefix tree.
        Raise a TypeError if the given key is not a string.

        >>> trie['test'] = 0
        >>> del trie['test']
        >>> 'test' not in trie
        True
        >>> 'test' not in [word for word,_ in trie]
        True
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
            if curNode.value is None and len(curNode.children.keys()) == 0: # no children
                del parentNode.children[key[kInd-1]]

            curNode = parentNode
            parentNode = nodeStack.pop()
            kInd -= 1


    def __contains__(self, key: str) -> bool:
        """
        Is key a key in the prefix tree?  Return True or False.
        Raise a TypeError if the given key is not a string.

        >>> words = ["test", "testing", "tester", "tested", "testlonger"]
        >>> for word in words: 
        ...     trie[word] = "inserted"
        >>> presence = []
        >>> for word in words:
        ...     presence.append(word in trie)
        >>> all(presence)
        True
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


    def prefixIter(self, prefix: str):
        """
        Returns a generator of (key, value) pairs for all keys/values in a specified
        sub prefix tree and its children.
        """
        if not isinstance(prefix, str):
            raise TypeError("Prefix must be a string.")
        
        relTree = self._getNode_(self, prefix)
        if relTree is None:
            yield from ()
        else:
            yield from relTree.__iter__()


    def globWords(self, expr: str, curPrefix: str = "") -> set[str]:
        '''
        Recursively attempts to match words to a given expression that can include
        the ? and * wildcards. ? matches single character (guaranteed to match),
        while * can match zero or more characters.
        '''
        # Early termination cases
        if expr == "" and self.value is not None:
            return {(curPrefix, self.value)}
        elif expr == "":
            return set()
        elif expr == "*": #early termination
            return {(curPrefix+subStr, freq) for subStr, freq in self}

        # Attempt to divide the problem depending on the current expression encountered
        if expr[0].isalpha(): # match all character exprs found
            eInd = 1
            while eInd < len(expr) and expr[eInd].isalpha():
                eInd += 1

            newRoot = self._getNode_(self, expr[:eInd])
            # edge case for non-existant substr
            if newRoot is None:
                return set()
            
            return newRoot.globWords(expr[eInd:], curPrefix+expr[:eInd])
        elif expr[0] == '?': # match a single character (guaranteed)
            retStrings = set()
            for newChar, newRoot in self.children.items():
                retStrings = retStrings | newRoot.globWords(expr[1:], curPrefix+newChar)
            
            return retStrings
        elif expr[0] == '*': # match as many or as little characters
            retStrings = self.globWords(expr[1:], curPrefix) # glob 0
            for newChar, newRoot in self.children.items():
                retStrings = retStrings | newRoot.globWords(expr[1:], curPrefix+newChar) # glob 1
                retStrings = retStrings | newRoot.globWords(expr, curPrefix+newChar) # glob 2+
            
            return retStrings
        else:
            raise ValueError("Expression encountered an unknown character: {}".format(expr[0]))


    def __str__(self):
        """
        A string representation of the trie. There's not really an easy way to show
        this, so this just prints the collection of words in the trie instead.
        """
        return [word for word in self].__str__()


def word_frequencies(text):
    """
    Given a piece of text as a single string, create a prefix tree whose keys
    are the words in the text, and whose values are the number of times the
    associated word appears in the text.

    >>> corpus = '''Lorem ipsum dolor sit amet, consectetur adipiscing elit,
    ...           sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
    ...           Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris
    ...           nisi ut aliquip ex ea commodo consequat.'''
    >>> x = word_frequencies(corpus)
    >>> corpus = [sentence.split() for sentence in tokenize_sentences(corpus)]
    >>> all([(word in x) and (1 <= x[word] <= 3) for sentence in corpus for word in sentence])
    True
    """
    tokens = [sentence.split() for sentence in tokenize_sentences(text)]
    tokens = [elem for subList in tokens for elem in subList]
    freqTree = PrefixTree()
    for tok in tokens:
        freqTree.incrementValue(tok, 1)

    return freqTree


def autocomplete(tree: PrefixTree, prefix, max_count=None):
    """
    Return the list of the most-frequently occurring elements that start with
    the given prefix.  Include only the top max_count elements if max_count is
    specified, otherwise return all.

    Raise a TypeError if the given prefix is not a string.
    """
    if not isinstance(prefix, str):
        raise TypeError("Prefix must be a string.")
    
    topElements : list[tuple[int, str]] = list()
    for rWord, count in tree.prefixIter(prefix):
        topElements.append((rWord, count))
        if max_count is not None and len(topElements) > max_count:
            topElements = sorted(topElements, key = lambda tup:tup[1], reverse = True)[:-1]

    return [prefix+end for end,_ in topElements]


def generate_single_edit_candidates(word: str):
    """
    Returns a list of unique single edit candidates where the edits can be one 
    of the following:
        1) A single-edit insertion at any index
        2) A single-edit deletion of any index
        3) A single character replacement
        4) A two-character transpose (swapping)
    Note that this function makes no assessment of the word's existence in any
    tree.

    Args:
        word: The word for which to generate single edit candidates.
    """
    alphabet = "abcdefghijklmnopqrstuvwxyz"
    visited = set()

    # inserts
    for wInd in range(len(word)+1):
        for curChar in alphabet:
            curCand = word[:wInd]+curChar+word[wInd:]
            if curCand not in visited:
                yield curCand
                visited.add(curCand)

    # deletions
    for wInd in range(len(word)):
        curCand = word[:wInd]+word[wInd+1:]
        if curCand not in visited:
            yield curCand
            visited.add(curCand)

    # replacements
    for wInd in range(len(word)):
        for curChar in alphabet:
            if curChar == word[wInd]:
                continue

            curCand = word[:wInd]+curChar+word[wInd+1:]
            if curCand not in visited:
                yield curCand
                visited.add(curCand)

    # transposes
    for wInd in range(len(word)-1):
        curCand = word[:wInd] + word[wInd+1] + word[wInd] + word[wInd+2:]
        if curCand not in visited:
            yield curCand
            visited.add(curCand)


def autocorrect(tree, prefix, max_count=None):
    """
    Return the list of the most-frequent words that start with prefix or that
    are valid words that differ from prefix by a small edit.  Include up to
    max_count elements from the autocompletion.  If autocompletion produces
    fewer than max_count elements, include the most-frequently-occurring valid
    edits of the given word as well, up to max_count total elements.
    """
    # first generate the autocomplete responses
    autocompResults = set(autocomplete(tree, prefix, max_count))

    # then generate however many results we need from the autocorrect side
    acLen = None if max_count is None else max_count - len(autocompResults)

    # and perform autocorrect
    topElements : list[tuple[int, str]] = list()
    for newWord in generate_single_edit_candidates(prefix):
        if newWord not in tree or newWord in autocompResults:
            continue

        topElements.append((newWord, tree[newWord]))
        if acLen is not None and len(topElements) > acLen:
            topElements = sorted(topElements, key = lambda tup:tup[1], reverse = True)[:-1]

    return list(autocompResults) + [word for word,_ in topElements]


def word_filter(tree: 'PrefixTree', pattern):
    """
    Return list of (word, freq) for all words in the given prefix tree that
    match pattern.  pattern is a string, interpreted as explained below:
         * matches any sequence of zero or more characters,
         ? matches any single character,
         otherwise char in pattern char must equal char in word.
    """
    return list(tree.globWords(pattern))


# you can include test cases of your own in the block below.
if __name__ == "__main__":
    doctest.testmod(extraglobs={'trie': PrefixTree()})
