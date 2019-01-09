# -*- coding: utf-8 -*-
"""
Created on Wed Jan  9 12:18:57 2019

@author: yifei.wan
"""

import glob
import collections
import matplotlib.pyplot as plt

files = glob.glob('C:/Users/yifei.wan/Desktop/Accession_file/*.txt')

def Accession_reader(file):
    with open(file, 'r') as raw:
        lines = raw.readlines()
    sample = {line.strip().split('\t')[0]: line.strip().split('\t')[1].split(', ') for line in lines if 'Sample' not in line }
    return sample

samples = {}    
for file in files:
    samples.update(Accession_reader(file))
    
ICDs = []
for ICD in samples.values():
    ICDs = ICDs + ICD


ICD_top10 = list(zip(*collections.Counter(ICDs).most_common(10)))
#%%
width = 0.5
plt.xticks(rotation=45)
plt.title('Top 10 ICDs')
plt.xlabel('ICD')
plt.ylabel('Proportion %')
fig, ax = plt.bar(ICD_top10[0], [freq/len(samples)*100 for freq in ICD_top10[1]], width, color='g')

#%%
ICD_top50 = collections.Counter(ICDs).most_common(51)

print('ICD\tFrequency %', file = open('ICD_frequency.txt', 'w+'))
for ICD in ICD_top50:
    print('{}\t{}'.format(ICD[0], ICD[1]/len(samples)*100), file = open('ICD_frequency.txt', 'a+'))
    
