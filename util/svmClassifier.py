from sklearn import svm
import random
import numpy as np

def transpose(lists):
    '''
    return the transpose of lists, a list of lists.
    all the inner lists had better be the same length!
    '''

    T = []
    for i in range(len(lists[0])):
        T.append([None]*len(lists))

    for i in range(len(lists)):
        for j in range(len(lists[0])):
            T[j][i] = lists[i][j]

    return T


def trainSVM(data, labels):
    '''
    data[i][j]: jth observation of the ith dataset
    labels[i]: correct classification of the ith dataset
    returns an svm trained on data and labels.
    '''

    classifier = svm.SVC(kernel=DNF_kernel, class_weight='auto')
    classifier.fit(data, labels)
    return classifier

def shuffleLists(a, b):
  '''
  given two lists a, b, shuffle them maintaining pairwise correspondence.
  thanks http://stackoverflow.com/questions/13343347/randomizing-two-lists-and-maintaining-order-in-python
  '''

  combined = zip(a, b)
  random.seed(2154)
  random.shuffle(combined)

  a[:], b[:] = zip(*combined)

def DNF_kernel_elt(u,v):
    '''
    construct the term of the kernel matrix corresponding to vectors u and v.
    '''

    k = 1
    assert len(u) == len(v), 'input arrays to DNF_kernel must be the same length.'
    for i in range(len(u)):
        k = k*(2*u[i]*v[i] - u[i] - v[i] + 2)

    return k-1

def DNF_kernel(U,V):
    '''
    disjunctive normal form kernel from Sadohara:
    http://citeseerx.ist.psu.edu/viewdoc/download;jsessionid=ED6330AC1297BAAA56EF7FB507AFDFF3?doi=10.1.1.103.7219&rep=rep1&type=pdf
    '''

    rows = []
    columns = []

    for i in range(len(U)):
        for j in range(len(V)):
            columns.append(DNF_kernel_elt(U[i], V[j]))
        rows.append(columns)
        columns = []

    return np.array(rows)


def assessResults(rawData, truth, trainingSize=5000):
    '''
    rawData[i][j] = ith observation of the jth dataset
    truth[j] = correct classification of the jth dataset
    trainingSize<j = how much of the data to train on
    returns the numbers of TT, TF, FT, FF (assessed:correct)
    '''

    data = transpose(rawData)
    #shuffleLists(data, truth)
    classifier = trainSVM(data[0:trainingSize], truth[0:trainingSize])

    TT = 0
    TF = 0
    FT = 0
    FF = 0

    for i in range(trainingSize, len(truth)):
        assessment = classifier.predict(data[i])
        if assessment and truth[i]:
            TT += 1
        elif assessment and not truth[i]:
            TF += 1
        elif not assessment and truth[i]:
            FT += 1
        elif not assessment and not truth[i]:
            FF += 1

    return TT, TF, FT, FF