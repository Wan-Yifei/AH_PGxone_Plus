#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul 19 21:25:34 2018

@author: yifei.wan
"""

import sys
import getopt

def pathways(args):
    '''
    This is a entry function. It is utilized to accept paths of input file 
    and out file from shell respectively. It also provides options for 
    linux commands.
    '''
    inputfile = ''
    outputfile = ''
    
    try:
        opts, arg = getopt.getopt(args, 'hi:o:')
    except getopt.GetoptError:
        print('Usage: -i <path of input> -o <path of output>')
        sys.exit(2)
        
    for opt, arg in opts:
        if opt == '-h':
            print('Usage: PGxOneV3_Drug_extract.py -i <path of input> -o <path of output>')
            sys.exit(0)
        elif opt == '-i':
            inputfile = arg
        elif opt == '-o':
            outputfile = arg

    print('\ninput: {:<30}'.format(inputfile))
    print('output: {:<30}\n'.format(outputfile))
            
    return inputfile, outputfile


    
    
pathways(sys.argv[1:])            
            
    