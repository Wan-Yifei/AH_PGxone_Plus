#!/usr/bin/python
#-*- coding: utf-8 -*-

class Gene(object):
    def __init__(self, sample_ID, sample_ICD, gene_name, Drug_action, amplicon_name, Range):
        self.ID = sample_ID 
        self.gene = gene_name 
        self.sample_ICD = sample_ICD
        self.ICD = self.get_ICD(Drug_action) 
        self.ICD_relevant = self.ICD_check()
        if self.ICD_relevant:  
            self.panel, self.low_amp = self.get_amp(amplicon_name, Range) 

    def get_ICD(self, Drug_action):
        #ICDs = next(line.strip().split('\t')[7] for line in Drug_action if line.strip().split('\t')[5] == self.gene)
        ICDs = [] 
        for line in Drug_action:
            if 'Anesthesiology' in line.split('\t')[0]: continue
            if line.split('\t')[5] in self.gene:
               ICDs = ICDs + line.split('\t')[7].split(', ')
        ICDs = list(set(ICDs))
        return ICDs

    def get_amp(self, amplicon_name, Range):

    ## Range: the file records loci of each amplicon
    ## location of correspoding amplicon with low count
        low_amp =  [[loc.split('\t')[0]] + loc.split('\t')[1].split('..') for name in amplicon_name for loc in Range if loc.split('\t')[2] == name]
    ## All amplicons of CYP super-family with enough count
        amp_panel = [[loc.split('\t')[0]] + loc.split('\t')[1].split('..') for loc in Range if 'CYP' in loc and [loc.split('\t')[0]] + loc.split('\t')[1].split('..') not in low_amp]
        return amp_panel, low_amp

    def ICD_check(self):
        ICD_relevant = bool(set(self.ICD) & set(self.sample_ICD)) ## True: this gene is relatived to ICDs, False: ignore this gene
        return ICD_relevant
        
