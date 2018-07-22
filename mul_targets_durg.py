#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jul 21 11:10:49 2018

@author: yifei.wan
"""

def read(inputfile):
    '''
    This function is used to read file and restructure data as a list.
    Lines will be splited by '\t' as elements.
    '''
    with open(inputfile, 'r') as durglist:
        ## test code block:
        #testline = durglist.readline()
        
        ## read durg list
        list = [line.rstrip('\n').split('\t') for line in durglist.readlines()[1:] ]
    return list
    

def durgs_targets(durglist):
    '''
    This function extracts durgs with its corresponding genes as a dictionary.
    '''
    durg_dict = {}
    ## Generate a dict: key=durg, value=genes
    for line in durglist:
        durg_dict.setdefault(line[3], []).append('\t' + line[5])
    return durg_dict
 

def mul_targets_durg(durg_dict):
    '''
    This function queries durgs with more than one target gene and produces a 
    list to store result.
    '''
    durg_mult_targets = [[durg, ','.join(genes)] for durg, genes in durg_dict.items() \
                         if len(durg_dict[durg]) > 1]
    durg_mult_targets = [['Durg', '\tGenes']] + durg_mult_targets
    return durg_mult_targets


def write_output(mul_targets_durg, outputfile):
    '''
    This function adds '\n' to the end of each line and output file to indicated path.
    '''
    with open(outputfile, 'w') as output:
        output.writelines(str(line[0]) + str(line[1] + '\n') for line in mul_targets_durg)
        
def main(inputfile, outputfile):
    durglist = read(inputfile)
    durg_dict = durgs_targets(durglist)
    durg_mult_target = mul_targets_durg(durg_dict)
    write_output(durg_mult_target, outputfile)
    
main('/home/ywan/project/AH_PGxone_Plus/PGxOneV3_drug_action.txt', 'test.txt')