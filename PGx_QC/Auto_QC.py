# @author: Yifei Wan

# =======================================================================================
# 04/09/2019    Basic version 0.0.1
# Summary:
#
# Automatically process QC for each run of PGxOne_V3.
# =======================================================================================

#To do: Line60 needs a list comprehension to handle self.potential_Allele which includes nested list.

import numpy as np
import itertools as ir
import re

class Gene:
    ## Gene has low coverage amplicon(s).
    def __init__(self, sample_ID, gene_name, Output_geno, amplicon_name, Active_score, Drug_action, Low_coverage, Range, Gene_KB):
        self.ID = sample_ID
        self.gene = gene_name
        self.ICD = self.get_ICD(Drug_action)
        self.genotype = self.get_geno(Output_geno)
        self.phenotype, self.score_allele = self.get_pheno(Active_score)
        self.panel, self.low_amp = self.get_amp(amplicon_name, Range) ## panel: location of amplicons with enough count; low_amp: location of amplicons with low count
        self.potential_Allele = self.get_pot_allele(Gene_KB)
        self.potential_Phenotype = self.get_pot_pheno(Active_score) ## Logical flag of specified gene: whether does activity change?
        self.show()

    def show(self):
        print 'ID: %s'%self.ID
        print 'Gene: %s'%self.gene
        print 'ICDs: %s'%self.ICD
        print 'Genotype: %s'%self.genotype
        print 'Phenotype: %s'%self.phenotype
        print 'Low_coverage_amplicon: %s'%self.low_amp
        print 'Potential_alleles: %s'%self.potential_Allele
        print 'Potential_Phenotype: %s'%self.potential_Phenotype
        #print 'Panel: %s'%self.panel
        print 'Low_location: %s'%self.low_amp

    def get_ICD(self, Drug_action):
        ICDs = next(line.strip().split('\t')[7] for line in Drug_action if line.strip().split('\t')[5] == self.gene)
        return ICDs

    def get_geno(self, Output_geno):
        index = next(line.strip().split('\t').index(self.gene) for line in Output_geno if self.gene in line)
        genotype = next(line.strip().split('\t')[index] for line in Output_geno if self.ID in line)
        return genotype

    def get_pheno(self, Active_score):
        score_string = next(line.strip().split('\t')[3] for line in Active_score if self.gene in line)
        score_threshold = next(line.strip().split('\t')[4] for line in Active_score if self.gene in line)
        score_allele = {item.split('\t')[1] : float(item.split('\t')[2]) for item in Active_score if self.gene in item} ## extract socre for each allele
        alleles = self.genotype.split('/')
        phenotype = self.parse_pheno(alleles, score_allele, score_threshold)
        return phenotype, score_allele

    def parse_pheno(self, alleles, score_allele, score_threshold):
        alleles_score = sum([score_allele[allele.replace('xN', '')]*2 if 'xN' in allele else score_allele[allele] for allele in alleles]) ## score of input genotype
        score_level, score_bin = self.parse_score(score_threshold) ## name of action level and bins of score
        #print alleles_score
        #print score_bin
        phenotype = score_level[np.digitize(alleles_score, score_bin)] ## phenotype of input genotype
        return phenotype

    def parse_score(self, score_threshold):
        #print score_threshold
        score_level = np.array([item.split(':')[0] for item in score_threshold.split(';')]) ## extract medications action level
        score_bin = [float(num) for num in set(re.findall(r'\d.\d+', score_threshold))] ## extract bin of each level
        score_bin.sort()
        ## parse score standard as close range
        return score_level, score_bin

    def get_amp(self, amplicon_name, Range):
    ## Range: the file records loci of each amplicon
    ## location of correspoding amplicon with low count
        low_amp =  [[loc.split('\t')[0]] + loc.split('\t')[1].split('..') for name in amplicon_name for loc in Range if loc.split('\t')[2] == name]
    ## All amplicons of CYP super-family with enough count
        amp_panel = [[loc.split('\t')[0]] + loc.split('\t')[1].split('..') for loc in Range if 'CYP' in loc and [loc.split('\t')[0]] + loc.split('\t')[1].split('..') not in low_amp]
        return amp_panel, low_amp

    def get_pot_allele(self, Gene_KB):
        poten_alleles = []
        for low_range in self.low_amp:
            for allele in Gene_KB:
                if allele.split('\t')[0] == self.gene: 
                    if allele.split('\t')[4].replace('chr', '') == low_range[0]:
                        if all([int(pos) not in range(int(high_range[1]) + 5, int(high_range[2]) - 4) for pos in allele.split('\t')[5].split(', ') for high_range in self.panel]):
                            poten_alleles.append(allele.split('\t')[1].strip())
        poten_alleles = poten_alleles + list(set(self.genotype.split('/'))) ## add original allele to the potential list
        poten_geno = [list(allele) for allele in ir.combinations_with_replacement(poten_alleles, 2)]
        return poten_geno

    def get_pot_pheno(self, Active_score):
        #score_string = next(line.strip().split('\t')[4] for line in Active_score if self.gene in line)
        score_threshold = next(line.strip().split('\t')[4] for line in Active_score if self.gene in line)
        phenotypes = [self.parse_pheno(pot_allele, self.score_allele, score_threshold) for pot_allele in self.potential_Allele]
        print 'Phenotype %s'%phenotypes 
        phen_flag = all([pheno == self.phenotype for pheno in phenotypes]) ## if False, amplicon failed.
        return phen_flag
