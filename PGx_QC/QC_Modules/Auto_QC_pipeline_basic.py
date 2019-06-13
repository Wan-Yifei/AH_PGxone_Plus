# =============================================================================
# Automatical QC pipeline of PGxOne
# @author: Yifei Wan
# 
# =============================================================================
# 06/12/2019 Basic version 0.0.1
# Summary: 
# This pipeline accept runfolder name to process QC for specified run.
#
# Input: 
# 1. The name of run folder;
# Output:
# 1. QC check list.
# =============================================================================
# 06/12/2019 Basic version 0.0.2
#
# Feat:
# 1. Add # check for action files.
# =============================================================================

import sys
import os
import glob
import re
from colorama import Fore, Back, Style, init 

#sys.path.append('/home/yifei.wan/PGx_QC/Auto_QC.py')
sys.path.append('/home/yifei.wan/PGx_QC/QC_Modules/gene_scored.py')
sys.path.append('/home/yifei.wan/PGx_QC/QC_Modules/sample.py')
sys.path.append('/home/yifei.wan/PGx_QC/QC_Modules/control.py')

import sample as aq
import sample
import control
import gene_scored

Runfolder = sys.argv[1]
path = '/data/CLIA-Data/PGxOne_V3/Production/BI_Data_Analysis/%s'%Runfolder

Drug_action_path = '%s/%s'%(path, 'PGxOneV3_drug_action.txt')
Low_coverage_path = '%s/%s'%(path, 'sample_QC_low_coverage.txt')
Active_score_path = '%s/%s'%(path, 'PGxOneV3_gene_allele_activity_score.txt')
Output_geno_path = '%s/%s'%(path, 'sample_output_genotype.txt')
Range_path = glob.glob('%s/NA17281_S[0-9][0-9].txt'%path)[0] 
Gene_var_path = '/home/yifei.wan/AH_Project/PGx_QC/PGx_GV/PGxOne_v3_Gene_Variant_List.txt'
Code_drug_path = '%s/%s'%(path, 'sample_codes_drugs.txt')
CYP_hom_path = '/data/CLIA-Data/PGxOne_V3/Production/BI_Data_Analysis/%s/sample_QC_CYP2D6_deletion_hom.txt'%Runfolder
LIS = '%s/LIS'%path ## path of LIS folder

def lis_count(LIS): ## check the count of action files
    print("========================================================")
    print("Count# of action files")
    print("")
    LIS_n = len([name for name in os.listdir(LIS) if os.path.isfile(LIS + '/' + name)])
    if LIS_n == 44: print(Fore.GREEN + 'LIS # check: %d'%LIS_n)
    else: print(Fore.RED + 'LIS # check: %d'%LIS_n)
    print("========================================================")

def low_coverage_scan(Low_coverage):
    samples = [line.strip().split('\t')[0].split('_')[0] for line in Low_coverage if 'Sample' not in  line]
    ids = list(set(samples))
    #print ids
    return ids

def get_control_ID(Output_geno):
    controls = [line.strip().split('\t')[0] for line in Output_geno if 'NA' in line.split('\t')[0]]
    return controls

def cyp_homo_check(cyp_list):
    CYP_genotypes = {line.strip().split('\t')[0]:line.strip().split('\t')[1] for line in cyp_list if 'sample_ID' not in line}
    print("========================================================")
    print('Homo/Heter check for CYP2D6')
    print('')
    for sample in CYP_genotypes.keys():
        if CYP_genotypes[sample].split('/')[0] != CYP_genotypes[sample].split('/')[1]:
            print(Fore.GREEN + '%s passed!'%sample)
        else:
            print(Fore.RED + 'The genotype of CYP2D6 of %s needs check!!'%sample)
            print('')
    print("========================================================")

## colorful print init
init(autoreset = True)

with open(Code_drug_path, 'r', errors='replace') as CD, open(Drug_action_path, 'r', errors='replace') as DA, open(
    Low_coverage_path, 'r', errors='replace') as LC, open(Range_path, 'r', errors='replace') as RP, open(
    Active_score_path, 'r', errors='replace') as AS, open(Output_geno_path, 'r', errors='replace') as OG, open(
    Gene_var_path, 'r', errors='replace') as GK, open(CYP_hom_path, 'r', errors='replace') as CP:
        Active_score = AS.readlines()
        Drug_action = DA.readlines()
        Low_coverage = LC.readlines()
        Range = RP.readlines()
        Output_geno = OG.readlines()
        Gene_KB = GK.readlines()
        Code_drug = CD.readlines()
        cyp_list = CP.readlines()

        potential_failed_samples = low_coverage_scan(Low_coverage)
        ctrls = get_control_ID(Output_geno)
        #print ctrls
        print("========================================================")
        print("========================================================")
        print('Run folder: %s'%Runfolder)
        print("========================================================")
        print("Check controls:")
        print("")
        
        for ctrl_id in ctrls:
            if ctrl_id in potential_failed_samples:
                low_coverage_flag = True ## contrl is potential failed
            else:
                low_coverage_flag = False
            conl = (control.Control(ctrl_id, Output_geno, Code_drug, Active_score
            , Drug_action, Low_coverage, Range, Gene_KB, low_coverage_flag))
            if conl.standard_pass:
                print(Fore.GREEN + '%s passed!'%conl.ID)
            if not conl.cyp2d6_pass:
                print(Fore.YELLOW + 'The genotype of CYP2D6 does not match SOP: %s'%conl.whole_genotype[17])
        print("")

        lis_count(LIS)
        cyp_homo_check(cyp_list)

        print("Completely failed samples:")
        print("")
        complete_failed = {} 
        critical_failed = {}
        for ID in potential_failed_samples:
            if 'NA' not in ID:
                check_case = aq.Sample(ID, Output_geno, Code_drug, Active_score
                , Drug_action, Low_coverage, Range, Gene_KB)

                if not check_case.QC_complete_pass:
                    if check_case.swab_b_flag:
                        complete_failed[check_case.ID + 'B'] = check_case.QC_CYP2D6_notice
                    else:
                        complete_failed[check_case.ID] = check_case.QC_CYP2D6_notice
                elif not check_case.QC_amplicon_pass:
                    if 'completely failed' in check_case.failed_amp_notice:
                        if check_case.swab_b_flag:
                            complete_failed[check_case.ID + 'B'] = check_case.QC_CYP2D6_notice
                        else:
                            complete_failed.append[check_case.ID] = check_case.QC_CYP2D6_notice
                    else:
                        if check_case.swab_b_flag:
                            critical_failed[check_case.ID + 'B'] = check_case.failed_critical_amp
                        else:
                            critical_failed[check_case.ID] = check_case.failed_critical_amp
                elif not check_case.scored_QC:
                    if check_case.swab_b_flag:
                        critical_failed[check_case.ID + 'B'] = list(check_case.failed_critical_scored_amp.keys())
                    else:
                        critical_failed[check_case.ID] = list(check_case.failed_critical_scored_amp.keys())
                else:
                    pass
        
        n = 1
        for case in complete_failed.items():
            print('%s. %s: '%(n,case[0]), case[1])
            n += 1

        print("========================================================")
        print("Samples failed on critical amplicons:")
        print("")
        n = 1
        for case in critical_failed.items():
            print("%s. %s : failed on %s"%(n, case[0], case[1]))
            n += 1
        print("========================================================")

## write QC output to the QC list
Run_ind = Runfolder[Runfolder.find('Run'):Runfolder.find('Run')+7]
print('Completely failed sample:', file = open('/home/yifei.wan/AH_Project/PGx_QC/auto_QC/%s_QC.txt'%Run_ind, 'w+'))
for case in complete_failed:
    print(case, file = open('/home/yifei.wan/AH_Project/PGx_QC/auto_QC/%s_QC.txt'%Run_ind, 'a+'))

print('Samples failed on critical amplicons:', file = open('/home/yifei.wan/AH_Project/PGx_QC/auto_QC/%s_QC.txt'%Run_ind, 'a+'))
for case in critical_failed.items():
    print(case[0], file = open('/home/yifei.wan/AH_Project/PGx_QC/auto_QC/%s_QC.txt'%Run_ind, 'a+'))

