#! /bin/bash

# @author: Yifei Wan

# ==================================================================
# 04/02/2019	Basic version 0.0.1
# Copy action files from spcified LIS folder to PGxOne_App folder.
#
# **Input Argument**
# 1. the name of run folder.
# ==================================================================

set -e

RUNFOLDER=$1
LISFOLDER=/data/CLIA-Data/PGxOne_V3/Production/BI_Data_Analysis/$RUNFOLDER/LIS
APPFOLDER='/data/CLIA-Data/PGxOne_APP'

mv -v $LISFOLDER/*.txt $APPFOLDER/ > PGxOne_APP_log.txt 2> PGxOne_APP_err.txt

