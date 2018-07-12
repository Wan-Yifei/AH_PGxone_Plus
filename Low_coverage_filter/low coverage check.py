# -*- coding: utf-8 -*-
"""
Created on Wed Jul 11 09:32:03 2018
@author: yifei.wan

This script is utilized to fliter low coverage genes.
a. Identity complete failed sample(s);
b. Identity low coverage (<10) gene(s) for non-complete sample(s).
"""
import sys
import csv

# Accept argument(pathway) from shell
def pathway():
    if (len(sys.argv) < 1):
        raise Exception('Please input pathway of sample_QC_low_coverage.txt')
    elif (len(sys.argv) > 1):
        raise Exception('Please only input pathway of sample_QC_coverage.txt')
    else:
        print(sys.argv)
        
if __name__ == '__main__':
    pathway()
    