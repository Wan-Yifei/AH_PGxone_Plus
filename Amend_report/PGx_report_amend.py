#To do: Can handle empty filed
#To do: remove dulplicate drugs or ICD codes
#To do: can handle multiple amending, e.g. ICD + address. --> add to bash: Amend_list_Check.sh

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

def Update(Run_folder, ID, Type, Med_added, ICD_added):
	print('test')
	accession_new = ''
	## Update required filed of sample
	with open('%s/sample_codes_drugs_accession.txt'%Run_folder, 'r') as accession: 
		print(accession)
		accession_ori = accession.readlines()
		for sample in accession_ori:
			line = sample.strip().split('\t')
			if line[0] == ID:
				print(line)
				if Type == 'Medication':
					line[2] = line[2] + ', ' + Med_added
				elif Type == 'ICD':
					line[1] = line[1] + ', ' + ICD_added
				elif Type == 'Both':
					line[1] = line[1] + ', ' + ICD_added
					line[2] = line[2] + ', ' + Med_added
				else:
					print('The {} of {} has been updated, please check!'.format(Type, ID))
				line = '\t'.join(line) + '\n'
				accession_new += line
			else:
				line = '\t'.join(line) + '\n'
				accession_new += line 
	## Save new accession file
	with open('%s/sample_codes_drugs_accession.txt'%Run_folder, 'w') as accession: 
		accession.writelines(accession_new)

# 3. Main function

def Main():
	args = ParseArg()
	Run_folder = args.Run_folder
	ID = args.ID
	Type = args.Type
	ICD_added = args.I
	Med_added = args.M
	Update(Run_folder, ID, Type, Med_added, ICD_added)

# 4. Run script

if __name__ == '__main__':
	Main()
