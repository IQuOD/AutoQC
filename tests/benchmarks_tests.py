import util.benchmarks as benchmarks

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