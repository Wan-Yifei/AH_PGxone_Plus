## This script is uitilized to check which samples are not included in the LIS folder.

import os
import sys

path = '/data/CLIA-Data/PGxOne_V3/Production/BI_Data_Analysis/' + sys.argv[1]
plus =  path + '/Plus'

with open(path + '/sample_codes_drugs.txt', 'r') as sc:
    sample_code = sc.readlines()
    samples = [sample.strip().split('\t')[0] for sample in sample_code]

action_files = [f.split('_')[0] for f in os.listdir(plus)]
action_files_miss = [f for f in action_files if f not in samples and 'NA' not in f]

print('Miss samples: %s'%action_files_miss)

