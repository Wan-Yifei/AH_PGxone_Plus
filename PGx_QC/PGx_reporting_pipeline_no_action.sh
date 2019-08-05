#! /bin/bash

# @author: Yifei Wan

# ==========================================================================
# 05/06/2019
# 
# This pipeline accepts the name of run folder then deleles failed sample an# d un-resolved samples. Finally it would upload actions files to xifin.
# ==========================================================================
# 05/23/2019
#
# Add NY check.
# ==========================================================================

set -e

RUNFOLDER=$1
QC_list=$2
python column_verify.py $RUNFOLDER
python3 /home/yifei.wan/AH_Project/PGx_QC/PGx_Delete.py $RUNFOLDER $QC_list
python3 /home/yifei.wan/AH_Project/PGx_QC/PGx_Delete_no_action.py $RUNFOLDER $QC_list
echo
echo ====================================================
python /home/yifei.wan/AH_Project/PGx_NY/PGx_NY.py $RUNFOLDER
echo
echo ====================================================
python /data/AmendReports/Script/check_release.py $RUNFOLDER
python /data/AmendReports/Script/check_release_no_action.py $RUNFOLDER
echo
echo ====================================================
bash /home/yifei.wan/AH_Project/PGx_App/PGxOne_APP_mover_no_action.sh $RUNFOLDER

