# -*- coding: utf-8 -*-
"""
Created on Wed Oct  3 12:26:09 2018

@author: yifei.wan

Prepare MSI raw count for statistical analysis.
"""
import glob
import os

os.chdir('C:/Users/yifei.wan/Desktop/Spike-in/msi')
files = glob.glob('*.txt')

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

for file in files:
    with open(file) as raw:
        count_raw = raw.readlines()
        count_reformed = [Change_Format(line) for line in count_raw]
        count_sorted = sorted(count_reformed, key = lambda line: len(line[2].split(',')), reverse = True)
        output_path = 'C:/Users/yifei.wan/Desktop/MSI_positive/{}'.format(file)
        Output_count(count_sorted)


#'C:/Users/yifei.wan/Desktop/Msi_raw_count/1_percent_HCT16-Large-RD_S39_msi_array99.txt'

