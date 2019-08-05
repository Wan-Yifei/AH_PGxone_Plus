#! /bin/bash

# @author: Yifei Wan

# ======================================================================
# 04/02/2019	Basic version 0.0.1
# Feat: 
# Copy action files from spcified LIS folder to PGxOne_App folder.
#
# **Input Argument**
# 1. the name of run folder.
# ======================================================================
# 04/03/2019	Basic version 0.0.2
# Feat:
# Redirect output and batch upload
#
# 1. Replace mv to cp;
# 2. Add batch uploading;
# 3. Redirect standard output and error message to both console and file.
# ======================================================================
# 04/19/2019	Basic version 0.1.0
# Feat: 
# Check and upload resolved action files
#
# 1. move action files in the resolved folder;
# 2. clear files in the resolved folder.
# ======================================================================
# 04/22/2019	Basic version 0.1.1
# Feat:
#
# 1. Echo "Release folder is empty!" when folder does not have any files.
# ======================================================================
# 04/22/2019	Basic version 0.1.2
# Fix:
#
# 1. Add echo function to accept error when rm meets empty folder.
# ======================================================================
# 07/19/2019	Basic version 0.1.3
# Feat:
#
# 1. Add date to log files.
# ======================================================================
set -e

RUNFOLDER=$1
LISFOLDER=/data/CLIA-Data/PGxOne_V3/Production/BI_Data_Analysis/$RUNFOLDER/LIS
LISFOLDER_NO=/data/CLIA-Data/PGxOne_V3/Production/BI_Data_Analysis/$RUNFOLDER/LIS_no_action
APPFOLDER='/data/CLIA-Data/PGxOne_APP'
BATCHUPLOAD='/xifin/result-data/'
RELEASE='/data/CLIA-Data/PGx_Resolved/Release'
RELEASE_NO='/data/CLIA-Data/PGx_Resolved/Release_no_action'

echo >> /data/AmendReports/Script/PGx_APP_log/PGxOne_APP_log.txt
echo >> /data/AmendReports/Script/PGx_APP_log/PGxOne_UPLOAD_log.txt
echo `date` >> /data/AmendReports/Script/PGx_APP_log/PGxOne_APP_log.txt
echo `date` >> /data/AmendReports/Script/PGx_APP_log/PGxOne_UPLOAD_log.txt

## Upload to APP
cp -v $LISFOLDER/*.txt $APPFOLDER/ > >(tee -a /data/AmendReports/Script/PGx_APP_log/PGxOne_APP_log.txt) 2> >(tee -a /data/AmendReports/Script/PGx_APP_log/PGxOne_APP_err.log >&2)
{
	cp -v $RELEASE/*.txt $APPFOLDER/ > >(tee -a /data/AmendReports/Script/PGx_APP_log/PGxOne_APP_log.txt) 2> >(tee -a /data/AmendReports/Script/PGx_APP_log/PGxOne_APP_err.log >&2)
} || {
	echo Release folder is empty!
}

## Upload to LIS
read -p "Input any key to initial batch uploading:"
cp -v $LISFOLDER_NO/*.txt $BATCHUPLOAD/ > >(tee -a /data/AmendReports/Script/PGx_APP_log/PGxOne_UPLOAD_log.txt) 2> >(tee -a /data/AmendReports/Script/PGx_APP_log/PGxOne_UPLOAD_err.txt >&2)
{
	cp -v $RELEASE_NO/*.txt $BATCHUPLOAD/ > >(tee -a /data/AmendReports/Script/PGx_APP_log/PGxOne_UPLOAD_log.txt) 2> >(tee -a /data/AmendReports/Script/PGx_APP_log/PGxOne_UPLOAD_err.txt >&2)
} || {
	echo Release_no_action folder is empty!
}

{
	rm -v  $RELEASE/*
} || {
	echo There is no resolved sample!
}

{
	rm -v  $RELEASE_NO/*
} || {
	echo There is no resolved no action sample!
}
