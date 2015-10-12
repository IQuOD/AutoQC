import util.svmClassifier as svmClassifier
import numpy

def test_transpose():
    '''
    check some basic behavior of transpose
    '''

    matrix = [[1,2],[3,4],[5,6]]
    T = svmClassifier.transpose(matrix)

    assert numpy.array_equal(T, [[1,3,5],[2,4,6]]), 'incorrect transposition'

def test_training():
    '''
    trivial test to make sure we have a functioning SVM:
    '''

    classifier = svmClassifier.trainSVM([[0,0,0],[1,1,1]], [False, True])

    assert classifier.predict([1,1,1]), 'trivial svm training failed.'

def test_assessResults():
    '''
    simple test of the full svm analysis
    '''

    testA = [0,0,1,1,1,0,1,0,0]
    testB = [1,0,1,0,1,1,0,1,1]
    truth = [0,1,1,0,1,0,0,0,0]

    TT, TF, FT, FF = svmClassifier.assessResults([testA, testB], truth, 4)

    assert TT==1, 'wrong TT on trivial test (svm should be perfect in this case)'
    assert TF==0, 'wrong TF on trivial test (svm should be perfect in this case)'
    assert FT==0, 'wrong FT on trivial test (svm should be perfect in this case)'
    assert FF==4, 'wrong FF on trivial test (svm should be perfect in this case)'

def shuffleList_test():
    '''
    check behavior of shuffling.
    '''

    a = [1,2,3,4,5]
    b = ['a', 'b', 'c', 'd', 'e']
    svmClassifier.shuffleLists(a,b)

    assert a[b.index('d')] == 4, 'lists did not maintain pairwise correspondence after shuffling.'