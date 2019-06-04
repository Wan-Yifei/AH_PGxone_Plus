#!/usr/bin/python
#-*- coding: utf-8 -*-

import sys
sys.path.append('/home/yifei.wan/PGx_QC/QC_Modules/sample.py')
from sample import Sample

class Control(Sample):

    genes = (['ABCB1', 'ACE', 'ADRA2A', 'AGTR1', 'ANKK1', 'APOE', 'ATM', 'CDA',
    'CES1', 'CNR1', 'COMT', 'CYP1A2', 'CYP2B6', 'CYP2C19', 'CYP2C8', 'CYP2C9', 
    'CYP2D6', 'CYP3A4', 'CYP3A5', 'CYP4F2', 'DPYD', 'DRD1', 'DRD2', 'ERCC1', 
    'F2', 'F5', 'FAAH', 'G6PD', 'GRIK4', 'GSTP1', 'HLA-B', 'HTR1A', 'HTR2A', 
    'HTR2C', 'IFNL3', 'ITPA', 'KIF6', 'MTHFR', 'NAT2', 'NOS1AP', 'NQO1', 
    'OPRM1', 'SCN2A', 'SLCO1B1', 'TPMT', 'UGT1A1', 'UGT2B15', 'VKORC1', 'XRCC1'])
    
    NA17244_standard_genotype = (['c.3435T>C/c.3435T>C/c.2677T>G/c.2677T>G', 
    'WT/WT', 'WT/c.-1252G>C', 'WT/c.*86A>C', 'WT/WT', 'WT/WT', 'WT/c.175-5285G>T',
    'WT/c.-451C>T', 'WT/c.428G>A', 'WT/WT', 'WT/c.472G>A', '*1A/*1F', 'A785G/G516T', 
    '*1/*1', '*1/*1', '*1/*1', '*2xN/*4', '*1A/*1A', '*3A/*3A', '*1/*1', '*1/*9A',
    'WT/c.-48G>A', 'WT/WT', 'WT/WT', 'WT/WT', 'WT/WT', 'WT/WT', 'WT/WT', 
    'c.83-10039T>C/c.83-10039T>C', 'WT/c.313A>G', 'WT/WT', 'WT/WT', 'WT/c.614-2211T>C', 
    'c.551-3008C>G/c.551-3008C>G', 'WT/WT', 'WT/WT', 'WT/c.2155T>C', 'WT/C677T',
    '*5/*6/*12/*13', 'WT/c.106-38510G>T', 'WT/c.559C>T', 'WT/c.118A>G', 'WT/WT',
    '*1/*1', '*1/*1', '*1/*1', '*1/*2', '-1639G>A/-1639G>A', 'WT/c.1196A>G'])

    NA17281_standard_genotype = (['WT/c.2677T>G', 'WT/WT', 'WT/c.-1252G>C', 
    'WT/c.*86A>C', 'WT/A1', 'WT/WT', 'WT/WT', 'WT/c.-451C>T', 'WT/WT', 'WT/c.*3475A>G',
    'WT/c.472G>A', '*1F/*1F', 'A785G/G516T', '*1/*17', '*1/*1', '*1/*1', '*5/*9', 
    '*1A/*1A', '*3A/*3A', '*1/*1', '*5/*5/*9A', 'WT/c.-48G>A', 'WT/WT', 'WT/WT', 
    'WT/WT', 'WT/WT', 'WT/WT', 'WT/WT', 'WT/c.83-10039T>C', 'WT/WT', 'WT/WT', 
    'WT/c.-1019G>C', 'c.614-2211T>C/c.614-2211T>C', 'c.551-3008C>G/c.551-3008C>G',
    'WT/WT', 'WT/c.124+21A>C', 'c.2155T>C/c.2155T>C', 'C677T/A1298C', '*5/*6/*13',
    'c.106-38510G>T/c.178-20044C>T/c.178-13122C>T', 'WT/WT', 'WT/WT', 'WT/WT',
    '*1/*5', '*1/*1', '*1/*28', '*1/*2', 'WT/-1639G>A', 'c.1196A>G/c.1196A>G'])

    def __init__(self, ID, Output_geno, Code_drug, Active_score, Drug_action, Low_coverage, Range, Gene_KB, low_coverage_flag):
        self.ID = ID
        self.whole_genotype = self.get_whole_genotype(Output_geno)
        self.standard_pass, self.cyp2d6_pass = self.standard_check()
        if low_coverage_flag:
            Sample.__init__(self, ID, Output_geno, Code_drug, Active_score, Drug_action, Low_coverage, Range, Gene_KB) 

    def get_whole_genotype(self, Output_geno):
        genotypes = next(line.strip().split('\t') for line in Output_geno if self.ID in line)
        return genotypes

    def standard_check(self):
        if 'NA17244' in self.ID:
            mismatch_count = len([g_control for g_standard, g_control in 
            zip(self.NA17244_standard_genotype, self.whole_genotype) if g_standard != g_control])
            ## check the mismatch of CYP2D6
            if self.whole_genotype[16] != '2xN/*4' or self.whole_genotype[16] != '*4/2xN': 
                print self.whole_genotype[16]
                mismatch_CYP2D6 = False
            else:
                mismatch_CYP2D6 = True
        if 'NA17281' in self.ID:
            mismatch_count = len([g_control for g_standard, g_control in
            zip(self.NA17281_standard_genotype, self.whole_genotype) if g_standard != g_control])
            ## check the mismatch of CYP2D6
            if self.whole_genotype[16] != '*5/*9':
                mismatch_CYP2D6 = False
            else:
                mismatch_CYP2D6 = True
        if mismatch_count > 3:
            control_QC = True ## control passes QC
        else:
            control_QC = False ## control failed
        return control_QC, mismatch_CYP2D6

