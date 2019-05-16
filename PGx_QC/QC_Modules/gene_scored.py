#!/usr/bin/python
#-*- coding: utf-8 -*-

## To do: the get_ICD function cannot get complete ICD list of gene, need to be fixed.

import sys
sys.path.append('/home/yifei.wan/PGx_QC/QC_Modules/gene.py')
from gene import Gene
import numpy as np
import itertools as ir
import re

class GeneScored(Gene):
    def __init__(self, sample_ID, sample_ICD, gene_name, Output_geno, amplicon_name, Active_score, Drug_action, Low_coverage, Range, Gene_KB):
        Gene.__init__(self, sample_ID, sample_ICD, gene_name, Drug_action, amplicon_name, Range)
        if self.ICD_relevant:
            self.genotype = self.get_geno(Output_geno) 
            self.phenotype, self.score_allele = self.get_pheno(Active_score) 
            self.potential_allele = self.get_pot_allele(Gene_KB) 
            self.potential_phenotype = self.get_pot_pheno(Active_score)
        else:
            self.genotype = None
            self.phenotype, self.score_allele = None, None 
            self.potential_allele = None 
            self.potential_phenotype = True 
        #self.Check_list()

    def Check_list(self):
        print 'sample ICD: %s'%self.sample_ICD
        print 'ICD of %s: %s'%(self.gene, self.ICD)
        print 'Original gneotype: %s'%self.genotype
        print 'Original phenotype: %s'%self.phenotype
        print 'All potential alleles: %s'%self.potential_allele
        print 'Potential phenotype check pass: %s'%self.potential_phenotype

    def get_geno(self, Output_geno):
        index = next(line.strip().split('\t').index(self.gene) for line in Output_geno if self.gene in line)
        genotype = next(line.strip().split('\t')[index] for line in Output_geno if self.ID in line)
        return genotype

    def get_pheno(self, Active_score):
        score_string = next(line.strip().split('\t')[3] for line in Active_score if self.gene in line)
        score_threshold = next(line.strip().split('\t')[4] for line in Active_score if self.gene in line)
        score_allele = {item.split('\t')[1] : float(item.split('\t')[2]) for item in Active_score if self.gene in item}
        alleles = self.genotype.split('/')
        phenotype = self.parse_pheno(alleles, score_allele, score_threshold)
        return phenotype, score_allele

    def parse_pheno(self, alleles, score_allele, score_threshold):
        alleles_score = sum([score_allele[allele.replace('xN', '')]*2 if 'xN' in allele else score_allele[allele] for allele in alleles])
        score_level, score_bin = self.parse_score(score_threshold) ## name of action level and bins of score
        phenotype = score_level[np.digitize(alleles_score, score_bin)] ## phenotype of input genotype
        return phenotype

    def parse_score(self, score_threshold):
        #print score_threshold
        score_level = np.array([item.split(':')[0] for item in score_threshold.split(';')]) ## extract medications action level
        score_bin = [float(num) for num in set(re.findall(r'\d.\d+', score_threshold))] ## extract bin of each level
        score_bin.sort()
        ## parse score standard as close range
        return score_level, score_bin

    def get_pot_allele(self, Gene_KB):
        poten_alleles = []
        for low_range in self.low_amp:
            for allele in Gene_KB:
                if allele.split('\t')[0] == self.gene:
                    if allele.split('\t')[4].replace('chr', '') == low_range[0]:
                        if (all([int(pos) not in range(int(high_range[1]) + 5, int(high_range[2]) - 4) 
                        for pos in allele.split('\t')[5].split(', ') for high_range in self.panel])):
                            poten_alleles.append(allele.split('\t')[1].strip())
        poten_alleles = poten_alleles + list(set(self.genotype.split('/'))) ## add original allele to the potential list
        poten_geno = [list(allele) for allele in ir.combinations_with_replacement(poten_alleles, 2)]
        return poten_geno

    def get_pot_pheno(self, Active_score):
        #score_string = next(line.strip().split('\t')[4] for line in Active_score if self.gene in line)
        score_threshold = next(line.strip().split('\t')[4] for line in Active_score if self.gene in line)
        phenotypes = [self.parse_pheno(pot_allele, self.score_allele, score_threshold) for pot_allele in self.potential_allele]
        phen_flag = all([pheno == self.phenotype for pheno in phenotypes]) ## if False, amplicon failed.
        return phen_flag

