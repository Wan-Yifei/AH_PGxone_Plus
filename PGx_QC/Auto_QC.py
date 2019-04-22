# @author: Yifei Wan

# =======================================================================================
# 04/09/2019	Basic version 0.0.1
# Summary:
#
# Automatically process QC for each run of PGxOne_V3.
# =======================================================================================

import numpy as np
import itertools as ir
import re

Class Gene():
	## Gene has low coverage amplicon(s).
	def __init__(self, sample_ID, gene_name, amplicon_name, Drug_action, Low_coverage, Range):
		self.ID = sample_ID
		self.gene = gene_name
		self.ICD = self.get_ICD()
		self.genotype = self.get_geno()
		self.phenotype = self.get_pheno()
		self.panel, self.low_amp = self.get_amp()
		self.potential_Allele = self.get_pot_allel()
		self.potential_Phenotype = self.get_pot_pheno() ## Logical flag of specified gene: whether does activity change?

	def get_ICD(self, Drug_action):
		ICDs = next([line.strip().split('\t')[7] for line in Drug_action if line.strip().split('\t')[5] == self.gene])
		return ICDs

	def get_geno(self, Output_geno):
		index = next([line.strip().split('\t').index(self.gene) for line in Output_geno if self.gene in line])
		genotype = next([line.strip().split('\t')[index] for line in Output_geno if self.ID in line])
		return genotype

	def get_pheno(self, Active_score):
		score_string = next([line.strip().split('\t')[4] for line in Active_score if self.gene in line])
		score_threshold = next([line.strip.split('\t')[5] for line in Active_score if self.gene in line])
		alleles = self.genotype.split('/')
		phenotype = self.parse_pheno(alleles, score_string, score_threshold)
		return phenotype

	def parse_pheno(self, alleles, score_string, score_threshold):
		score_allele = {item.split(':')[0] : item.split(':')[1] for item in score_string.split(';')} ## extract socre for each allele
		alleles_score = sum([score_allele[allele.replace('xN', '')]*2 if 'xN' in allel else score_allele[allele] for allele in alleles]) ## score of input genotype
		score_level, score_bin = self.parse_score(score_threshold) ## name of action level and bins of score
		phenotype = score_level[np.digitize(alleles_score, score_bin)] ## phenotype of input genotype
		return phenotype

	def parse_score(self, score_threshold):
		score_level = np.array([item.split(':')[0] for item in score_threshold.split(';')]) ## extract medications action level
		score_bin = [float(num) for num in set(re.findall(r'\d.\d+', score_threshold))].sort() ## extract bin of each level
		## parse score standard as close range
		return score_level, score_bin

	def get_amp(self, amplicon_name, Range)
	## Range: the file records loci each amplicon
		#low_amp_names = [amp.split('\t')[2] for amp in Low_coverage if int(amp.split('\t')[3]) < 6 and self.gene in amp]  
	## location of correspoding amplicon with low count
		low_amp =  [[loc.split('\t')[0]] + loc.split('\t')[1].split('..') for name in amplicon_name for loc in Range if loc.split('\t')[2] == name]
	## All amplicons of CYP super-family with enough count
		amp_panel = [[loc.split('\t')[0]] + loc.split('\t')[1].split('..') for loc in Range if 'CYP' in loc and loc.split('\t')[0]] + loc.split('\t')[1].split('..') not in low_amp]
		return amp_panel, low_amp

	def get_pot_allele(self, Gene_KB):
		poten_alleles = [allele[2] for allele in Gene_KB for low_range in self.low_amp for high_range in self.panel if allele.split('\t')[0] == self.gene and allele.split('\t')[4].replace('chr', '') == low_range[0] and allele.split('\t')[5] in range(low_range[1] + 5, low_range[2] - 4) and allele.split('\t')[5] not in range(high_range[1] + 5, high_range[2] -4)]
		poten_geno = [list(allele) for allele in ir.combinations_with_replacement(poten_alleles, 2)]
		return poten_geno

	def get_pot_pheno(self, Active_score):
		score_string = next([line.strip().split('\t')[4] for line in Active_score if self.gene in line])
		score_threshold = next([line.strip.split('\t')[5] for line in Active_score if self.gene in line])
		phenotypes = [self.parse_pheno(alleles, score_string, score_threshold) for alleles in self.potential_Phenotype]
		phen_flag = all([pheno == self.phenotype for pheno in phenotypes])
		return phen_flag
