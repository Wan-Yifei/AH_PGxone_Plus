# -*- coding: utf-8 -*-
"""
Created on Wed Oct 24 14:36:03 2018

@author: yifei.wan

Prepare Chinese MSI raw count for statistical analysis.
"""
import glob
import os

os.chdir('C:/Users/yifei.wan/Desktop/MSI development/CHN/raw_count')
files = glob.glob('*msi.txt')

# 1. Input raw data from pipeline
def Change_Format(line):
    newline = []
    newline = [line.split('  ')[0]] + (line.split('  '))[1].split(' [')  
    newline[2] = newline[2].replace(']', '')
    return newline

# 2. Output result
def Output_count(count_reformed):
    output = open(output_path,'w',encoding='utf-8')
    for row in count_reformed:
        output.write('{}_{}\t{}'.format(row[0],row[1].strip(),row[2].replace(', ', '\t')))
    output.close()    

# 3. Excutive functions
for file in files:
    with open(file) as raw:
        count_raw = raw.readlines()
        index = 1
        count_reformed = []
        for line in count_raw:
            if index not in (list(range(1,17,3)) + [17]):
                count_reformed.append(Change_Format(line))
            index = index + 1
  
        count_sorted = sorted(count_reformed, key = lambda line: len(line[2].split(',')), reverse = True)
        output_path = 'C:/Users/yifei.wan/Desktop/MSI development/MSI_CHN/{}'.format(file)
        Output_count(count_sorted)
