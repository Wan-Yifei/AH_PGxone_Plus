#!/usr/bin/python
#-*- coding: utf-8 -*-

import Gene_Scored as GS
import re
import sys
sys.path.append('/home/yifei.wan/PGx_QC/QC_Modules/Gene_Scored.py')
import Gene as G

class Sample:

    Amplicons_scored_list = ["CYP1A2", "CYP2C19", "CYP2C9", "CYP2D6", "CYP3A4", "CYP3A5", "CYP4F2", "DPYD", "NAT2", "TPMT"]

    def __init__(self, ID, Output_geno, Code_drug, Active_score, Drug_action, Low_coverage, Range, Gene_KB):
        self.ID = ID 
        self.ICD = self.get_ICD(Code_drug)
        self.LowCount_amplicon, self.LowCount_ex_amplicon, self.LowCount_scored_amplicon = self.get_low_count_amp(Low_coverage) 
        ## QC result of amplicons with coverage less than 5 (no score check requirement).
        self.QC_Complete_Pass, self.QC_CYP2D6_notice = self.Global_QC() 
        if self.QC_Complete_Pass:
            self.Failed_critical_amp, self.Failed_amp_notice, self.QC_amplicon_pass = self.Amp_less_5_QC(Drug_action, Range)
        #if self.QC_amplicon_pass:
            ## dict of Gene object having socre info with coverage less than 5 
        self.Failed_critical_scored_amp, self.Failed_scored_amp_notice, self.scored_QC = self.Scored_less_5_QC(Output_geno, Active_score, Drug_action, Low_coverage, Range, Gene_KB)        
        self.Check()

    def Check(self):
        print 'Sample ID: %s'%self.ID
        print 'Sample ICDs: %s'%self.ICD
        print 'Coverage less than 5: %s'%self.LowCount_ex_amplicon
        print 'Scored amplicons having coverage less than 5: %s'%self.LowCount_scored_amplicon
        print 'Gobal Pass: %s'%self.QC_Complete_Pass
        print 'CYP2D6 global QC status note: %s'%self.QC_CYP2D6_notice
        try:
            print 'Non-scored amplicon QC status note: %s'%self.Failed_amp_notice
            print 'Non-scored amplicon QC pass: $s'%self.QC_amplicon_pass
        except:
            print 'No gene objects generated!'
        try:
            print self.Failed_scored_amp_notice
            print 'Scored amplicon QC pass: %s'%self.scored_QC
        except:
            print 'No scored objects generated!'

    def get_ICD(self, Code_drug):
        ICDs = next(ICD.strip().split('\t')[1].split(', ') for ICD in Code_drug if self.ID in ICD)
        sample_ICDs = [re.sub('\..*', '', ICD) for ICD in ICDs]
        return sample_ICDs 
        
    def get_low_count_amp(self, Low_coverage):
        ## key: amplicon_name, value: count
        Low_amplicons = {amp.strip().split('\t')[2] : int(amp.strip().split('\t')[3]) for amp in Low_coverage if self.ID in amp} 
        ## key: amplicon_name, value: gene_name
        gene_amplicons = {amp.strip().split('\t')[2] : amp.strip().split('\t')[1].split('_')[0] for amp in Low_coverage if self.ID in amp}  
        ## amplicons with coverage less than 6. key: amplicon_name, value: gene_name
        Low_ex_amplicons = {amp : gene_amplicons[amp] for amp, count in Low_amplicons.items() if count < 6 and amp not in ['792978_CYP3A4-exon7-1', 'GRIK4_intron3']} 
        ## amplicons having score info, key: gene_name, value: amplicon_name 
        Low_scored_amplicons = {}
        for amp in Low_ex_amplicons.keys():
            if next((scored in amp) for scored in self.Amplicons_scored_list if scored in amp and 'CNV_CYP2D6' not in amp):
                values = Low_scored_amplicons.get(Low_ex_amplicons[amp], [])
                Low_scored_amplicons[Low_ex_amplicons[amp]] = values + [amp] ## key: gene, values: amplicons (list) 
        return Low_amplicons, Low_ex_amplicons, Low_scored_amplicons

    def Global_QC(self):
        Low_CYP2D6 = len([amp for amp in self.LowCount_amplicon.keys() if 'CYP2D6' in amp])
        CYP2D6 = Low_CYP2D6/28
        CYP2D6_check = None
        Low_amplicons = len(self.LowCount_amplicon.keys())
        if Low_amplicons > 10 and Low_CYP2D6 > 0.8:
            QC_status = False 
            CYP2D6_check = '%s CYP2D6 amplicons are Low coverage, please check!'%Low_CYP2D6 ## Del/Del check required
        elif Low_amplicons > 20:
            QC_status = False ## Completely failed
        else:
            QC_status = True ## Pass global check
        return QC_status, CYP2D6_check
        
    def Scored_less_5_QC(self, Output_geno, Active_score, Drug_action, Low_coverage, Range, Gene_KB):
        ## Low coverage amplicons much associate to ICD code of sample:
        ## key: gene, value: Gene_scored instance 
        Amplicon_check = {low_amp[0] : GS.Gene_Scored(self.ID, self.ICD, low_amp[0], Output_geno, low_amp[1], Active_score, Drug_action, Low_coverage, Range, Gene_KB) \
        for low_amp in self.LowCount_scored_amplicon.items() if low_amp[0] in self.Failed_critical_amp} 
        ## Failed_scored_gene dict: key: gene, value: QC result of gene
        Failed_scored_gene = {gene[0]: gene[1].potential_Phenotype for gene in Amplicon_check.items() if not gene[1].potential_Phenotype}
        Scored_gene_pass = all(Failed_scored_gene.values())
        Failed_scored_amp_notice = 'Sample %s has failed on critical amplicons: %s'%(self.ID, Failed_scored_gene.keys())
        return Failed_scored_gene, Failed_scored_amp_notice, Scored_gene_pass

    def Amp_less_5_QC(self, Drug_action, Range):
        ## the amplicons of each gene should be organize as a list
        Low_ex_gene = {}
        for amp in self.LowCount_ex_amplicon.keys():
           values = Low_ex_gene.get(amp, [])
           Low_ex_gene[self.LowCount_ex_amplicon[amp]] = values + [amp] ## key: gene, values: amplicons

        if len(self.LowCount_ex_amplicon) > 7:
             QC_status = False ## too many critial amplicons have extrme low coverage
             Failed_amp_notice = '%s critical amplicons have coverage less than 6, sample has completely failed!'%len(LowCount_ex_amplicon)
        else:
             Amplicon_check = {low_gene[0] : G.Gene(self.ID, self.ICD, low_gene[0], Drug_action, low_gene[1], Range) for low_gene in Low_ex_gene.items()}
        Failed_gene = [gene[0] for gene in Amplicon_check.items() if gene[1].ICD_relevant and gene[0]]
        Potential_failed_gene = [gene for gene in Failed_gene if gene not in self.Amplicons_scored_list]
        QC_status = bool(Potential_failed_gene)
        if QC_status:
            Failed_amp_notice = 'Sample %s has failed on critical amplicons: %s'%(self.ID, Failed_gene)
        else:
            Failed_amp_notice = None
        return Failed_gene, Failed_amp_notice, QC_status 
