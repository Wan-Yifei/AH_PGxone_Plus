# -*- coding: utf-8 -*-
"""
Created on Wed Nov 14 15:48:51 2018

@author: yifei.wan

Automate low coverage QC of PGxOne
"""
#%%
# 1. Import files
import os
import re
import sys
import argparse
import pprint

def ParseArg():

	p = argparse.ArgumentParser(description = 'Automatically check low coverage amplicon')
	p.add_argument("Run_Name",type=str, help="Full name of run folder")
	if len(sys.argv)==1:
		sys.stderr.write(p.print_help())
		sys.exit(0)
	return p.parse_args()


# 2. Create dictionary of samples with low covergae amplicon
#%%
## 2.1 Remove coverage larger than 5

def Low_coverage_filter(QC_record):
	QC_filtered = []
	for line in QC_record:
		newline = line.rstrip().split('\t')
		if newline[0] == 'Sample': continue ## skip the header
		if float(newline[3]) > 29 : continue ## remove coverage larger than 30 counts
		if 'CNV_' in newline[1]:
			gene_name = re.sub(r'CNV_', '', newline[1])
			gene_name = gene_name[0:gene_name.find('_')]
		else:
			gene_name = newline[1][0:newline[1].find('_')]
		newline = [newline[0][0:newline[0].find('_')], gene_name, newline[2], float(newline[3])]
		QC_filtered.append(newline)
	return(QC_filtered)

#%%
## 2.2 dict of low_coverage amplicon #, name of amplicon, low_CYP2D6

def Low_coverage_dict(QC_filter):
	low_coverage_count = {}
	low_coverage_amp = {}
	low_CYP2D6 = {}
	for line in QC_filtered:
		if '792978_CYP3A4-exon7-1' in line[2] or 'GRIK4_intron3' in line[2]: continue
		if 'CYP2D6' in line[1]:
			low_CYP2D6[line[0]] = low_CYP2D6.get(line[0], 0) + 1
		#if line[3] > 30: continue ## only consider reads less than 30 
		low_coverage_count[line[0]] = low_coverage_count.get(line[0], 0) + 1 ## the count of low coverage amplicons
		if line[3] > 5: continue ## for ICD check: only consider reads less than 5
		low_coverage_amp[line[0]] = low_coverage_amp.get(line[0], [])
		low_coverage_amp[line[0]].append(line[1])
	low_coverage_amp ={k:list(set(v)) for (k, v) in low_coverage_amp.items()} ## {sample:gene name of low coverage amplicons}
	return low_coverage_count, low_coverage_amp, low_CYP2D6

## 2.3 Completely failed and potentially filed critical amplicons 
#%%
def Fail_samples(low_coverage_count, low_CYP2D6):
	#sample_failed_complete = {sample:count for sample, count in low_coverage_count.items() if count > 19 and low_CYP2D6.get(sample, 0)/count < 0.5}
	sample_failed_complete = {sample: low_CYP2D6.get(sample, 0)/count * 100 for sample, count in low_coverage_count.items() if count > 19}
	sample_failed_amplicon = {sample:low_coverage_count[sample] for sample in low_coverage_amp.keys() if sample not in sample_failed_complete.keys()} ## samples which require ICD check
	sample_CYP2D6_check = [sample for sample, count in low_CYP2D6.items() if low_CYP2D6[sample]/low_coverage_count[sample] > 0.5 and sample in sample_failed_complete.keys()]
	#print(sample_CYP2D6_check)
	return sample_failed_complete, sample_failed_amplicon.keys(), sample_CYP2D6_check
## return valuse: completely failed samples, potentially failed samples, CYP2D6 manual check list	

#%%
## 2.4 ICDs of samples which potentially failed on critical amplicon

def Sample_ICD(patient_ICD, failed_amplicon):
	sample_ICD = {}
	failed_amplicon_list = [sample.rstrip('B') for sample in failed_amplicon]
	for line in patient_ICD:
		newline = line.rstrip().split('\t')
		if 'SampleID' in newline[0]: continue
		if newline[0] in failed_amplicon_list:
			sample_ICD[newline[0]] = set([re.sub('\..*', '', icd) for icd in newline[1].split(', ')])
			#print(newline[1].split(', '))
	return sample_ICD

#%%

## 2.5 ICDs of low coverage amplicon
def Gene_ICD(failed_amplicon):
	gene_ICD = {}
#	 sum_failed_ICD = {}
	failed_amp_gene = {sample: low_coverage_amp[sample] for sample in failed_amplicon} ## potentially failed sample : corressponding genes
	genes = [gene for items in failed_amp_gene.values() for gene in items] ## flat the list structure of failed_amp_gene
	for line in drug_ICD:
		newline = line.split('\t')
		if 'Anesthesiology' in newline[0]: continue
		if newline[5] in genes:
			gene_ICD[newline[5]] = gene_ICD.get(newline[5], []) + newline[7].split('\t')[0].split(', ') # gene: coresponding ICD
	#gene_ICD = {gene:[icd for icds in icd_list for icd in icds] for gene, icd_list in gene_ICD.items()}
#	 for sample, genes in failed_amp_gene.items():
#		 icds = [gene_ICD[gene] for gene in genes]
#		 icds = [gene for genes in icds for gene in genes]
#		 sum_failed_ICD[sample.strip('B')] = set(icds) ## failed ICDs for each sample	
	return failed_amp_gene, gene_ICD

#%%

## 2.6. Generate ICD check list to help manual review failed on critical amplicons
def ICD_check():
	failed_checklist = {sample:{'ICD':icds} for sample, icds in sample_ICD.items() }
	## Add B back to ID
	for sample in list(failed_checklist.keys()):
	#print(sample+'??')
		if sample + 'B' in failed_amp_gene.keys():
		   #print(sample, sample+ 'B')
			sample_b = sample + 'B'
			failed_checklist[sample_b] = failed_checklist.pop(sample) ## Update the key, add B back to ID
			failed_checklist[sample_b]['Low coverage amplicon'] = {Gene:list(set(gene_ICD[Gene])) for Gene in failed_amp_gene[sample_b] if Gene != 'CYP2D8'}
		else:
			#print('**'+sample)
			failed_checklist[sample]['Low coverage amplicon'] = {Gene:list(set(gene_ICD[Gene])) for Gene in failed_amp_gene[sample] if Gene != 'CYP2D8'}
	## find the sample failed on critical amplicon by insertion between sets
	failed_on_amplicon = [sample for sample in failed_checklist.keys() if bool(failed_checklist[sample]['ICD'] & {icd for icds in list(failed_checklist[sample]['Low coverage amplicon'].values()) for icd in icds if icd != ''})]
	return failed_checklist, failed_on_amplicon

## 2.7 Check genotypes of controls
def Control_check():
	control_genotype = {line.strip().split('\t')[0]:line.strip().split('\t')[1:] for line in sample_genotypes if 'NA' in line.strip().split('\t')[0]}
	NA17244 = ['c.3435T>C/c.3435T>C/c.2677T>G/c.2677T>G', 'WT/WT', 'WT/c.-1252G>C', 'WT/c.*86A>C', 'WT/WT', 'WT/WT', 'WT/c.175-5285G>T', 'WT/c.-451C>T', 'WT/c.428G>A', 'WT/WT', 'WT/c.472G>A', '*1A/*1F', 'A785G/G516T', '*1/*1', '*1/*1', '*1/*1', '*2xN/*4', '*1A/*1A', '*3A/*3A', '*1/*1', '*1/*9A', 'WT/c.-48G>A', 'WT/WT', 'WT/WT', 'WT/WT', 'WT/WT', 'WT/WT', 'WT/WT', 'c.83-10039T>C/c.83-10039T>C', 'WT/c.313A>G', 'WT/WT', 'WT/WT', 'WT/c.614-2211T>C', 'c.551-3008C>G/c.551-3008C>G', 'WT/WT', 'WT/WT', 'WT/c.2155T>C', 'WT/C677T', '*5/*6/*12/*13', 'WT/c.106-38510G>T', 'WT/c.559C>T', 'WT/c.118A>G', 'WT/WT', '*1/*1', '*1/*1', '*1/*1', '*1/*2', '-1639G>A/-1639G>A', 'WT/c.1196A>G']
	NA17281 = ['WT/c.2677T>G', 'WT/WT', 'WT/c.-1252G>C', 'WT/c.*86A>C', 'WT/A1', 'WT/WT', 'WT/WT', 'WT/c.-451C>T', 'WT/WT', 'WT/c.*3475A>G', 'WT/c.472G>A', '*1F/*1F', 'A785G/G516T', '*1/*17', '*1/*1', '*1/*1', '*5/*9', '*1A/*1A', '*3A/*3A', '*1/*1', '*5/*5/*9A', 'WT/c.-48G>A', 'WT/WT', 'WT/WT', 'WT/WT', 'WT/WT', 'WT/WT', 'WT/WT', 'WT/c.83-10039T>C', 'WT/WT', 'WT/WT', 'WT/c.-1019G>C', 'c.614-2211T>C/c.614-2211T>C', 'c.551-3008C>G/c.551-3008C>G', 'WT/WT', 'WT/c.124+21A>C', 'c.2155T>C/c.2155T>C', 'C677T/A1298C', '*5/*6/*13', 'c.106-38510G>T/c.178-20044C>T/c.178-13122C>T', 'WT/WT', 'WT/WT', 'WT/WT', '*1/*5', '*1/*1', '*1/*28', '*1/*2', 'WT/-1639G>A', 'c.1196A>G/c.1196A>G']
	control_QC = {}
	for control in control_genotype.keys():
		if 'NA17244' in control:
			control_QC[control] = len([g_control for g_standard, g_control in zip(NA17244, control_genotype[control]) if g_standard != g_control])
		if 'NA17281' in control:
			control_QC[control] = len([g_control for g_standard, g_control in zip(NA17281, control_genotype[control]) if g_standard != g_control])
	print('====================================================================')
	print('====================================================================')
	print('Check genotype of controls:')
	for control in control_QC:
		if control_QC[control] > 3: print('Warning: %s may failed!! Manual check required!!'%control)
		else: print('%s passed!'%control)
	print('====================================================================')

## 3. Run script
if __name__ == '__main__':
	args = ParseArg()
	folder = args.Run_Name
	Run = folder[folder.find('Run'):folder.find('Run')+6]
	#folder = '181112_CLIA_Plus_Run723_M01519_0042_000000000-C2LBF'
	#os.chdir('/data/CLIA-Data/PGxOne_V3/Testing/BI_Data_Analysis%s'%folder)
	#os.chdir('T:/PGxOne_V3/Production/BI_Data_Analysis/%s'%folder)
#	 QC_check = 'T:/PGxOne_V3/Production/BI_Data_Analysis/%s/sample_QC_low_coverage.txt'%folder ## sample_QC_low_coverage file
#	 Accession = 'T:/PGxOne_V3/Production/BI_Data_Analysis/%s/sample_codes_drugs_accession.txt'%folder ## sample accession file
#	 Drug_info = 'T:/PGxOne_V3/Production/BI_Data_Analysis/%s/PGxOneV3_drug_action.txt'%folder ## gene and corresponding ICD codes
	QC_check = '/data/CLIA-Data/PGxOne_V3/Production/BI_Data_Analysis/%s/sample_QC_low_coverage.txt'%folder ## sample_QC_low_coverage file
	Accession = '/data/CLIA-Data/PGxOne_V3/Production/BI_Data_Analysis/%s/sample_codes_drugs_accession.txt'%folder ## sample accession file
	Drug_info = '/data/CLIA-Data/PGxOne_V3/Production/BI_Data_Analysis/%s/PGxOneV3_drug_action.txt'%folder ## gene and corresponding ICD codes
	#Genotypes = '/data/CLIA-Data/PGxOne_V3/Production/BI_Data_Analysis/%s/sample_output_genotype_test.txt'%folder ## genotypes of all samples
	Genotypes = '/data/CLIA-Data/PGxOne_V3/Production/BI_Data_Analysis/%s/sample_output_genotype.txt'%folder ## genotypes of all samples


	with open(QC_check) as raw:
		QC_record = raw.readlines()
		
	with open(Accession) as raw:
		patient_ICD = raw.readlines()
		
	with open(Drug_info) as raw:
		drug_ICD = raw.readlines()

	with open(Genotypes) as raw:
		sample_genotypes = raw.readlines()

	QC_filtered = Low_coverage_filter(QC_record)
	low_coverage_count, low_coverage_amp, low_CYP2D6 = Low_coverage_dict(QC_filtered)
	failed_complete, failed_amplicon, sample_CYP2D6_check = Fail_samples(low_coverage_count, low_CYP2D6)
	sample_ICD = Sample_ICD(patient_ICD, failed_amplicon) ## samples with corresponding ICDs from accession
	failed_amp_gene, gene_ICD= Gene_ICD(failed_amplicon)
	failed_checklist, failed_on_amplicon = ICD_check()
	Control_check()
	print('Completely failed sample: CYP2D6%\n')
	print('Completely failed sample:', file = open('%s_QC.txt'%Run, 'w+'))
	n = 1 ## count for failed samples
	for line in failed_complete.items():
		print('{0}. Sample: {1}, CYP2D6%: {2:.2f}'.format(n, line[0], line[1]))
		print('%s'%line[0], file = open('%s_QC.txt'%Run, 'a+'))
		n += 1
	print('\n')
	print('********************************************************************')
	print('********************************************************************')
	print('\n')
	print('Failed on critical amplicons: \n{}'.format('\n'.join(failed_on_amplicon)))
	print('********************************************************************')
	print('Samples failed on amplicons:', file = open('%s_QC.txt'%Run, 'a+'))
	n = 1
	for gene in failed_on_amplicon:
		print('\n')
		print('{}. Check Low coverage:{}'.format(n, gene))
		print('%s'%gene, file = open('%s_QC.txt'%Run, 'a+'))
		print('ICD: {}\n'.format(failed_checklist[gene]['ICD']))
		print('ICD of low coverage amplicons:')
		for gene_icds in failed_checklist[gene]['Low coverage amplicon'].items():
			if bool(set(gene_icds[1]) & set(failed_checklist[gene]['ICD'])):
				pprint.pprint(gene_icds, width=1000)
		print('********************************************************************')
	n += 1
