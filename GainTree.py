# -*- coding: utf-8 -*-
"""
Created on Sun Sep 18 09:49:07 2016
@author: hwkobe
"""
from __future__ import division
import xlrd,xlwt,random,pickle
import DecisionTree
import TreePlotter

def GetNegativeFeatureVector(xls,labels):
    
    ExcelFile = xlrd.open_workbook(xls)
    sheet = ExcelFile.sheet_by_index(0)

    items = sheet.row_values(0)
    names1 = sheet.col_values(0)
    names2 = sheet.col_values(1)
    names3 = sheet.col_values(3)
    names4 = sheet.col_values(4)
    Dict = {}
    for i in range(1,sheet.nrows):
        mut_name = names1[i]+'_'+str(names2[i])+'_'+names3[i]+'>'+names4[i]
        dic ={}
        for j in range(0,sheet.ncols):
            dic[items[j]] = sheet.cell(i,j).value
        
        if  dic['1000g2015aug_all'] > 0.80:
               Dict[mut_name] = dic
    #print len(Dict)
    Feature = []; TestVec = []
    for x in random.sample(range(len(Dict)),150):
        mut = Dict.keys()[x]
        feature = []
        for label in labels:
            v = Dict[mut][label]
            feature.append(v)
        if '' not in feature:
            feature.append('no')
            Feature.append(feature)
    for y in random.sample(range(int(len(Dict)/2),len(Dict)),300):
        mut = Dict.keys()[y]
        vec = []
        for label in labels:
            v = Dict[mut][label]
            vec.append(v)
        if '' not in vec:
            TestVec.append(vec)
    #print len(Feature)
    return Feature,TestVec
    
    
def GetPositiveFeatureVector(xls,labels,start):
    ExcelFile = xlrd.open_workbook(xls)
    sheet = ExcelFile.sheet_by_index(0)
    items = sheet.row_values(0)
    names1 = sheet.col_values(start)
    names2 = sheet.col_values(start+1)
    names3 = sheet.col_values(start+3)
    names4 = sheet.col_values(start+4)
    
    Dict = {}
    for i in range(1,sheet.nrows):
        mut_name = names1[i]+'_'+str(names2[i])+'_'+names3[i]+'>'+names4[i]
        dic = {}
        for j in range(0,sheet.ncols):
            dic[items[j]] = sheet.cell(i,j).value
        Dict[mut_name] = dic
    #print Dict[Dict.keys()[0]]['SIFT_pred']    
    Feature = [] 
    for mut in Dict.keys():
        feature = []
        for label in labels:
            v = Dict[mut][label]
            feature.append(v)
        if '' not in feature and start == 12:
            feature.append('yes')
            Feature.append(feature)
        if '' not in feature and start == 4:
            Feature.append(feature)
    return Feature
    
##########C: Conservation of protein;  D: Damage of protein##################   
C_Labels = ['fathmm-MKL_coding_pred','MetaLR_pred','MetaSVM_pred']
C_FeatLabels = ['fathmm-MKL_coding_pred','MetaLR_pred','MetaSVM_pred']
D_Labels = ['Polyphen2_HDIV_pred','MutationTaster_pred','FATHMM_pred'] 
D_FeatLabels = ['Polyphen2_HDIV_pred','MutationTaster_pred','FATHMM_pred'] 

C_Positive = GetPositiveFeatureVector('training.xls',C_Labels,12)
D_Positive = GetPositiveFeatureVector('training.xls',D_Labels,12)
C_Positive_t = GetPositiveFeatureVector('testing.xls',C_Labels,4)
D_Positive_t = GetPositiveFeatureVector('testing.xls',D_Labels,4)
C_Negative,C_TestVec = GetNegativeFeatureVector('10128.annotation.xls',C_Labels)
D_Negative,D_TestVec = GetNegativeFeatureVector('10128.annotation.xls',D_Labels)
#############################################################################
print len(D_Positive)
C_dataset = C_Negative + C_Positive
D_dataset = D_Negative + D_Positive
#print dataset
C_Tree = DecisionTree.CreatTree(C_dataset,C_Labels)
D_Tree = DecisionTree.CreatTree(D_dataset,D_Labels)

#TreePlotter.CreatPlot(D_Tree)
#TreePlotter.CreatPlot(C_Tree)


C_TreeFile = open('C_Tree','w')
D_TreeFile = open('D_Tree','w')
pickle.dump(C_Tree,C_TreeFile)
pickle.dump(D_Tree,D_TreeFile)
C_TreeFile.close();D_TreeFile.close()


ClassList = [] 
#print Positive[50:]  # [50:]: #Positive:       #TestVec:
for vec in C_TestVec: 
    vec = vec[0:3]
    ClassList.append(DecisionTree.Classify(C_Tree,C_FeatLabels,vec))
    
print len(ClassList),ClassList.count('no')/len(ClassList)
