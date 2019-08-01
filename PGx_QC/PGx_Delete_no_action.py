import sys
import argparse
import os

def ParseArg():

    p = argparse.ArgumentParser(description = 'Automatically remove failed samples from LIS folder')
    p.add_argument('Run_Name', type = str, help = 'Full name of run folder')
    p.add_argument('Falied_SampleList', type = str, help = 'File name of QC result')
    if len(sys.argv) == 1:
        sys.stderr.write(p.print_help())
        sys.exit(0)
    return p.parse_args()

args = ParseArg()
Run_name = args.Run_Name
QC_result = args.Falied_SampleList

Run_folder = '/data/CLIA-Data/PGxOne_V3/Production/BI_Data_Analysis/%s'%Run_name  

with open('%s/sample_codes_drugs.txt'%Run_folder) as Records:
    samples = Records.readlines()

with open(QC_result) as Del_list:
    samples_del = Del_list.readlines()

ReqID_CaseID = {sample.strip().split('\t')[0]:sample.strip().split('\t')[3] for sample in samples if 'SampleID' not in sample.strip().split('\t')[0]}
CaseID_Del = [ReqID_del.strip() for ReqID_del in samples_del if 'A-' in ReqID_del or 'RM-' in ReqID_del]

#print(CaseID_Del)

if CaseID_Del and not ReqID_CaseID: raise IOError('Check QC list, action files cannot be found!')
if not CaseID_Del and ReqID_CaseID: raise IOError('Check QC list, some unexpected action files are found!')

n = 1 ## Deleted sample count
for sample in CaseID_Del:
    #if sample in ReqID_CaseID.keys():
    try:
        CaseID = ReqID_CaseID[sample]
    except:
        raise IOError('Cannot find sample ID in run folder, please check!')   
    try:
        os.remove('{}/LIS_no_action/{}.txt'.format(Run_folder,CaseID))
        print('{}.Action file: {}/{} has been deleted!'.format(n, sample, CaseID))
        n += 1
    except:
        print('{}/{} cannot found!'.format(Run_folder, CaseID))
        raise IOError(CaseID + '.txt doesn\'t exit!!')

for sample in ReqID_CaseID.keys():
    if sample.startswith('RM'):
        CaseID = ReqID_CaseID[sample]
        if os.path.isfile('{}/LIS_no_action/{}.txt'.format(Run_folder,CaseID)): 
            os.remove('{}/LIS_no_action/{}.txt'.format(Run_folder,CaseID))
            print('{}.Action file: {}/{} has been deleted!'.format(n, sample, CaseID))
            n += 1
