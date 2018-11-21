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
import argparse

def ParseArg():
    
    p = argparse.ArgumentParse(description = 'Automatically check low coverage amplicon')
    p.add_argument("Run_Name",type=str, help="Full name of run folder")


    
# 2. Create dictionary of samples with low covergae amplicon
#%%
## 2.1 Remove coverage larger than 5

def Low_coverage_filter(QC_record):
    QC_filtered = []
    for line in QC_record:
        newline = line.rstrip().split('\t')
        if newline[0] == 'Sample': continue ## skip the header
        if float(newline[3]) > 5 : continue ## remove coverage larger than 5 counts
        newline = [newline[0][0:newline[0].rfind('_')], newline[1][0:newline[1].rfind('_')], newline[2], float(newline[3])]
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
        low_coverage_count[line[0]] = low_coverage_count.get(line[0], 0) + 1  
        low_coverage_amp[line[0]] = low_coverage_amp.get(line[0], [])
        low_coverage_amp[line[0]].append(line[1])
        if 'CYP2D6' in line[1]:
            low_CYP2D6[line[0]] = low_CYP2D6.get(line[0], 0) + 1
    low_coverage_amp ={k:list(set(v)) for (k, v) in low_coverage_amp.items()}
    return low_coverage_count, low_coverage_amp, low_CYP2D6
         
## 2.3 Completely failed and potentially filed on critical amplicons 
#%%
def Fail_samples(low_coverage_count, low_CYP2D6):
    sample_failed_complete = {sample:count for sample, count in low_coverage_count.items() if count > 19 and low_CYP2D6.get(sample, 0)/count < 0.5}
    sample_failed_amplicon = {sample:count for sample, count in low_coverage_count.items() if count < 20 and low_CYP2D6.get(sample, 0)/count < 0.5}
    sample_CYP2D6_check = [sample for sample, count in low_CYP2D6.items() if low_CYP2D6[sample]/low_coverage_count[sample] > 0.5 and sample in sample_failed_complete.keys()]
    #print(sample_CYP2D6_check)
    return sample_failed_complete.keys(), sample_failed_amplicon.keys(), sample_CYP2D6_check
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
#    sum_failed_ICD = {}
    failed_amp_gene = {sample: low_coverage_amp[sample] for sample in failed_amplicon} ## potentially failed sample : corressponding genes
    genes = [gene for items in failed_amp_gene.values() for gene in items] ## flat the list structure of failed_amp_gene
    for line in drug_ICD:
        newline = line.split('\t')
        if 'Anesthesiology' in newline[0]: continue
        if newline[5] in genes:
            gene_ICD[newline[5]] = gene_ICD.get(newline[5], []) + newline[7].split('\t')[0].split(', ') # gene: coresponding ICD
    #gene_ICD = {gene:[icd for icds in icd_list for icd in icds] for gene, icd_list in gene_ICD.items()}
#    for sample, genes in failed_amp_gene.items():
#        icds = [gene_ICD[gene] for gene in genes]
#        icds = [gene for genes in icds for gene in genes]
#        sum_failed_ICD[sample.strip('B')] = set(icds) ## failed ICDs for each sample   
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
            failed_checklist[sample_b]['Low coverage amplicon'] = {Gene:list(set(gene_ICD[Gene])) for Gene in failed_amp_gene[sample_b]}
        else:
            #print('**'+sample)
            failed_checklist[sample]['Low coverage amplicon'] = {Gene:list(set(gene_ICD[Gene])) for Gene in failed_amp_gene[sample]}
    ## find the sample failed on critical amplicon by insertion between sets
    failed_on_amplicon = [sample for sample in failed_checklist.keys() if len(failed_checklist[sample]['ICD'] & {icd for icds in (list(failed_checklist[sample]['Low coverage amplicon'].values())) for icd in icds})]
    return failed_checklist, failed_on_amplicon

if __name__ == '__main__':
    args = ParseArg()
    folder = args.Run_Name
    os.chdir('/data/CLIA-Data/PGxOne_V3/Production/%s'%folder)
    QC_check = 'sample_QC_low_coverage.txt' ## sample_QC_low_coverage file
    Accession = 'sample_codes_drugs_accession.txt' ## sample accession file
    Drug_info = 'PGxOneV3_drug_action.txt' ## gene and corresponding ICD codes
    
    with open(QC_check) as raw:
        QC_record = raw.readlines()
        
    with open(Accession) as raw:
        patient_ICD = raw.readlines()
        
    with open(Drug_info) as raw:
        drug_ICD = raw.readlines()

    QC_filtered = Low_coverage_filter(QC_record)
    low_coverage_count, low_coverage_amp, low_CYP2D6 = Low_coverage_dict(QC_filtered)
    failed_complete, failed_amplicon, sample_CYP2D6_check = Fail_samples(low_coverage_count, low_CYP2D6)
    sample_ICD = Sample_ICD(patient_ICD, failed_amplicon) ## samples with corresponding ICDs from accession
    failed_amp_gene, gene_ICD= Gene_ICD(failed_amplicon)
    failed_checklist, failed_on_amplicon = ICD_check()
    print('Completely failed sample: {}\t'.format('\t'.join(list(failed_complete))))
    print('Failed on critical amplicons: {}\t'.format('\t'.join(failed_on_amplicon)))
    for gene in failed_on_amplicon:
        print('Check Low coverage:{}'.format(gene))
        print('ICD: {}\n'.format(failed_checklist[gene]['ICD']))
        for gene_icds in failed_checklist[gene]['Low coverage amplicon'].items():
            print('Low coverage amplicon: {}\n'.format(gene_icds))