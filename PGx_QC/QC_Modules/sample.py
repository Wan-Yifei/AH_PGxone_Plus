#!/usr/bin/python
#-*- coding: utf-8 -*-

import gene_scored as GS
import re
import sys
sys.path.append('/home/yifei.wan/PGx_QC/QC_Modules/gene_scored.py')
import gene as G

class Sample:

    AMPLICONS_SCORED_LIST = ["CYP1A2", "CYP2C19", "CYP2C9", "CYP2D6", "CYP3A4", "CYP3A5", "CYP4F2", "DPYD", "NAT2", "TPMT"]

    def __init__(self, ID, Output_geno, Code_drug, Active_score, Drug_action, Low_coverage, Range, Gene_KB):
        self.ID = ID 
        self.ICD = self.get_ICD(Code_drug)
        self.low_count_amplicon, self.low_count_ex_amplicon, self.low_count_scored_amplicon = self.get_low_count_amp(Low_coverage) 
        ## QC result of amplicons with coverage less than 5 (no score check requirement).
        self.QC_complete_pass, self.QC_CYP2D6_notice = self.global_QC() 
        if self.QC_complete_pass:
            self.failed_critical_amp, self.failed_amp_notice, self.QC_amplicon_pass = self.amp_less_5_QC(Drug_action, Range)
        #if self.QC_amplicon_pass:
            ## dict of Gene object having socre info with coverage less than 5 
        self.failed_critical_scored_amp, self.failed_scored_amp_notice, self.scored_QC = self.scored_less_5_QC(Output_geno, Active_score, Drug_action, Low_coverage, Range, Gene_KB)        
        self.Check()

    def Check(self):
        print 'Sample ID: %s'%self.ID
        print 'Sample ICDs: %s'%self.ICD
        print 'Coverage less than 5: %s'%self.low_count_ex_amplicon
        print 'Scored amplicons having coverage less than 5: %s'%self.low_count_scored_amplicon
        print 'Gobal Pass: %s'%self.QC_complete_pass
        print 'CYP2D6 global QC status note: %s'%self.QC_CYP2D6_notice
        try:
            print 'Non-scored amplicon QC status note: %s'%self.failed_amp_notice
            print 'Non-scored amplicon QC pass: $s'%self.QC_amplicon_pass
        except:
            print 'No gene instances generated!'
        try:
            print self.failed_scored_amp_notice
            print 'Scored amplicon QC pass: %s'%self.scored_QC
        except:
            print 'No scored objects generated!'

    def get_ICD(self, Code_drug):
        ICDs = next(ICD.strip().split('\t')[1].split(', ') for ICD in Code_drug if self.ID in ICD)
        sample_ICDs = [re.sub('\..*', '', ICD) for ICD in ICDs]
        return sample_ICDs 
        
    def get_low_count_amp(self, Low_coverage):
        ## key: amplicon_name, value: count
        low_amplicons = {amp.strip().split('\t')[2] : int(amp.strip().split('\t')[3]) for amp in Low_coverage if self.ID in amp} 
        ## key: amplicon_name, value: gene_name
        gene_amplicons = {amp.strip().split('\t')[2] : amp.strip().split('\t')[1].split('_')[0] for amp in Low_coverage if self.ID in amp}  
        ## amplicons with coverage less than 6. key: amplicon_name, value: gene_name
        low_ex_amplicons = {amp : gene_amplicons[amp] for amp, count in low_amplicons.items() if count < 6 and amp not in ['792978_CYP3A4-exon7-1', 'GRIK4_intron3']} 
        ## amplicons having score info, key: gene_name, value: amplicon_name 
        low_scored_amplicons = {}
        for amp in low_ex_amplicons.keys():
            if next((scored in amp) for scored in self.AMPLICONS_SCORED_LIST if scored in amp and 'CNV_CYP2D6' not in amp):
                values = low_scored_amplicons.get(low_ex_amplicons[amp], [])
                low_scored_amplicons[low_ex_amplicons[amp]] = values + [amp] ## key: gene, values: amplicons (list) 
        return low_amplicons, low_ex_amplicons, low_scored_amplicons

    def global_QC(self):
        low_CYP2D6 = len([amp for amp in self.low_count_amplicon.keys() if 'CYP2D6' in amp])
        CYP2D6 = low_CYP2D6/28
        CYP2D6_check = None
        low_amplicons = len(self.low_count_amplicon.keys())
        if low_amplicons > 10 and low_CYP2D6 > 0.8:
            QC_status = False 
            CYP2D6_check = '%s CYP2D6 amplicons are low coverage, please check!'%low_CYP2D6 ## Del/Del check required
        elif low_amplicons > 20:
            QC_status = False ## Completely failed
        else:
            QC_status = True ## Pass global check
        return QC_status, CYP2D6_check
        
    def scored_less_5_QC(self, Output_geno, Active_score, Drug_action, Low_coverage, Range, Gene_KB):
        ## low coverage amplicons much associate to ICD code of sample:
        ## key: gene, value: Gene_scored instance 
        amplicon_check = {low_amp[0] : GS.GeneScored(self.ID, self.ICD, low_amp[0], Output_geno, low_amp[1], Active_score, Drug_action, Low_coverage, Range, Gene_KB) \
        for low_amp in self.low_count_scored_amplicon.items() if low_amp[0] in self.failed_critical_amp} 
        ## failed_scored_gene dict: key: gene, value: QC result of gene
        failed_scored_gene = {gene[0]: gene[1].potential_phenotype for gene in amplicon_check.items() if not gene[1].potential_phenotype}
        scored_gene_pass = all(failed_scored_gene.values())
        failed_scored_amp_notice = 'Sample %s has failed on critical amplicons: %s'%(self.ID, failed_scored_gene.keys())
        return failed_scored_gene, failed_scored_amp_notice, scored_gene_pass

    def amp_less_5_QC(self, Drug_action, Range):
        ## the amplicons of each gene should be organize as a list
        low_ex_gene = {}
        for amp in self.low_count_ex_amplicon.keys():
           values = low_ex_gene.get(amp, [])
           low_ex_gene[self.low_count_ex_amplicon[amp]] = values + [amp] ## key: gene, values: amplicons

        if len(self.low_count_ex_amplicon) > 7:
             QC_status = False ## too many critial amplicons have extrme low coverage
             failed_amp_notice = '%s critical amplicons have coverage less than 6, sample has completely failed!'%len(low_count_ex_amplicon)
        else:
             amplicon_check = {low_gene[0] : G.Gene(self.ID, self.ICD, low_gene[0], Drug_action, low_gene[1], Range) for low_gene in low_ex_gene.items()}
        failed_gene = [gene[0] for gene in amplicon_check.items() if gene[1].ICD_relevant and gene[0]]
        potential_failed_gene = [gene for gene in failed_gene if gene not in self.AMPLICONS_SCORED_LIST]
        QC_status = bool(potential_failed_gene)
        if QC_status:
            failed_amp_notice = 'Sample %s has failed on critical amplicons: %s'%(self.ID, failed_gene)
        else:
            failed_amp_notice = None
        return failed_gene, failed_amp_notice, QC_status 
