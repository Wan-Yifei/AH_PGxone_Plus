#!/usr/bin/python2

# author: Yifei

# Select and move samples from NY.

import os
import sys


# Run folder
runfolder = sys.argv[1]

accession_file = '/data/AmendReports/Resolved_list/CSVFile.csv'
samples_ids = '/data/CLIA-Data/PGxOne_V3/Production/BI_Data_Analysis/%s/sample_codes_drugs.txt' % runfolder

output_log = '/data/CLIA-Data/PGxOne_NYHotel/logs/'
output_folder = '/data/CLIA-Data/PGxOne_NYHotel/'

# Dose CSVFile exist?
if not os.access(accession_file, os.F_OK):
    raise IOError('CSV file does not exist!')

# Identify NY samples
with open(samples_ids, 'r') as ids, open(accession_file, 'r') as accession:
    case_ids = [case.strip().split('\t')[3] for case in ids.readlines()]
    NY_ids = ({sample.strip().split(',')[2] : sample.strip().split(',')[3] for sample in accession.readlines()
                if sample.strip().split(',')[2] in case_ids and 
                'NY Hotel' in sample.strip().split(',')[1]})

if not NY_ids:
    print ' Cannot find any NY samples!'
    quit()

with open(output_log + 'processed_log.txt', 'a+') as logging, open(output_log + 'NY_list.txt', 'a+') as id_list:
    ids = id_list.readlines()
    for action in NY_ids.keys():
        print 'Copy ' + action + '/' + NY_ids[action]
        os.system('cp /data/CLIA-Data/PGxOne_V3/Production/BI_Data_Analysis/%s/LIS/%s.txt %s' 
        % (runfolder, action, output_folder + '/' + NY_ids[action] + '.txt'))
        ## chage user group
        os.system('chgrp CLIA /data/CLIA-Data/PGxOne_V3/Production/BI_Data_Analysis/%s/LIS/%s.txt %s' 
        % (runfolder, action, output_folder + '/' + NY_ids[action] + '.txt'))
        print >> logging, action + '/' + NY_ids[action]
        if action + '\n' not in ids:
            print >> id_list, action
