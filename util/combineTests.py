import itertools
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

def slice_by_lengths(lengths, the_list):
    '''
    adopted from http://stackoverflow.com/questions/19368375/set-partitions-in-python
    takes <the_list> and breaks it up into sublists, of the lengths listed in <lengths>
    '''

    assert sum(lengths) == len(the_list), 'must break list up into sublist with nothing missing and no left-overs'

    for length in lengths:
        new = []
        for i in range(length):
            new.append(the_list.pop(0))
        yield new

def subgrups(my_list):
    '''
    adopted from http://stackoverflow.com/questions/19368375/set-partitions-in-python
    forms all subgroups of elements in a list, without reordering
    '''
    partitions = partition(len(my_list))
    permed = []
    for each_partition in partitions:
        permed.append(set(itertools.permutations(each_partition, len(each_partition))))

    for each_tuple in itertools.chain(*permed):
        yield list(slice_by_lengths(each_tuple, deepcopy(my_list)))

def subsetter(nItems, subSize):
    '''
    returns a list containing every possible partition of the set of size <subSize> drawn
    without replacement from the list of integers 0..nItems-1
    '''

    subs = []

    for i in itertools.combinations(range(nItems), subSize):
        for j in subgrups(list(i)):
            subs.append(j)

    return subs

def combineLogic(logicTable, partition):
    '''
    logicTable[i][j]: list of lists of boolean values reflecting the decision made by the ith test on the jth dataset.
    partition: list containing a partition of a subset of the rows of logicTable; partition syntax ANDs
    together elements in a sublist, and ORs together elements in partition. For example,

    partition = [[0,3], [1], [7]] means

    (0 AND 3) OR (1) OR (7). Note not all rows need be used.

    Returns a list (same length as range of j in logicTable) of boolean values reflecting the result of
    combining rows in the way described.
    '''

    #all entries in logicTable are bool
    for i in logicTable:
        for j in i:
            assert isinstance(j, bool)
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

    for andGroup in partition:
        subpartitions.append(andRows(logicTable, andGroup))

    result = [False]*len(subpartitions[0])

    for i in range(len(subpartitions)):
        for j in range(len(subpartitions[0])):
            result[j] = result[j] or subpartitions[i][j]

    return result

def andRows(logicTable, rows):
    '''
    logicTable[i][j]: list of lists of boolean values.
    rows: list of rows of logicTable to and together

    returns: list of result of above operation
    '''

    #row list must not be empty
    assert len(rows) > 0

    result = logicTable[rows[0]][:]
    cols = len(logicTable[0])

    for i in range(1, len(rows)):
        for j in range(cols):
            result[j] = result[j] and logicTable[rows[i]][j]

    return result

def combineTests(logicTable):
    '''
    Generate all possible paritions of tests into AND / OR combinations, and return the result

    logicTable[i][j]: list of lists of boolean values reflecting the decision made by the ith test on the jth dataset.
    '''

    totalTests = len(logicTable)

    results = []

    #consider combining every possible number of tests, from a single test to all of them
    for nTests in range(1,totalTests+1):
         parts = subsetter(totalTests, nTests)

         for each_part in parts:
             combo = combineLogic(logicTable, each_part)
             print combo, each_part
             results.append([each_part, combo])

    return results





table = [[True, True],[False, True],[False, False], [False, False]]

res = combineTests(table)
