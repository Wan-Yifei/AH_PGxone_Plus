#!/usr/bin/python
#-*- coding: utf-8 -*-

class Gene:
    def __init__(self, sample_ID, gene_name, Drug_action, amplicon_name, Range):
        self.ID = sample_ID 
        self.gene = gene_name 
        self.ICD = self.get_ICD(Drug_action) 
        self.panel, self.low_amp = self.get_amp(amplicon_name, Range) 

    def get_ICD(self, Drug_action):
        ICDs = next(line.strip().split('\t')[7] for line in Drug_action if line.strip().split('\t')[5] == self.gene)
        return ICDs

    def get_amp(self, amplicon_name, Range):

    ## Range: the file records loci of each amplicon
    ## location of correspoding amplicon with low count
        low_amp =  [[loc.split('\t')[0]] + loc.split('\t')[1].split('..') for name in amplicon_name for loc in Range if loc.split('\t')[2] == name]
    ## All amplicons of CYP super-family with enough count
        amp_panel = [[loc.split('\t')[0]] + loc.split('\t')[1].split('..') for loc in Range if 'CYP' in loc and [loc.split('\t')[0]] + loc.split('\t')[1].split('..') not in low_amp]
        return amp_panel, low_amp

