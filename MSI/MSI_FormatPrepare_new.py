# -*- coding: utf-8 -*-
"""
Created on Fri Nov  9 16:29:21 2018

@author: yifei.wan
"""

# -*- coding: utf-8 -*-
"""
Created on Wed Oct  3 12:26:09 2018

@author: yifei.wan

Prepare MSI raw count for statistical analysis.
"""
import glob
import os

os.chdir('V:/Cai-MSI-development/healthy-controls/20181108-bfUID')
files = glob.glob('*array.txt')

# 1. Input raw data from pipeline
def Change_Format(line):
    newline = []
    newline = line.replace(' [', ' ').replace(']', '').replace(', ', ' ').split(' ')
    return newline

# 2. Output result
def Output_count(count_reformed):
    output = open(output_path,'w',encoding='utf-8')
    for row in count_reformed:
        output.write('{}_{}\t{}'.format(row[0],row[1],'\t'.join(row[2:])))
    output.close()    

for file in files:
    with open(file) as raw:
        print(file)
        count_raw = raw.readlines()
        count_reformed = [Change_Format(line) for line in count_raw]
        count_sorted = sorted(count_reformed, key = lambda line: len(line[1:]), reverse = True)
        output_path = 'C:/Users/yifei.wan/Desktop/MSI development/bfUID/{}'.format(file)
        Output_count(count_sorted)