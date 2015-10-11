from sklearn import svm

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

    classifier = svm.SVC()
    classifier.fit(data, labels)
    return classifier

def assessResults(rawData, truth, trainingSize=5000):
    '''
    rawData[i][j] = ith observation of the jth dataset
    truth[j] = correct classification of the jth dataset
    trainingSize<j = how much of the data to train on
    returns the numbers of TT, TF, FT, FF (assessed:correct)
    '''

    data = transpose(rawData)
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