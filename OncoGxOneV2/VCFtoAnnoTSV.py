#To do: Question- when value doesn't exit, how to handle.
#To do: If AF has two values, use which one?


##################################################################################################
# 2/20/2019    Basic version 0.0.1
#
# VCFtoAnnoTSV.py
# Filter the vcf to txt for OncoGxV2.
#
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
# %ID.anno.txt
##################################################################################################

import sys, subprocess, argparse, os, re, json
sys.path.append("/home/pengfei.yu/OncoGxOne/pipeline")
from VCFmodules.VCFutility import *
from VCFmodules.SnpEff import *
from ClinAccToMutationName import *
from urllib2 import Request, urlopen


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

def MutationsFromVCF(sample, output, request_variant_list, pop_freq):
	'''  extract actionable mutations from VCF '''
	mutations={}
	pathogenic_mutations=[]
	## Filter
	for v in sample:
		if v.QUAL<min_qual: continue

	## Filter AF, CAF, TOPMED:
		try:
			flag_AF = AF_filter(v, pop_freq)
			flag_CAF = CAF_filter(v, pop_freq)
			flag_TOPMED = TOPMED_filter(v, pop_freq)
			if not(all([flag_AF, flag_CAF, flag_TOPMED])): continue
		except:
			continue

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
		print >>output, result_line+"\t"+OncoGxKB_id
		if 'CLNACC' not in v.INFO and 'EFF' not in v.INFO: continue		  
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

		if mutation.endswith("="): continue  # bypass synonymous mutation
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
# Check the AF values of each allele:
# If one value with suffix "AF" is less than population frequency, corresponding mutation should
# be removed from output txt file.
#
# Input:
# 1. variant: a line from Record object (an iteration);
# 2. pop_freq: the population frequence;
#
# Output: a boolean flag for AFs.
##################################################################################################

def AF_filter(variant, pop_freq):
	keys = [key for key in variant.__dict__['INFO'].keys() if '_AF' in key]
	#print '1.%s'%bool(keys)
	if bool(keys):
		flag_test = [float(variant.__dict__['INFO'][key][0]) for key in keys]
		#print flag_test
		flag_AF = all([bool(float(variant.__dict__['INFO'][key][0]) > pop_freq) for key in keys])
	else:
		flag_AF = bool(keys)
	#print '2.%s'%flag_AF
	return flag_AF

##################################################################################################
# Check the CAF values of each allele:
#
# Input:
# 1. variant: a line from Record object (an iteration);
# 2. pop_freq: the population frequence;
#
# Output: a boolean flag for CAF.
##################################################################################################

def CAF_filter(variant, pop_freq):
	if variant.__dict__['INFO']['CAF'].split(',')[1].replace('.', "").isdigit():
		flag_CAF = bool(float(variant.__dict__['INFO']['CAF'].split(',')[1]) > pop_freq)
	else:
		flag_CAF = False
	#print variant.__dict__['INFO']['CAF'].split(',')[1]
	#print flag_CAF
	return flag_CAF

##################################################################################################
# Check the TOPMED values of each allele:
#
# Input:
# 1. variant: a line from Record object (an iteration);
# 2. pop_freq: the population frequence;
#
# Output: a boolean flag for TOPMED.
##################################################################################################

def TOPMED_filter(variant, pop_freq):
	if variant.__dict__['INFO']['TOPMED'].split(',')[1].replace('.', "").isdigit():
		flag_TOPMED = bool(float(variant.__dict__['INFO']['TOPMED'].split(',')[1]) > pop_freq)
	else:
		flag_TOPMED = False
	#print variant.__dict__['INFO']['TOPMED'].split(',')[1]
	#print flag_TOPMED
	return flag_TOPMED


##################################################################################################
# Main function
##################################################################################################

def main():
	## Receive VCF from argument 
	vcf_file = sys.argv[1]

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
	with open(vcf_file,"r") as File:
		vcf = VCFReader(File)
		output_path = vcf_file.replace("_eff_clinvar_dbnsfp.vcf",".anno.txt") 
		output = open(output_path, 'w')
		print >>output, Comments.strip()
		print >>output, header_line+"\tOncoGxKB_id"
		point_result, patho_result = MutationsFromVCF(vcf, output, request_variant_list, pop_freq)
		output.close()
		File.close()
 
##################################################################################################
##################################################################################################

# Run script

if __name__ == '__main__':
	min_depth=20
	min_qual = 35
	min_freq = 0.02
	max_freq = 0.90
	pop_freq = 0.002
	main()

