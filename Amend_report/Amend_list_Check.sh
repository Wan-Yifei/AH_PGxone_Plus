#! /bin/bash

# @author Yifei Wan

# ===================================================================================================
# 01/29/2019	Beta version 0.0.1
# Summary:
# The bash script Amend_list_check.sh is use to automatically amend PGxOne reports.
#
# ** Input files**
# 1. Amend_request.txt: Accessioners input sample ID, amending content type and new added content.
#	1.1 For ICD: Input all ICD codes the sample having;
#	1.2 For MED: Input new medications or all medications of the sample, and use comma as delimiter;
#	1.3 For TYPE: Which kind of content requires amending? ICD? Medication? Address...
# 2. sample_codes_drugs.txt: Used to search CASE_ID of each sample.
#
# **Output files**
# 1. Amend_log.txt: Record all processed samples;
# 2. E-mail: This script would send reminder to Zhuosheng and Yifei.
#
# **Dependence**
# PGx_report_amend.py	Beta version 0.0.1
# ===================================================================================================

set -e
## message for Lab director
MESSAGE="Please resign with \"Update"

## Read amend requirement from require list
awk -F '\t' 'BEGIN {OFS = ";"} {if($1~/A-*/){print $1,$2,$3,$4}}' $1 | while IFS=';' read ID TYPE ICD MED 
do
## Find run folder based on ID
	find /data/CLIA-Data/PGxOne_V3/Production/BI_Data_Analysis/ -name "$ID*.vcf" | while read path
	do
		dirname $path >> tmp.txt
	done
	runfolder=$(sort -u -t_ -rk4 tmp.txt | head -n 1 | cut -d / -f7) ## pathway of run folder, select the newest folder
	run_index=$(echo $runfolder | cut -d _ -f4) ## e.g. Run700
	rm tmp.txt ## delet tmp
	echo -e
	echo ================================================================
	echo ================================================================
	echo -e
	echo Amend $ID from $runfolder
	echo -e

## Amend report
	if [ ! -z $runfolder ]
	then
		if [[ $TYPE == *"Medication"* && $TYPE == *"ICD"* ]]
		then
			echo cond1:Both
			python3 PGx_report_amend.py $runfolder $ID $TYPE -M "$MED" -I "$ICD"
			bash /home/yifei.wan/AH_PGxOne_Plus/PGx_Run/PGxOne_Scripts.sh $runfolder
			CASE_ID=$(awk -F"\t" -v ID=$ID '$1 == ID {print $4}' /data/CLIA-Data/PGxOne_V3/Production/BI_Data_Analysis/$runfolder/sample_codes_drugs.txt) ## find corresponding CASE ID based on requistion ID
			#echo /data/CLIA-Data/PGxOne_V3/Production/BI_Data_Analysis/$runfolder/LIS/$CASE_ID.txt
			cp /data/CLIA-Data/PGxOne_V3/Production/BI_Data_Analysis/$runfolder/LIS/$CASE_ID.txt /xifin/result-data/$CASE_ID.txt 
			sed -i "/$ID/d" $1 ## remove processed sample from request file
		elif [[ $TYPE == *"Medication"* ]]
		then
			echo cond2:Med
			python3 PGx_report_amend.py $runfolder $ID $TYPE -M "$MED"
			bash /home/yifei.wan/AH_PGxOne_Plus/PGx_Run/PGxOne_Scripts.sh $runfolder
			CASE_ID=$(awk -F"\t" -v ID=$ID '$1 == ID {print $4}' /data/CLIA-Data/PGxOne_V3/Production/BI_Data_Analysis/$runfolder/sample_codes_drugs.txt) ## find corresponding CASE ID based on requistion ID
			#echo /data/CLIA-Data/PGxOne_V3/Production/BI_Data_Analysis/$runfolder/LIS/$CASE_ID.txt
			cp /data/CLIA-Data/PGxOne_V3/Production/BI_Data_Analysis/$runfolder/LIS/$CASE_ID.txt /xifin/result-data/$CASE_ID.txt 
			sed -i "/$ID/d" $1 ## remove processed sample from request file
		elif [[ $TYPE == *"ICD"* ]]
		then
			echo cond3:ICD
			python3 PGx_report_amend.py $runfolder $ID $TYPE -I "$ICD"
			bash /home/yifei.wan/AH_PGxOne_Plus/PGx_Run/PGxOne_Scripts.sh $runfolder
			CASE_ID=$(awk -F"\t" -v ID=$ID '$1 == ID {print $4}' /data/CLIA-Data/PGxOne_V3/Production/BI_Data_Analysis/$runfolder/sample_codes_drugs.txt) ## find corresponding CASE ID based on requistion ID
			#echo /data/CLIA-Data/PGxOne_V3/Production/BI_Data_Analysis/$runfolder/LIS/$CASE_ID.txt
			cp /data/CLIA-Data/PGxOne_V3/Production/BI_Data_Analysis/$runfolder/LIS/$CASE_ID.txt /xifin/result-data/$CASE_ID.txt 
			sed -i "/$ID/d" $1 ## remove processed sample from request file
		else
			continue
		fi
	else
		echo Cannot find any run folder including $ID | tee -a Amend_log.txt | mail -s "Cannot find $ID" yifei.wan@admerahealth.com zhuosheng.gu@admerahealth.com ## generate log file and send remindering e-mail 
		sed -i "/$ID/d" $1 ## remove processed sample from request file
		continue
	fi
	if [[ $TYPE == *"Medication"* || $TYPE == *"ICD"* ]]
	then
		echo [`date`] The content: $TYPE of $ID from $run_index has been updated! $MESSAGE $TYPE\". | tee -a Amend_log.txt | mail -s "Pleas resign $ID" yifei.wan@admerahealth.com zhuosheng.gu@admerahealth.com 
	else
		echo [`date`] $TYPE of $ID has been update. Please check! | tee Amend_log.txt | mail -s "Pleas check $ID" yifei.wan@admerahealth.com
	fi
done
