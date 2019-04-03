#! /bin/bash

# @author: Yifei Wan

# ======================================================================
# 04/02/2019	Basic version 0.0.1
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

set -e

RUNFOLDER=$1
LISFOLDER=/data/CLIA-Data/PGxOne_V3/Production/BI_Data_Analysis/$RUNFOLDER/LIS
APPFOLDER='/data/CLIA-Data/PGxOne_APP'
BATCHUPLOAD='/xifin/result-data/'

echo >> PGxOne_App_log.txt
echo >> PGxOne_UPLOAD_log.txt
cp -v $LISFOLDER/*.txt $APPFOLDER/ > >(tee -a PGxOne_APP_log.log) 2> >(tee -a PGxOne_APP_err.log >&2)
read -p "Input any key to initial batch uploading:"
cp -v $LISFOLDER/*.txt $BATCHUPLOAD/ > >(tee -a PGxOne_UPLOAD_log.txt) 2> >(tee -a PGxOne_UPLOAD_log.txt >&2)

