## cheange own group of files
import os
import sys
import grp

runfolder = '/data/CLIA-Data/PGxOne_V3/Production/BI_Data_Analysis/' + sys.argv[1]
gid = grp.getgrnam('CLIA').gr_gid

## 1. change group of DDI
os.chown(runfolder + '/DDI/', -1, gid)
os.chown(runfolder + '/LIS/', -1, gid)
os.chown(runfolder + '/Plus/', -1, gid)

for root, dirs, files in os.walk(runfolder + '/DDI'):  
    for f in files:  
        os.chown(os.path.join(root, f), -1, gid)


for root, dirs, files in os.walk(runfolder + '/LIS'):  
    for f in files:  
        os.chown(os.path.join(root, f), -1, gid)

for root, dirs, files in os.walk(runfolder + '/Plus'):  
    for f in files:  
        os.chown(os.path.join(root, f), -1, gid)
