import sys
import os
import glob
import re

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

def low_coverage_scan(Low_coverage):
    samples = [line.strip().split('\t')[0].split('_')[0] for line in Low_coverage if 'Sample' not in  line]
    ids = list(set(samples))
    #print ids
    return ids

def get_control_ID(Output_geno):
    controls = [line.strip().split('\t')[0] for line in Output_geno if 'NA' in line.split('\t')[0]]
    return controls

with open(Code_drug_path, 'r') as CD, open(Drug_action_path, 'r') as DA, open(
    Low_coverage_path, 'r') as LC, open(Range_path, 'r') as RP, open(
    Active_score_path, 'r') as AS, open(Output_geno_path, 'r') as OG, open(
    Gene_var_path, 'r') as GK:
        Active_score = AS.readlines()
        Drug_action = DA.readlines()
        Low_coverage = LC.readlines()
        Range = RP.readlines()
        Output_geno = OG.readlines()
        Gene_KB = GK.readlines()
        Code_drug = CD.readlines()

        potential_failed_samples = low_coverage_scan(Low_coverage)
        ctrls = get_control_ID(Output_geno)
        #print ctrls
        for ctrl_id in ctrls:
            if ctrl_id in potential_failed_samples:
                low_coverage_flag = True ## contrl is potential failed
            else:
                low_coverage_flag = False
            conl = (control.Control(ctrl_id, Output_geno, Code_drug, Active_score
            , Drug_action, Low_coverage, Range, Gene_KB, low_coverage_flag))
            print conl.ID
            print 'Control passed' + " : " + str(conl.standard_pass)
            print ('CYP2D6 genotype of control' + conl.ID + " : " + 
                    str(conl.cyp2d6_pass) + " " + conl.whole_genotype[16])
        
        print "========================================================"
        print "========================================================\n"
        for ID in potential_failed_samples:
            if 'NA' not in ID:
                check_case = aq.Sample(ID, Output_geno, Code_drug, Active_score
                , Drug_action, Low_coverage, Range, Gene_KB)
                if not check_case.QC_complete_pass:
                    check_case.check()
                    print "========================================================"
                    print "========================================================\n"
                elif not check_case.QC_amplicon_pass:
                    check_case.check()
                    print "========================================================"
                    print "========================================================\n"
                elif not check_case.scored_QC:
                    check_case.check()
                    print "========================================================"
                    print "========================================================\n"
                else:
                    pass
 
