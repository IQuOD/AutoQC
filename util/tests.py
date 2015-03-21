import combineTests


def test_partition_type():
    '''
    all elements of the partition must be lists
    '''
    testPartition = combineTests.partition(7)
    for i in testPartition:
        assert isinstance(i, list)

def test_partition_ascention_start():
    '''
    ascending parition should start with [1,1,....,1]
    '''
    testPartition = combineTests.partition(5)
    for i in testPartition:
        assert i == [1,1,1,1,1], "ascending partition doesn't begin with [1,1,...,1]"
        return

def test_partition_ascention_end():
    '''
    ascending parition should end with [n]
    '''
    testPartition = combineTests.partition(5)
    dumpPartition = []
    for i in testPartition:
        dumpPartition.append(i)

    assert dumpPartition[-1] == [5], "ascending partition doesn't end with [n]"

def test_slice_by_lengths_lengthCheck():
    '''
    do we actually get sub lists of the lengths we asked for?
    '''

    lengths = [1,2,2]
    testList = [10,34,76,20,86]
    sliced = combineTests.slice_by_lengths(lengths, testList)

    count = 0
    for i in sliced:
        assert len(i) == lengths[count]
        count = count + 1

def test_slice_by_lengths_ordering():
    '''
    does everything stay in the same order?
    '''

    lengths = [1,2,2]
    testList = [10,34,76,20,86]
    copy = list(testList)
    sliced = combineTests.slice_by_lengths(lengths, testList)

    composed = []

    for i in sliced:
        composed = composed + i

    assert composed == copy

def test_subgrups_type():
    '''
    all elements returned by subgrups' yield should be lists
    '''
    test = combineTests.subgrups([1,2,3])
    for i in test:
        assert isinstance(i, list)

def test_subgrups_consistency():
    '''
    every subgrouping should be the same as the original list when merged
    '''

    test = combineTests.subgrups([1,2,3])
    merged = []
    for i in test:
        merged = []
        for j in i:
            merged = merged + j
        assert merged == [1,2,3]

def test_subsetter_tooBig():
    '''
    if asked for a subset bigger than the original set, should just get []
    '''

    assert combineTests.subsetter(3,2161) == []

def test_subsetter_setsize():
    '''
    is every subset the size we asked for?
    '''

    test = combineTests.subsetter(5,3)
    merged = []
    for i in test:
        merged = []
        for j in i:
            merged = merged + j
        assert len(merged) == 3

def test_subsetter_no_new_elements():
    '''
    is every subset actually a subset of the original?
    '''

    test = combineTests.subsetter(5,3)

    for i in test:
        testset = range(5)
        for j in i:
            for k in j:
                assert testset.index(k) >= 0
                del testset[testset.index(k)]

def test_combineLogic_spotcheck():
    '''
    check if a particular example works out the way it should
    '''
    table = [[True, True],[False, True],[False, False], [False, False]]

    assert combineTests.combineLogic(table, [[0], [1], [2,3]]) == [True, True]
    assert combineTests.combineLogic(table, [[1], [2,3]]) == [False, True]
    assert combineTests.combineLogic(table, [[3], [0]]) == [True, True]
    assert combineTests.combineLogic(table, [[3]]) == [False, False]

def test_andRows_spotcheck():
    '''
    check if a particular example works out the way it should
    '''
    table = [[True, True],[False, True],[False, False], [False, False]]

    assert combineTests.andRows(table, [0,1]) == [False, True]
    assert combineTests.andRows(table, [1,3,2]) == [False, False]
    assert combineTests.andRows(table, [1]) == [False, True]

def test_combineTests_spotcheck():
    '''
    check if a particular example works out the way it should
    '''
    table = [[True, True],[False, True]]
    result = combineTests.combineTests(table)
    assert result[0] == [[[0]], [True, True]]
    assert result[1] == [[[1]], [False, True]]
    assert result[2] == [[[0], [1]], [True, True]]
    assert result[3] == [[[0, 1]], [False, True]] 
