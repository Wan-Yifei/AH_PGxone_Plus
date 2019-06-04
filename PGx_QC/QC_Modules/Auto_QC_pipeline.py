import sys
import os
import glob
import re

#sys.path.append('/home/yifei.wan/PGx_QC/Auto_QC.py')
sys.path.append('/home/yifei.wan/PGx_QC/QC_Modules/gene_scored.py')
sys.path.append('/home/yifei.wan/PGx_QC/QC_Modules/sample.py')

import sample as aq

Runfolder = sys.argv[1]
path = '/data/CLIA-Data/PGxOne_V3/Production/BI_Data_Analysis/%s'%Runfolder

Drug_action_path = '%s/%s'%(path, 'PGxOneV3_drug_action.txt')
Low_coverage_path = '%s/%s'%(path, 'sample_QC_low_coverage.txt')
Active_score_path = '%s/%s'%(path, 'PGxOneV3_gene_allele_activity_score.txt')
Output_geno_path = '%s/%s'%(path, 'sample_output_genotype.txt')
Range_path = glob.glob('%s/NA17281_S[0-9][0-9].txt'%path)[0] 
Gene_var_path = '/home/yifei.wan/AH_Project/PGx_QC/PGx_GV/PGxOne_v3_Gene_Variant_List.txt'
Code_drug_path = '%s/%s'%(path, 'sample_codes_drugs.txt')

#print Drug_action_path
#print Low_coverage_path
#print Range_path

#ID = 'A-1600158824'
#ID = 'A-1600161746B'
ID = sys.argv[2]
amp_name = ['792984_CYP3A5-exon2-2-exon2-1']
gene_name = 'CYP3A5'
ICDs = ['F32.9', 'F41.9']
sample_ICD = [re.sub('\..*', '', ICD) for ICD in ICDs]

with open(Code_drug_path, 'r') as CD, open(Drug_action_path, 'r') as DA, open(Low_coverage_path, 'r') as LC, open(Range_path, 'r') as RP, open(Active_score_path, 'r') as AS, open(Output_geno_path, 'r') as OG, open(Gene_var_path, 'r') as GK:
        Active_score = AS.readlines()
        Drug_action = DA.readlines()
        Low_coverage = LC.readlines()
        Range = RP.readlines()
        Output_geno = OG.readlines()
        Gene_KB = GK.readlines()
        Code_drug = CD.readlines()
        #check_point = aq.Gene(ID, gene_name, Output_geno, amp_name, Active_score, Drug_action, Low_coverage, Range, Gene_KB)
        #check_point = aq.Gene_Scored(ID, sample_ICD, gene_name, Output_geno, amp_name, Active_score, Drug_action, Low_coverage, Range, Gene_KB)
        check_point = aq.Sample(ID, Output_geno, Code_drug, Active_score, Drug_action, Low_coverage, Range, Gene_KB)

        #check_point = aq.Gene(ID, gene_name, OG, amp_name, AS, DA, LC, Range)

