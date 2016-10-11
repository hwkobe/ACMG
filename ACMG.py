# -*- coding: utf-8 -*-
"""
Created on Thu Sep 22 09:15:10 2016
@author: hwkobe
"""
from __future__ import division
from parameters import *
import xlrd,pickle,operator
import DecisionTree

def ChangeFileToList(File):
    List = []
    for ln in file(File,'rt').readlines():
        List.append(ln.strip('\n'))
    return List

def DamagePrediction(mutation):
    FeatVec = []
    for label in D_Labels:
        FeatVec.append(mutation[label])
    D_Tree = pickle.load(open(D_TreeFile))
    Pred = DecisionTree.Classify(D_Tree,D_Labels,FeatVec)
    return Pred
        
def ConservePrediction(mutation):
    FeatVec = []
    for label in C_Labels:
        FeatVec.append(mutation[label])
    C_Tree = pickle.load(open(C_TreeFile)) 
    Pred = DecisionTree.Classify(C_Tree,C_Labels,FeatVec)
    return Pred        

def IsPVS1(mutation):
    pvs1 = 0
    NullMutation = ['nonsynonymous SNV','stopgain','stoploss']
    IndelMutation = ['frameshift insertion','frameshift deletion']
    
    if mutation['ExonicFunc.refGene'] in NullMutation or mutation['Func.refGene'] == 'splicing':
        if DamagePrediction(mutation) == 'yes' or ConservePrediction(mutation) == 'yes': pvs1 = 1
    
    if mutation['ExonicFunc.refGene'] in IndelMutation: 
        if mutation['MutationTaster_indel_pred'] == 'D': pvs1 = 1
    return pvs1
    
def IsPS1_4(mutation):
    ps = 0
    NullMutation = ['nonsynonymous SNV','stopgain','stoploss']
    if mutation['ExonicFunc.refGene'] in NullMutation or mutation['Func.refGene'] == 'splicing':
        if  mutation['HGMD_Phenotype'] not in ['','.']: ps += 1    
        if 'Pathogenic' in mutation['CLINSIG']: ps += 1
    return ps
    
def IsPM1_6(mutation):
    pm = 0
    if mutation['1000g2015aug_all'] in ['','.'] or mutation['1000g2015aug_all'] < 0.05: pm += 1
    if mutation['ExonicFunc.refGene'] in ['frameshift insertion','frameshift deletion','stoploss']:pm += 1
    if mutation['Func.refGene'] == 'splicing': pm += 1
    return pm
    
def IsPP1_5(mutation):
    pp = 0
    if DamagePrediction(mutation) == 'yes': pp += 1
    if ConservePrediction(mutation) == 'yes': pp += 1
    if mutation['OMIN_disease'] not in ['.','---'] or mutation['HPO'] not in ['.','---']: pp += 1
    return pp
    
def IsBA1(mutation):
    ba1 = 0
    if mutation['1000g2015aug_all'] > 0.05 and mutation['1000g2015aug_all'] not in ['','.']: ba1 = 1    
    return ba1
    
def IsBS1_4(mutation):
    bs = 0
    if 'Benign' in mutation['CLINSIG']: bs += 1
    return bs

def IsBP1_7(mutation):
    bp = 0
    if DamagePrediction(mutation) == 'no': bp += 1
    if mutation['ExonicFunc.refGene'] == 'synonymous SNV' and 'splicing' not in mutation['Func.refGene']: bp += 1 
    return bp   
    
def Prediction(mutation):
    Prediction = 'uncertain'; Prediction1 = 'uncertain'; Prediction2 = 'uncertain'
    pvs1 = IsPVS1(mutation); ps = IsPS1_4(mutation)
    pm = IsPM1_6(mutation); pp = IsPP1_5(mutation)
    ba1 = IsBA1(mutation); bs = IsBS1_4(mutation); bp = IsBP1_7(mutation)
    print [pvs1,ps,pm,pp],[ba1,bs,bp]
    Score = pvs1*5 + ps*4 + pm*3 + pp*2
    if pvs1 == 1:
        if ps >= 1 : Prediction1 = 'Pathogenic'
        elif pm >= 2: Prediction1 = 'Pathogenic'
        elif pm == 1 and pp == 1: Prediction1 = 'Pathogenic'
        elif pp >= 2 :Prediction1 = 'Pathogenic'
        elif pm == 1: Prediction1 = 'Likely Pathogenic'
    
    elif ps >= 2:  Prediction1 = 'Pathogenic' 
    elif ps ==1:
        if pm >= 3 : Prediction1 = 'Pathogenic'
        elif pm >= 2 and pp >= 2: Prediction1 = 'Pathogenic'
        elif pm >= 1 and pp >= 4: Prediction1 = 'Pathogenic'
        elif pm ==1 : Prediction1 = 'Likely Pathogenic'
        elif pp >= 2: Prediction1 = 'Likely Pathogenic'
        
    elif pm >= 3: Prediction1 = 'Likely Pathogenic'
    elif pm ==2 and pp >= 2 : Prediction1 = 'Likely Pathogenic'
    elif pm ==1 and pp >= 4:  Prediction1 = 'Likely Pathogenic'
    
    if ba1 == 1: Prediction2 = 'Benign'
    elif bs >= 2: Prediction2 = 'Benign'
    elif bs == 1 and bp == 1: Prediction2 = 'Likely Benign'
    elif bp >= 2: Prediction2 = 'Likely Benign'
    
    if Prediction1 == 'uncertain' and Prediction2 != 'uncertain':  
        Prediction =  Prediction2
    elif Prediction2 == 'uncertain' and Prediction1 != 'uncertain': 
        Prediction =  Prediction1
    elif Prediction2 != 'uncertain' and Prediction1 != 'uncertain':
        Prediction = 'uncertain'
    elif Prediction2 == 'uncertain' and Prediction1 == 'uncertain':
        Prediction = 'uncertain'
    #print  Prediction  
    return (Prediction,Score)
    
    
    
if __name__ == '__main__':
    
    #f = open('pred','w')
   
    ExcelFile = xlrd.open_workbook('first_batch.xls')
    a = 12
    sheet = ExcelFile.sheet_by_index(0)
    items = sheet.row_values(0)
    names1 = sheet.col_values(a)
    names2 = sheet.col_values(a+1)
    names3 = sheet.col_values(a+3)
    names4 = sheet.col_values(a+4)
    print sheet.nrows
    
    Dict = {}
    for i in range(1,sheet.nrows):
        
        mut_name = names1[i]+'_'+str(names2[i])+'_'+names3[i]+'>'+names4[i]
        dic = {}
        for j in range(0,sheet.ncols):
            dic[items[j]] = sheet.cell(i,j).value
        Dict[mut_name] = dic
    
    pred = [] 
    rank = {}
    #print sorted(Dict.keys())
    
    for mutation in sorted(Dict.keys()):
        #if Dict[mutation]['FILTER'] == 'PASS' and Dict[mutation]['Coverage'] > 30:
        #if Dict[mutation]['ExonicFunc.refGene'] not in ['.','']:
           if Prediction(Dict[mutation])[0] == 'uncertain':
              print mutation
            
           pred.append(Prediction(Dict[mutation])[0])
        #f.write(Prediction(Dict[mutation])+'\n')
    
    print pred.count('uncertain'),pred.count('Pathogenic'),pred.count('Likely Pathogenic')
    print pred.count('Benign'),pred.count('Likely Benign')
    #print rank['chr9_135202993.0_G>A']
    #print sorted(rank.iteritems(), key=operator.itemgetter(1),reverse = True)
    #f.close()
   
    
 
    
    
    
    
    
    
    
    
    
    
    
    
