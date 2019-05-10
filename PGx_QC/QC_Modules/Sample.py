#!/usr/bin/python
#-*- coding: utf-8 -*-

sys.path.append('/home/yifei.wan/PGx_QC/QC_Modules/Gene_Scored.py')
import Gene_Scored as GS

class Sample:

    Amplicons_scored_list = ["CYP1A2", "CYP2C19", "CYP2C9", "CYP2D6", "CYP3A4", "CYP3A5", "CYP4F2", "DPYD", "NAT2", "TPMT"]

    def __init__(self, Output_geno, Code_drug, Active_score, Drug_action, Low_coverage, Range, Gene_KB):
        self.ID = ID 
        self.ICD = self.get_ICD(Drug_action)
        self.LowCount_Amplicon, self.exLowCount_Amplicon, self.LowCount_scored = self.get_low_count_amp(Low_coverage) 
        self.scored_QC = self.Scored_less_5_QC(Output_geno, amp_name, Active_score, Drug_action, Low_coverage, Range, Gene_KB) ## dict of Gene object having socre info with coverage less than 5 
        self.QC_Amplicon_Pass = self.Amp_less_5_QC() ## QC result of amplicons with coverage less than 5(no score check requirement.
        self.QC_Complete_Pass = self.Global_QC() 

    #def get_ID(self, Low_coverage):
    #   ID = list({sample.strip().split('\t')[0] for sample in Low_coverage})
    #   return ID
        
    def get_ICD(self, Code_drug):
        ICD = next(ICD.strip().split('\t')[1] for ICD in Code_drug if self.ID in ICD)
        return ICD 
        
    def get_low_count_amp(self, Low_coverage):
        Low_amplicons = {amp.strip().split('\t')[2] : amp.strip().split('\t')[3] for amp in Low_coverage if self.ID in amp} ## key: amplicon_name, value: count
        gene_amplicons = {amp.strip().split('\t')[2] : amp.strip().split('\t')[1].split('_')[0] for amp in Low_coverage if self.ID in amp} ## key: amplicon_name, value: gene_name 
        Low_ex_amplicons = {amp : gene_amplicons[amp] for amp, count in Low_amplicons.items() if count < 6} ## amplicons with coverage less than 6. key: amplicon_name, value: gene_name
        ## amplicons having score info, key: amplicon_name, value: gene_name 
        #Low_scored_amplicons = {amp : Low_ex_amplicons[amp] for amp in Low_ex_amplicons.keys() if next((scored in amp) for scored in Amplicons_scored_list if scored in amp and 'CNV_CYP2D6' not in amp)] 
        for amp in Low_ex_amplicons.keys():
            if next((scored in amp) for scored in Amplicons_scored_list if scored in amp and 'CNV_CYP2D6' not in amp)]:
                values = Low_scored_amplicons.get(Low_ex_amplicons[amp], [])
                Low_scored_amplicons[Low_ex_amplicons[amp]] = values.append(amp)  
        return Low_amplicons, Low_ex_amplicons, Low_scored_amplicons

    def Global_QC(self):
        Low_CYP2D6 = len([amp for amp in self.LowCount_Amplicons.keys() if 'CYP2D6' in amp])
        CYP2D6 = low_CYP2D6/28
        CYP2D6_check = None
        Low_amplicons = len(self.LowCount_Amplicons.keys())
        if Low_amplicons > 10 and Low_CYP2D6 > 0.8:
            QC_status = False 
            CYP2D6_check = '%s CYP2D6 amplicons are Low coverage, please check!'%Low_CYP2D6 ## Del/Del check required
        elif Low_amplicon > 20:
            QC_status = False ## Completely failed
        else:
            QC_status = True ## Pass global check
        
    def Scored_less_5_QC(self, Output_geno, Low_scored_amplicons, Active_score, Drug_action, Low_coverage, Range, Gene_KB):
        Amplicon_check = {low_amp[0] : GS.Gene_scored(self.ID, low_amp[1], Output_geno, low_amp[0], Active_score, Drug_acton, Low_coverage, Range, Gene_KB) for low_amp in Low_scored_amplicons.items()} 
        Failed_scored_gene = {gene.values(). 

    def Amp_less_5_QC(self, ):
        

