# tools for examining combining tests via and / or combinations

import itertools, numpy
from copy import deepcopy

def partition(n):
    '''
    generates ascentding integer partitions of <n>
    adopted from http://jeromekelleher.net/partitions.php
    '''
    a = [0 for i in range(n + 1)]
    k = 1
    y = n - 1
    while k != 0:
        x = a[k - 1] + 1
        k -= 1
        while 2*x <= y:
            a[k] = x
            y -= x
            k += 1
        l = k + 1
        while x <= y:
            a[k] = x
            a[l] = y
            yield a[:k + 2]
            x += 1
            y -= 1
        a[k] = x + y
        y = x + y - 1
        yield a[:k + 1]

def combineLogic(logicTable, partition, a=True):
    '''
    logicTable[i][j]: list of lists of boolean values reflecting the decision made by the ith test on the jth dataset.
    partition: list containing a partition of a subset of the rows of logicTable; partition syntax ANDs
    together elements in a sublist, and ORs together elements in partition if <a>=True, or with AND and OR reversed
    if <a>=False. For example, wit <a>=True

    partition = [[0,3], [1], [7]] means

    (0 AND 3) OR (1) OR (7). Note not all rows need be used.

    Returns a list (same length as range of j in logicTable) of boolean values reflecting the result of
    combining rows in the way described.
    '''

    #all entries in logicTable are bool
    for i in logicTable:
        for j in i:
            assert isinstance(j, bool) or isinstance(j, numpy.bool_)
    #all rows reffed in partition are present in logicTable
    for i in partition:
        for j in i:
            assert j < len(logicTable)
    #all rows reffed in partition only used once each
    assertList = []
    for i in partition:
        for j in i:
            assert j not in assertList
            assertList.append(j)
    #partition must not be empty
    assert len(partition) > 0

    subpartitions = []

    if a:
        for andGroup in partition:
            subpartitions.append(combineRows(logicTable, andGroup))

        result = [False]*len(subpartitions[0])

        for i in range(len(subpartitions)):
            for j in range(len(subpartitions[0])):
                result[j] = result[j] or subpartitions[i][j]

    else:
        for andGroup in partition:
            subpartitions.append(combineRows(logicTable, andGroup, False))

        result = [True]*len(subpartitions[0])

        for i in range(len(subpartitions)):
            for j in range(len(subpartitions[0])):
                result[j] = result[j] and subpartitions[i][j]

    return result

def combineRows(logicTable, rows, a=True):
    '''
    logicTable[i][j]: list of lists of boolean values.
    rows: list of rows of logicTable to and or or together
    a: should rows be ANDed together? Otherwise, OR them together.
    returns: list of result of above operation
    '''

    #row list must not be empty
    assert len(rows) > 0

    result = logicTable[rows[0]][:]
    cols = len(logicTable[0])

    for i in range(1, len(rows)):
        for j in range(cols):
            if a:
                result[j] = result[j] and logicTable[rows[i]][j]
            else:
                result[j] = result[j] or logicTable[rows[i]][j]

    return result

def combineTests(logicTable):
    '''
    Generate all possible paritions of tests into AND / OR combinations, and return the result

    logicTable[i][j]: list of lists of boolean values reflecting the decision made by the ith test on the jth dataset.

    returns a list of lists; each sub-list contains three elements:
     - the partition in question
     - the result of combining rows in <logicTable> per that partition
     - are elements of sublists in a partition ANDed together? (otherwise ORed together, corresponds to <a> in combineRows)
    '''

    totalTests = len(logicTable)

    results = []

    partitions = generateCombinations( range(totalTests) )

    for each_partition in partitions:
        combo = combineLogic(logicTable, each_partition)
        #print combo, each_partition
        results.append([each_partition, combo, True])
        if not unitRows(each_partition):
            combo = combineLogic(logicTable, each_partition, False)
            #print combo, each_partition, 'Logic Switched'
            results.append([each_partition, combo, False])

    return results

def incrementPlaceCounter(counter, maxima):
    '''
    treats the list <counter> like a multi-digit counter with 'places';
    (like a digital clock or an ordinary number)
    max values for each place are in the list <maxima>.
    Increments counter to the next 'tick', and returns the incremented list.
    loops around to 0 at overflow.
    big-endian.
    '''

    counter[-1] = counter[-1] + 1
    copy = counter[:]
    i = 1

    while i <= len(counter):
        if copy[-1*i] == maxima[-1*i]:
            copy[-1*i] = 0
            if (-1*i - 1) >= -1*len(copy):
                copy[-1*i - 1] = copy[-1*i - 1] + 1
            else:
                copy = [0]*len(copy)
        i = i+1

    return copy

def generateSubsets(superset, subsetSize):
    '''
    from the list <superset>, generate all the possible subsets without replacement
    of size <subsetSize>
    '''

    subsets = []
    maxima = [len(superset)]*subsetSize
    counter = range(subsetSize)

    while True:
        if isAscending(counter):
            newSet = []
            for elt in counter:
                newSet.append(superset[elt])
            subsets.append(newSet)
        counter = incrementPlaceCounter(counter, maxima)
        if counter == [0]*subsetSize:
            break

    return subsets

def isAscending(lst):
    '''
    are the elements in <lst> strictly ascending?
    '''

    for i in range(len(lst)-1):
        if lst[i] >= lst[i+1]:
            return False

    return True

def remElts(lst, elts):
    '''
    remove the list of elements <elts> from the list <lst>,
    and return the result
    '''

    copy = lst[:]
    for i in elts:
        del copy[copy.index(i)]

    return copy

def uniqify(lst):
   '''
   returns a unique list of objects drawn from <lst>
   adopted from http://www.peterbe.com/plog/uniqifiers-benchmark
   '''
   noDupes = []
   [noDupes.append(i) for i in lst if not noDupes.count(i)]
   return noDupes

def generatePermutations(superset, partition):
    '''
    generate all possible ways to split <superset> up into subsets of sizes
    listed in <parition>
    '''

    permutations = generateSubsets(superset, partition[-1])
    for j in range(len(permutations)):
        permutations[j] = [[permutations[j]], remElts(superset[:], permutations[j])]

    i = 2
    while (i<=len(partition)):
        previousStep = permutations[:]
        permutations = []

        for partialPart in previousStep:
            nextPart = generateSubsets(partialPart[1], partition[-1*i])

            for np in nextPart:
                nextStepPart = partialPart[0][:]
                nextStepPart.append(np)
                permutations.append([nextStepPart, remElts(partialPart[1], np)])

        i = i+1

    #dump leftovers & double counting
    for i in range(len(permutations)):
        permutations[i] = sorted(permutations[i][0])
    permutations = uniqify(permutations)

    return permutations


def generateCombinations(superset):
    '''
    enumerate all ways to combine subsets of <superset> without replacement
    '''

    combos = []
    partitions = []

    for i in range(1,len(superset)+1):
        partitions += partition(i)

    for part in partitions:
        combos += generatePermutations(superset, part)

    return combos

def unitRows(table):
    '''
    table: list of lists

    returns: is there only one list in <table> OR are all the rows in <table> of length 1?
    '''

    if len(table) == 1:
        return True

    for row in table:
        if len(row) != 1:
            return False

    return True

def combinationStr(partition, a=True):
    '''
    Returns a string showing the logic expressed by the partition.
    a=True means that items in a sublist are ANDed together and list items ORed.
      False means the reverse.
    '''
    text = ''
    start = True
    for item in partition:
        if start:
            start = False
        else:
            if a:
                text += ' OR '
            else:
                text += ' AND '

        if len(item) > 1 and len(partition) > 1:
            text += '('

        subStart = True
        for subitem in item:
            if subStart:
                text += str(subitem)
                subStart = False
            else:
                if a:
                    text += ' AND '
                else:
                    text += ' OR '
                text += str(subitem)

        if len(item) > 1 and len(partition) > 1:
            text += ')'

    return text
