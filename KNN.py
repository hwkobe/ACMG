# -*- coding: utf-8 -*-
"""
Created on Mon Sep 26 16:53:51 2016
@author: hwkobe
"""
from numpy import *
import operator
import xlrd,xlwt,random


def KNN_Classifier(inX, dataset, labels, k):
    DataSetSize = dataset.shape[0]
    DiffMat = tile(inX, (DataSetSize,1)) - dataset
    sqDiffMat = DiffMat**2
    sqDistances = sqDiffMat.sum(axis=1)
    distances = sqDistances**0.5
    SortedDistances = distances.argsort()
    
    ClassCount = {}
    for i in range(k):
        voteILabel = labels[SortedDistances[i]]
        ClassCount[voteILabel] = ClassCount.get(voteILabel,0) + 1
    SortedClassCount = sorted(ClassCount.iteritems(), key=operator.itemgetter(1),reverse = True)
    
    return SortedClassCount
    
dataset = array([[1.0,1.0],[1.0,1.1],[0.0,0.0],[0.0,0.1]])
labels = ['A','A','B','B']

inX = [1.3,1.2]
a = open('pred','w')
a.write('1.3')
a.close()
print dataset
print  KNN_Classifier(inX, dataset, labels, 3)