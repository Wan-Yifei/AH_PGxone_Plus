# @author: Yifei Wan

# ================================================================================================
# 01/29/2019	Beta version 0.0.1
# Summary:
# The Python3 script PGx_report_amend.py updates sample information in accession file for each sample. 
# 
# Input: See ParseArg() function and find more details at the top of script: Amend_list_check.sh.
# Output: new sample codes_drugs_accession.txt for required samples.
# ================================================================================================
# 01/31/2019	Beta version 0.0.2
# Fix:
# Remove "\r" from new line when inserted content if too long.
# ================================================================================================

import argparse 
import sys

# 1. Parse arguments

def ParseArg():
	p = argparse.ArgumentParser(description = 'Amend report')
	p.add_argument("Run_folder", type=str, help="The path way of Run folder")
	p.add_argument("ID", type=str, help="The sample ID")
	p.add_argument("Type", type=str, help="which type of info is required to be amended")
	p.add_argument("-I", type=str, help="Added ICD codes")
	p.add_argument("-M", type=str, help="Added medications")
	if len(sys.argv) < 5 and '-h' not in sys.argv and '--help' not in sys.argv:
		sys.stderr.write(p.print_help())
		sys.exit(0)
	return p.parse_args()

# 2. Update info in accession file

def Update(Run_folder, ID, Type, Med_added = None, ICD_added = None):
	accession_new = ''
	## Update required filed of sample
	with open('/data/CLIA-Data/PGxOne_V3/Production/BI_Data_Analysis/%s/sample_codes_drugs_accession.txt'%Run_folder, 'r') as accession: 
		accession_ori = accession.readlines()
		for sample in accession_ori:
			line = sample.strip().split('\t')
			if line[0] == ID:
				#print(line)
				if 'Medication' in Type and 'ICD' in Type:
					#line[1] = line[1] + ', ' + ICD_added
					line[1] = ICD_added ## ICD required full list of ICD codes rather new ones.
					line[1] = line[1].replace('\r', '') ## ICD required full list of ICD codes rather new ones.
					line[2] = line[2] + ', ' + Med_added
					line[2] = ', '.join(set(line[2].strip(', ').split(', '))).replace('\r', '') ## remove additional space if original filed is empty and remove duplicate content
				elif 'ICD' in Type:
					#line[1] = line[1] + ', ' + ICD_added
					#line[1] = ', '.join(set(line[1].strip(', ').split(', ')))
					line[1] = ICD_added ## ICD required full list of ICD codes rather new ones.
					line[1] = line[1].replace('\r', '') ## ICD required full list of ICD codes rather new ones.
				elif 'Medication' in Type:
					#print(line[2])
					line[2] = line[2] + ', ' + Med_added
					line[2] = ', '.join(set(line[2].strip(', ').split(', '))).replace('\r', '')

				else:
					print('The {} of {} has been updated, please check!'.format(Type, ID))
				line = '\t'.join(line) + '\n'
				accession_new += line
			else:
				line = '\t'.join(line) + '\n'
				accession_new += line 
	## Save new accession file
	with open('/data/CLIA-Data/PGxOne_V3/Production/BI_Data_Analysis/%s/sample_codes_drugs_accession.txt'%Run_folder, 'w') as accession: 
		accession.writelines(accession_new)

# 3. Main function

def Main():
	args = ParseArg()
	Run_folder = args.Run_folder
	ID = args.ID
	ID = ID.strip()
	Type = args.Type
	Type = Type.strip()
	ICD_added = args.I
	if ICD_added:
		ICD_added = ICD_added.strip()
	Med_added = args.M
	if Med_added:
		Med_added = Med_added.strip()

	Update(Run_folder, ID, Type, Med_added, ICD_added)

# 4. Run script

if __name__ == '__main__':
	Main()
