# tools for combining tests via a decision tree
from sklearn import tree
import numpy as np

def buildTree(trueResults, testResults, trainingSize):
    '''
    trueResults = a list of correct assessments for a collection of datasets
    testResults = a list of lists; first index counts QC tests, second index counts datasets.
    trainingSize = number of datasets to include in the training 
    '''

    trainingResults = np.array(testResults).transpose()[0:trainingSize]
    trainingTruth = np.array(trueResults)[0:trainingSize]

    clf = tree.DecisionTreeClassifier()
    clf = clf.fit(trainingResults, trainingTruth)

    return clf

def reportPrediction(tree, trueResults, testResults, skipN=0):
    '''
    tree = decision tree built by buildTree; other vars as per that function.
    skipN = number of datasets to skip in analysis (typically set equal to trainingSize)
    '''

    testingResults = np.array(testResults).transpose()[skipN:]
    testingTruth = np.array(trueResults)[skipN:]

    tt = 0
    tf = 0
    ft = 0
    ff = 0

    for i in range(len(testingResults)):
      prediction = tree.predict(testingResults[i])

      if prediction[0] and testingTruth[i]:
        tt += 1
      elif not prediction[0] and not testingTruth[i]:
        ff += 1
      elif prediction[0] and not testingTruth[i]:
        tf += 1
      elif not prediction[0] and testingTruth[i]:
        ft += 1    

    print 'Correct flags:', tt
    print 'Correct no-flags:', ff
    print 'False positives:', tf
    print 'False negatives', ft