##################################################################################################
# 2/20/2019    Basic version 0.0.1
#
# VCFtoAnnoTSV.py
# Filter the vcf to txt for OncoGxV2.
#
# Contribution:
# @author: Dr. Cai Chen
# @maintain: Yifei Wan
#
# Summary:
# 1.Add filters for AF, CAF and TOPMED;
# 2. Refactor the main function.
#
# **Input file**
# %ID_eff_clinvar_dbnsfp.vcf
#
# **Output file**
# 1. %ID.anno.txt
# 2. %ID.Indel_HLA.txt
##################################################################################################
# 2/21/2019 Basic version 0.0.2
#
# Feat:
# 1. Pass when feature doesn't exit;
# 2. Try to filter TOPMED and CAF when ref larger than (1 - population frequency).
##################################################################################################
# 2/22/2019 Basic version 0.0.3
# 
# Feat:
# 1. Check rs ID and COSMIC ID;
# 2. Update pop_freq as 0.002.
##################################################################################################
# 2/23/2019 Basic version 0.0.4
# 
# Fix:
# Finding "_AF" failed. Apply str.endswith() to find keys ending with "AF".
##################################################################################################
# 2/24/2019 Basic version 0.1.0
#
# Feat:
# 1. Update the function of COSMIC_filter(): consider effect of mutation.
##################################################################################################
# 2/25/2019 Basic version 0.2.0
# 
# Feat:
# 1. Update conditions of COSMIC_filter();
# 2. Redirect the output: output the mutation having COSMIC and RS to the review txt file.
##################################################################################################
# 2/26/2019 Basic version 0.2.1
# 
# Feat:
# 1. Update the COSMIC_filter: When RS and COSMIC exist, check the effect of mutation.
##################################################################################################
# 3/4/2019 Basic version 0.3.0
#
# Feat:
# 1. COSMIC API: query COSMIC website;
# 2. Add Indel check to cosmic filter;
# 3. Apply stricter pop_fre for mutation with cosmic & rs & synonymous;
# 4. Add HLA filter;
# 5. Move indel and HLA alternates to Indel_HLA.txt
##################################################################################################
# 3/11/2019 Basic version 0.3.1
# 
# Fix:
# 1. Check flag before cal API.
##################################################################################################
# 3/17/2019 Basic version 1.0.0
#
# Ref:
# 1. Restructure the decesion tree for the somatic mutation;
# 2. Encapsulate the alternate from VCF as a class;
# 3. Cancel the review.txt.
##################################################################################################
# 3/17/2019 Basic version 1.0.1
#
# Fix:
# 1. Fix the typo of attribute.
##################################################################################################
# 3/18/2019 Basic version 1.1.1
#
# Feat:
# 1. Add the AC filter;
# 2. Call AF check functioni only when it has at least 5 support cases.
##################################################################################################

import sys, subprocess, argparse, os, re, json, time, copy 
sys.path.append("/home/pengfei.yu/OncoGxOne/pipeline")
from VCFmodules.VCFutility import *
from VCFmodules.SnpEff import *
from ClinAccToMutationName import *
from urllib2 import Request, urlopen, HTTPError

general_header = ["CHROM", "POS", "ID", "REF", "ALT"]
CLN_header = ["CLNACC", "CLNSIG","CLNSRC","CLNSRCID","CLNDBN","CLNDSDB","CLNDSDBID"]
dbNSFP_header = "rs_dbSNP141,Uniprot_acc,Uniprot_id,Uniprot_aapos,Interpro_domain,refcodon,codonpos,Ensembl_geneid,Ensembl_transcriptid,aapos,1000Gp1_AC,1000Gp1_AF,1000Gp1_AFR_AC,1000Gp1_AFR_AF,1000Gp1_EUR_AC,1000Gp1_EUR_AF,1000Gp1_AMR_AC,1000Gp1_AMR_AF,1000Gp1_ASN_AC,1000Gp1_ASN_AF,ESP6500_AA_AF,ESP6500_EA_AF,ExAC_AC,ExAC_AF,ExAC_Adj_AC,ExAC_Adj_AF,COSMIC_ID,COSMIC_CNT"
dbNSFP_header = dbNSFP_header.split(",")
Sample_header = ["DP","FREQ","GT"]
SnpEff_header = ['AA_change', 'c_change', 'Effect', 'Effect_Impact', 'Exon_Rank', 'Functional_Class', 'Gene_Name', 'Transcript_BioType', 'Transcript_ID']
header_line = "#"+"\t".join(general_header + Sample_header + ["SnpEff."+x for x in SnpEff_header]
							+ ["ClinVar."+x for x in CLN_header] + ["dbNSFP."+x for x in dbNSFP_header])
Comments='''
##FORMAT=<ID=DP,Number=1,Type=Integer,Description="Read Depth">
##FORMAT=<ID=FREQ,Number=1,Type=String,Description="Variant allele frequency">
##FORMAT=<ID=GT,Number=1,Type=String,Description="Genotype">
##INFO=<ID=CLNACC,Number=.,Type=String,Description="Variant Accession and Versions">
##INFO=<ID=CLNSIG,Number=.,Type=String,Description="Variant Clinical Significance, 0 - Uncertain significance, 1 - not provided, 2 - Benign, 3 - Likely benign, 4 - Likely pathogenic, 5 - Pathogenic, 6 - drug response, 7 - histocompatibility, 255 - other">
##INFO=<ID=CLNSRC,Number=.,Type=String,Description="Variant Clinical Chanels">
##INFO=<ID=CLNSRCID,Number=.,Type=String,Description="Variant Clinical Channel IDs">
##INFO=<ID=CLNDBN,Number=.,Type=String,Description="Variant disease name">
##INFO=<ID=CLNDSDB,Number=.,Type=String,Description="Variant disease database name">
##INFO=<ID=CLNDSDBID,Number=.,Type=String,Description="Variant disease database ID">
##INFO=<ID=dbNSFP_rs_dbSNP141,Number=A,Type=String,Description="rs number from dbSNP 141">
##INFO=<ID=dbNSFP_Uniprot_aapos,Number=A,Type=Integer,Description="amino acid position as to Uniprot. Multiple entries separated by '|'">
##INFO=<ID=dbNSFP_Uniprot_acc,Number=A,Type=String,Description="Uniprot accession number. Multiple entries separated by '|'">
##INFO=<ID=dbNSFP_Uniprot_id,Number=A,Type=String,Description="Uniprot ID number. Multiple entries separated by '|'">
##INFO=<ID=dbNSFP_Interpro_domain,Number=A,Type=String,Description="domain or conserved site on which the variant locates. Domain annotations come from Interpro database. The number in the brackets following a specific domain is the count of times Interpro assigns the variant position to that domain, typically coming from different predicting databases.">
##INFO=<ID=dbNSFP_refcodon,Number=A,Type=String,Description="reference codon">
##INFO=<ID=dbNSFP_aapos,Number=A,Type=Integer,Description="amino acid position as to the protein.">
##INFO=<ID=dbNSFP_codonpos,Number=A,Type=Integer,Description="position on the codon (1, 2 or 3)">
##INFO=<ID=dbNSFP_Ensembl_geneid,Number=A,Type=String,Description="Ensembl gene id">
##INFO=<ID=dbNSFP_Ensembl_transcriptid,Number=A,Type=String,Description="Ensembl transcript ids (separated by '|')">
##INFO=<ID=dbNSFP_1000Gp1_AC,Number=A,Type=Integer,Description="Alternative allele counts in the whole 1000 genomes phase 1 (1000Gp1) data.">
##INFO=<ID=dbNSFP_1000Gp1_AF,Number=A,Type=Float,Description="Alternative allele frequency in the whole 1000Gp1 data">
##INFO=<ID=dbNSFP_1000Gp1_AFR_AC,Number=A,Type=Integer,Description="Alternative allele counts in the 1000Gp1 African descendent samples">
##INFO=<ID=dbNSFP_1000Gp1_AFR_AF,Number=A,Type=Float,Description="Alternative allele frequency in the 1000Gp1 African descendent samples">
##INFO=<ID=dbNSFP_1000Gp1_AMR_AC,Number=A,Type=Integer,Description="Alternative allele counts in the 1000Gp1 American descendent samples">
##INFO=<ID=dbNSFP_1000Gp1_AMR_AF,Number=A,Type=Float,Description="Alternative allele frequency in the 1000Gp1 American descendent samples">
##INFO=<ID=dbNSFP_1000Gp1_ASN_AC,Number=A,Type=Integer,Description="Alternative allele counts in the 1000Gp1 Asian descendent samples">
##INFO=<ID=dbNSFP_1000Gp1_ASN_AF,Number=A,Type=Float,Description="Alternative allele frequency in the 1000Gp1 Asian descendent samples">
##INFO=<ID=dbNSFP_1000Gp1_EUR_AC,Number=A,Type=Integer,Description="Alternative allele counts in the 1000Gp1 European descendent samples">
##INFO=<ID=dbNSFP_1000Gp1_EUR_AF,Number=A,Type=Float,Description="Alternative allele frequency in the 1000Gp1 European descendent samples">
##INFO=<ID=dbNSFP_ESP6500_AA_AF,Number=A,Type=Float,Description="Alternative allele frequency in the Afrian American samples of the NHLBI GO Exome Sequencing Project (ESP6500 data set)">
##INFO=<ID=dbNSFP_ESP6500_EA_AF,Number=A,Type=Float,Description="Alternative allele frequency in the European American samples of the NHLBI GO Exome Sequencing Project (ESP6500 data set)">
##INFO=<ID=dbNSFP_ExAC_AC,Number=A,Type=Integer,Description="Allele count in total ExAC samples (~60,706 unrelated individuals)">
##INFO=<ID=dbNSFP_ExAC_Adj_AC,Number=A,Type=Integer,Description="Adjusted Alt allele counts (DP >= 10 & GQ >= 20) in total ExAC samples">
##INFO=<ID=dbNSFP_ExAC_Adj_AF,Number=A,Type=Float,Description="Adjusted Alt allele frequency (DP >= 10 & GQ >= 20) in total ExAC samples">
##INFO=<ID=dbNSFP_ExAC_AF,Number=A,Type=Float,Description="Allele frequency in total ExAC samples">
##INFO=<ID=dbNSFP_COSMIC_CNT,Number=A,Type=Integer,Description="number of samples having this SNV in the COSMIC database">
##INFO=<ID=dbNSFP_COSMIC_ID,Number=A,Type=String,Description="ID of the SNV at the COSMIC (Catalogue Of Somatic Mutations In Cancer) database">
##INFO=<ID=OncoGxKB_id,Number=A,Type=String,Description="ID of the variant at Admera's OncoGxKB database (https://agis.admerahealth.com/OncoGxKB)">
'''



##INFO=<ID=CAF,Number=.,Type=String,Description="An ordered, comma delimited list of allele frequencies based on 1000Genomes, starting with the reference allele followed by alternate alleles as ordered in the ALT column. Where a 1000Geno


def getInfo(Dict, key):
	if key in Dict:
		if type(Dict[key]) == list:
			return "|".join(str(f) for f in Dict[key])
		return Dict[key]
	else:
		return "."

def MutationsFromVCF(sample, output, Indel_HLA_output, request_variant_list, pop_freq, strict_freq, strict_freq2, strict_freq3):
	'''  extract actionable mutations from VCF '''
	mutations={}
	pathogenic_mutations=[]
	## Filter
	for v in sample:
		if v.QUAL<min_qual: continue


	## Test block 
		#print v.__dict__
		#print '%s, %s'%(v.__dict__['CHROM'], v.__dict__['POS'])
		#print '%s, %s, %s, %s'%(flag_AF, flag_CAF, flag_TOPMED, flag_COSMIC)
		#print v.__dict__['ID']
		#print not(all([flag_AF, flag_CAF, flag_TOPMED, flag_COSMIC]))
		#print [flag_AF, flag_CAF, flag_TOPMED, flag_COSMIC]
		#print not(all([flag_AF, flag_CAF, flag_TOPMED]))

		if set(['AD', 'AF']) < set(v.samples[0].keys()) and 'DP' not in v.samples[0].keys():
			depth = sum(v.samples[0]['AD'])  #MuTect2
			freq = v.samples[0]['AF'][0]	#MuTect2
			GT = v.samples[0]['GT']
		else:
			try:
				depth = v.samples[-1]['DP'][0]
			except:
				depth = v.INFO['DP']

			try:
				freq = float(v.samples[-1]['FREQ'].strip('%'))/100	# VarScan
			except:
				try:
					AD = v.samples[-1]['AD']  # GATK
					if depth<1: continue  
					freq = AD[1]*1.0/depth
				except:
					freq = v.samples[-1]['VF'] # somaticVariant Caller
			GT = v.samples[-1]['GT']
		if depth<min_depth: continue
		if freq > max_freq: continue
		if freq < min_freq: continue

##################################################################################################
########################          COSMIC mutation decesion tree          #########################
##################################################################################################

		## Initial an instant of Alternate class 
		print '\n'
		print '\n'
		print '\n'
		alternate = Alternate(v, pop_freq, strict_freq, strict_freq2, strict_freq3)
		## 1.
		#alternate.Show(pop_freq) ## show test result

		if not(all([alternate.AF_filter(alternate.AC_filter(), pop_freq), alternate.CAF_filter(pop_freq), alternate.TOPMED_filter(pop_freq)])):
			print 'continue'
			continue
		## 2.0
		if 'COSM' in alternate.ID:
			## 2.1
			if not alternate.Call_COSMIC_API(): continue
			## 2.2
			if 'rs' in alternate.ID:
				## 2.2.1
				if alternate.Eff_Check():
					## 2.2.1.1
					if not alternate.Strict_filter(strict_freq):
						continue
					## 2.2.1.1.1
					else:
						flag_output = alternate.Output_direct() 
				else:
					## 2.2.1.2
					if not alternate.Strict_filter(strict_freq2):
						contine
					else:
						## 2.2.1.2.1
						flag_output = alternate.Output_direct()
			else:
				## 2.2.2
				flag_output = alternate.Output_direct()
		else:
			## 2.3
			if 'rs' in alternate.ID:
				## 2.3.1
				if alternate.Eff_Check():
					## 2.3.1.1
					if not alternate.Strict_filter(strict_freq3):
						continue
					else:
						flag_output = alternate.Output_direct() 
				else:
					## 2.3.1.2
					if not alternate.Strict_filter(strict_freq2):
						continue
					else:
						flag_output = alternate.Output_direct()
			else:
				## 2.3.2
				if alternate.Eff_Check():
					flag_output = 'Indel_HLA' 
				else:
					flag_output = alternate.Output_direct()

##################################################################################################
		#print v.__dict__['ID']
		GT_convert = {'0/1':'HET', "1/1":'HOM', '0/0': "NONE"}
		general_info = [getattr(v, h) for h in general_header]
		CLN_info = [getInfo(v.INFO, h) for h in CLN_header]
		dbNSFP_info = [getInfo(v.INFO, "dbNSFP_"+h) for h in dbNSFP_header]
		Sample_info = [depth, freq, GT_convert[GT]]
		mutation_eff = EFF(v.INFO["EFF"].split(",")[0])

		if mutation_eff.AA_change==None:
			mutation_eff.AA_change = "."
		
		SnpEff_info = [getattr(mutation_eff, h) for h in SnpEff_header]
		## merge results
		result_line = "\t".join(str(f) for f in general_info + Sample_info + SnpEff_info + CLN_info + dbNSFP_info)
		if "." in mutation_eff.Mutation_Name:
			OncoGxKB_id = "."
		elif mutation_eff.Mutation_Name.replace("-"," / ") in request_variant_list:
			OncoGxKB_id = mutation_eff.Mutation_Name.replace("-"," / ")
		else:
			OncoGxKB_id = "."

		## Output review required mutations
		print flag_output
		if flag_output == 'Indel_HLA':
			print >> Indel_HLA_output, result_line + '\t' + OncoGxKB_id
		else:
			print >>output, result_line+"\t"+OncoGxKB_id

		if 'CLNACC' not in v.INFO and 'EFF' not in v.INFO: continue  
		#print v.__dict__['ID']
		if 'CLNACC' in v.INFO:
			variant=v.INFO["CLNACC"].split(",")[0].split(".")[0]
			try:
				mutation = mutation_translate(variant)
			except:
				continue
			if v.INFO["CLNSIG"].startswith("5") or v.INFO["CLNSIG"].startswith("255") or v.INFO["CLNSIG"].startswith("6"):
				pathogenic_mutations.append(variant+":"+mutation)
		else:
			if mutation_eff.AA_change==None: continue
			mutation=mutation_eff.Mutation_Name
		#print v.__dict__['ID']

		if mutation.endswith("="): continue  # bypass synonymous mutation
		#print v.__dict__['ID']
		Gene = mutation_eff.Gene_Name
		if len(v.REF)!=len(v.ALT) and Gene in ['EGFR','ERBB2']:  # check deletion or insertion on EGFR exons
			Gene = mutation_eff.Gene_Name
			Exon = str(mutation_eff.Exon_Rank)
			if len(v.REF)>len(v.ALT):
				Alt = "del"
			else:
				Alt = "ins"
			if Gene=='ERBB2' and Exon=='23' and ("NM_001005862.2" in mutation_eff.Transcript_ID): Exon="20"
			mutation = "%s-E%s_%s"%(Gene,Exon,Alt)
		mutations[mutation] = mutation_eff
	return mutations,pathogenic_mutations

##################################################################################################
# Main class: Alternate
# The Mutation is a class which is "derived" from  VCFmodule.
##################################################################################################

class Alternate():
	''' Initial extract content from VCFmodule object '''
	def __init__(self, variable, pop_freq, strict_freq, strict_freq2, strict_freq3):
		#print dir(variable)
		self.var = copy.deepcopy(variable)
		self.ID = copy.deepcopy(variable.ID)
		self.Show(pop_freq)

	def Show(self, pop_freq):
		print 'AC list      {}'.format(self.AC_filter())
		print 'AF check     {}'.format(self.AF_filter(self.AC_filter(), pop_freq))
		print 'CAF check    {}'.format(self.CAF_filter(pop_freq))
		print 'TOPMED check {}'.format(self.TOPMED_filter(pop_freq))

##################################################################################################

	def AC_filter(self, cases = 4):
		
		'''
		## Check the number of supported cases of alternate
		Only check the AF of alternate while it has as least 5 samples. 

		Input:
		1. self: a line form Record object (an iteration);

		Output: a boolean flag for ACs indicates whether check the AFs.
		'''
		keys = [key for key in self.var.__dict__['INFO'].keys() if key.endswith("_AC")]
		AC_count = {key.split('_AC')[0] : self.var.__dict__['INFO'][key][0] for key in keys if self.var.__dict__['INFO'][key][0] > cases}
		#print AC_count
		return AC_count


##################################################################################################

	def AF_filter(self, AC_count, pop_freq):

		'''
 ## Check the AF values of each allele ##
 If one value with suffix "AF" is less than population frequency, corresponding mutation should
 be removed from output txt file.

 Input:
 1. self: a line from Record object (an iteration);
 2. AC_count: the dictionary of available AC items; 
 2. pop_freq: the population frequence.

 Output: a boolean flag for AFs.
		'''
		keys = [key for key in self.var.__dict__['INFO'].keys() if key.endswith("_AF") and key.split('_AF')[0] in AC_count.keys()]
		#print keys
		if bool(keys):
			flag_AF = all([bool(float(self.var.__dict__['INFO'][key][0]) < pop_freq) for key in keys])
			#print 'judge_AF: {}'.format(flag_AF)
		else:
			flag_AF = True
		#self.AF = flag_AF
		return flag_AF

##################################################################################################

	def CAF_filter(self, pop_freq):

		'''
 ## Check the CAF values of each allele ##

 Input:
 1. self: a line from Record object (an iteration) which is initialed as an instant;
 2. pop_freq: the population frequence;

 Output: a boolean flag for CAF.
		'''
		try:
			if self.var.__dict__['INFO']['CAF'].split(',')[0].replace('.', "").isdigit():
				flag_CAF = bool(float(self.var.__dict__['INFO']['CAF'].split(',')[0]) > 1 - pop_freq)
		except:
			flag_CAF = True
		#self.CAF = flag_CAF
		#print 'object CAF1    {}'.format(id(self.CAF))
		return flag_CAF

##################################################################################################

	def TOPMED_filter(self, pop_freq):

		'''
## Check the TOPMED values of each allele ##

 Input:
 1. self: a line from Record object (an iteration) which is initialed as an instant;
 2. pop_freq: the population frequence;

 Output: a boolean flag for TOPMED.
		'''
		try:
			if self.var.__dict__['INFO']['TOPMED'].split(',')[0].replace('.', "").isdigit():
				flag_TOPMED = bool(float(self.var.__dict__['INFO']['TOPMED'].split(',')[0]) > float(1 - pop_freq))
		except:
			flag_TOPMED = True
		#self.TOPMED = flag_TOPMED
		#print 'object TOPMED   {}'.format(id(self.TOPMED))
		return flag_TOPMED

##################################################################################################

	def COSMIC_API(self):

		'''
 ## COSMIC websit API ##
 Visit COSMIC websit to check the real-time data of mutation.

 Input:
 1. self instant;
 2. hold: sleep time to avoid visiting website too frequent.
		'''
		COSMIC_ID = self.ID.split(';')[-1].replace('COSM', '')
		print COSMIC_ID
		## url of COSMIC website
		url = 'https://cancer.sanger.ac.uk/cosmic/mutation/overview?id='
		## pass ID to url
		url_ID = '%s%s'%(url, COSMIC_ID)
		#print url_ID
		## generte request
		request = Request(url_ID)
		## open url
		response = urlopen(request)
		page = response.read()

		if 'flagged as a SNP' in page or  'was not found in our database' in page:
			flag_online = True 
		else:
			flag_online = False 
		print 'API %s'%flag_online
		return flag_online

	def Call_COSMIC_API(self):

		''' Call API with time limit '''
		try:
			return self.COSMIC_API()
		except HTTPError, e:
			if e.code == 429:
				time.sleep(5)
				return self.Call_COSMIC_API()
			raise


##################################################################################################

	def Eff_Check(self):

		'''
 ## Check the synonymous_variant ##

 Input:
 1. self: instant. 
		'''
		#print self.var.__dict__['INFO']
		effect = self.var.__dict__['INFO']['EFF']
		if 'synonymous_variant' in effect:
			flag_eff = True
		else:
			flag_eff = False 
		#self.effect =  flag_eff
		return flag_eff

##################################################################################################

	def Indel_Check(self):

		'''
 Indle check
 Check is this mutation an indel.
 
 Input:
 1. self: instant. 
		'''
		## bases on reference
		ref = self.var.__dict__['REF']
		alt = self.var.__dict__['ALT']

		## is this an idel?
		if len(ref) != len(alt):
			flag_indel = True
		else:
			flag_indel = False
		#self.Indel = flag_indel
		return flag_indel

##################################################################################################

	def HLA_Check(self):

		'''
 ##  HLA check ##
 Check is this mutation a HLA.

 Input:
 1. self: instant.
		'''
		try:
			if 'HLA' in self.var.__dict__['INFO']['LOF']:
				flag_HLA = True
			else:
				flag_HLA = False
		except:
			flag_HLA = False
		#self.HLA = flag_HLA
		return flag_HLA

##################################################################################################

	def Output_direct(self):

		'''
 ## Redirect the output ##
		'''

		if self.Indel_Check() or self.HLA_Check():
			flag_output = 'Indel_HLA'
		else:
			flag_output = 'Action'
		self.output = flag_output
		return flag_output

##################################################################################################

	def Strict_filter(self, strict_freq):

		'''
 ##  Apply stricter threshold ##

 Input:
 1. self: instant;
 2. strict threshold: strict frequence.
		'''
		try:
			CAF_filter(self, strict_freq)
		except:
			self.CAF = True
		try:
			self.TOPMED = TOPMED_filter(self, strict_freq)
		except:
			self.TOPMED = True
		if self.CAF and self.TOPMED:
			flag_strict = True
		else:
			flag_strict = False
		return flag_strict



##################################################################################################
# Main function
##################################################################################################

def main():
	## Receive VCF from argument 
	vcf_file = sys.argv[1]
	output_path = vcf_file.replace("_eff_clinvar_dbnsfp.vcf", ".anno.txt") 
	Indel_HLA_path = vcf_file.replace("_eff_clinvar_dbnsfp.vcf", ".Indel_HLA.txt")

	## Log in OncoGxKB
	user_file = open("/home/pengfei.yu/API_user.txt","r")
	user_info = user_file.read().split("\n")[0]
	username = user_info.split("\t")[0]
	password = user_info.split("\t")[1]
	headers = {
	  'Accept': 'application/json'
	}
	request = Request('https://agis.admerahealth.com/OncoGxKB/default/user/jwt?username=%s&password=%s'%(username,password), headers=headers)
	data = urlopen(request).read()
	TOKEN = json.loads(data)["token"]

	headers2 = {
	  'Accept': 'application/json',
	  'Authorization':'Bearer %s'%TOKEN
	}
	
	## Request OncoGxKB
	request = Request("https://agis.admerahealth.com/OncoGxKB/api/api/Variant", headers=headers2)
	response_body = urlopen(request).read()
	request_variant_list = json.loads(response_body)

	## Output results
	with open(vcf_file,"r") as File, open(output_path, 'w') as output, open(Indel_HLA_path, 'w') as Indel_HLA_output:
		vcf = VCFReader(File)
		print >>output, Comments.strip()
		print >>output, header_line+"\tOncoGxKB_id"
		point_result, patho_result = MutationsFromVCF(vcf, output, Indel_HLA_output, request_variant_list, pop_freq, strict_freq, strict_freq2, strict_freq3 )
 
##################################################################################################
##################################################################################################

# Run script

start = time.time()

if __name__ == '__main__':
	min_depth= 20
	min_qual = 35
	min_freq = 0.02
	max_freq = 0.90
	pop_freq = 0.002
	strict_freq = 4e-4
	strict_freq2 = 0.001
	strict_freq3 = 2e-5
	main()

end = time.time()
print 'Time elapsed %8.2f'%(end - start)
