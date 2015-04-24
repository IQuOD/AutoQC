import combineTests
import benchmarks

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


def test_combineLogic_spotcheck():
    '''
    check if a particular example works out the way it should
    '''
    table = [[True, True],[False, True],[False, False], [False, False]]

    assert combineTests.combineLogic(table, [[0], [1], [2,3]]) == [True, True]
    assert combineTests.combineLogic(table, [[1], [2,3]]) == [False, True]
    assert combineTests.combineLogic(table, [[3], [0]]) == [True, True]
    assert combineTests.combineLogic(table, [[3]]) == [False, False]

def test_combineRows_spotcheck():
    '''
    check if a particular example works out the way it should
    '''
    table = [[True, True],[False, True],[False, False], [False, False]]

    assert combineTests.combineRows(table, [0,1]) == [False, True]
    assert combineTests.combineRows(table, [1,3,2]) == [False, False]
    assert combineTests.combineRows(table, [1]) == [False, True]

def test_combineTests_spotcheck():
    '''
    check if a particular example works out the way it should
    '''
    table = [[True, True],[False, True]]
    result = combineTests.combineTests(table)
    assert result[0][0:2] == [[[0]], [True, True]]
    assert result[1][0:2] == [[[1]], [False, True]]
    assert result[2][0:2] == [[[0], [1]], [True, True]]
    assert result[3][0:2] == [[[0, 1]], [False, True]]

def test_combinationStr_spotcheck():
    '''
    check a few examples
    '''

    assert combineTests.combinationStr([]) == ''
    assert combineTests.combinationStr([['x', 32]]) == 'x AND 32'
    assert combineTests.combinationStr([['x', 32]], False) == 'x OR 32'
    assert combineTests.combinationStr([[0,1], [12]]) == '(0 AND 1) OR 12'

def test_compare_to_truth_spotcheck():
    '''
    check a few examples
    '''

    dummyCombos = [[ 2, [False, False, True], 3 ], [ 5, [False, True, True], 7 ]]
    compare = benchmarks.compare_to_truth(dummyCombos, [False, True, False])

    assert compare[0][0] == 2
    assert compare[0][1] == [50.0, 0]
    assert compare[0][2] == 3
    assert compare[1][0] == 5
    assert compare[1][1] == [50.0, 100.0]
    assert compare[1][2] == 7
