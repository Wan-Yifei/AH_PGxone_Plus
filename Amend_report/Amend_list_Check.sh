#! /bin/bash

# @author Yifei Wan

# ===================================================================================================
# 01/29/2019	Beta version 0.0.1
# Summary:
# The bash script Amend_list_check.sh is use to automatically amend PGxOne reports.
#
# ** Input files**
# 1. Amend_request.csv: Accessioners input sample ID, amending content type and new added content.
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
# PGx_report_amend.py	Beta version 0.0.2
# PGx_Run/PGxOne_Scripts.sh
# ===================================================================================================
# 02/01/2019	Beta version 0.1.0
# Feature:
# 1. Recode content in request file to record file;
# 2. Send an additional e-mail to remind client care team.
#
# **Dependence**
# PGx_report_amend.py	Beta version 0.0.3
# ===================================================================================================
# 02/05/2019	Beta version 0.1.1
# Fix:
# If there is no MED and ICD, send reminder e-mail and record corresponding message.
# ===================================================================================================
# 02/12/2019	Beta version 0.1.2
# Fix:
# 1. Check that does tmp.txt exist before checking runfolder;
# 2. Correct the content of e-mail for client care team;
# 3. Don't rm content from Amend_request.txt if cannot find corresponding ID.
# ===================================================================================================
# 02/18/2019	Beta version 0.1.3
# Feat:
# Check PGxOneV3_Drug_List_not_covered_for_DDI.txt after run PGx_One_Scripts.sh to ensure that all
# drugs are covered.
# ===================================================================================================
# 02/21/2019	Beta version 0.1.4
# Feat:
# Update the pathway of PGxOne_Scripts.sh
# ===================================================================================================
# 02/22/2019	Beta version 0.1.5
# Feat:
# 1. Remove the trailing space from file to avoid find() command returning NA;
# 2. Add * to ID when remove line form Amend_request file.
# ===================================================================================================
# 03/01/2019	Beta version 0.1.6
# Feat:
# 1. Update the path of PGx_report_amend.py as complete path.
# ===================================================================================================
# 03/13/2019	Beta version 0.1.7
# Feat:
# 1. Update the path or record and log. Save both files to a fixed place as hidden files.
# ===================================================================================================
# 04/04/2019	Beta version 0.1.8
# Feat:
# 1. Copy action files to the PGxOne_APP folder.
# ===================================================================================================
# 04/12/2019	Beta version 0.2.0
# Feat:
# 1. Copy action files which are not amended medications or ICDs to APP folder and uploading folder;
# 2. Edit the e-mail for cond4: others.
# ===================================================================================================
# 04/18/2019	Gamma version 0.0.1
# Feat:
# 
# 1. Update the sender of the e-mail.
# ===================================================================================================
# 04/25/2019	Gamma version 0.0.1
# Feat:
# 
# 1. Run scripts for cond 4.
# ===================================================================================================

set -e
## message for Lab director
MESSAGE="Please resign with \"Update"

## Read amend requirement from require list
sed 's/"//g' $1 | sed 's/ \t/\t/g' | awk -F '\t' 'BEGIN {OFS = ";"} {if($1~/A-*/){print $1,$2,$3,$4}}' | while IFS=';' read ID TYPE ICD MED 
do
## Find run folder based on ID
	find /data/CLIA-Data/PGxOne_V3/Production/BI_Data_Analysis/ -name "$ID*.vcf" | while read path
	do
		dirname $path >> tmp.txt
	done
	if [ -f tmp.txt ]
	then
		runfolder=$(sort -u -t_ -rk4 tmp.txt | head -n 1 | cut -d / -f7) ## pathway of run folder, select the newest folder
		run_index=$(echo $runfolder | cut -d _ -f4) ## e.g. Run700
		rm tmp.txt ## delet tmp	echo -e
		echo ================================================================
		echo ================================================================
		echo -e
		echo Amend $ID from $runfolder
		echo -e
	else
		echo -e
		echo ================================================================
		echo ================================================================
		echo Cannot find $ID
	fi

## Amend report

DDI_check=/data/CLIA-Data/PGxOne_V3/Production/BI_Data_Analysis/$runfolder/PGxOneV3_Drug_List_not_covered_for_DDI.txt

	if [ ! -z $runfolder ]
	then
		if [[ $TYPE == *"edication"* && $TYPE == *"ICD"* ]]
		then
			echo cond1:Both
			python3 /home/yifei.wan/AH_Project/Amend_report/PGx_report_amend.py $runfolder $ID "$TYPE" -M "$MED" -I "$ICD"
			bash /home/yifei.wan/AH_Project/PGx_Run/PGxOne_Scripts.sh $runfolder
			DDI_count=$(wc -l $DDI_check | cut -d " " -f -1)
			if [[ $DDI_count < 2 ]]
			then
				CASE_ID=$(awk -F"\t" -v ID=$ID '$1 == ID {print $4}' /data/CLIA-Data/PGxOne_V3/Production/BI_Data_Analysis/$runfolder/sample_codes_drugs.txt) ## find corresponding CASE ID based on requistion ID
				#echo /data/CLIA-Data/PGxOne_V3/Production/BI_Data_Analysis/$runfolder/LIS/$CASE_ID.txt
				cp /data/CLIA-Data/PGxOne_V3/Production/BI_Data_Analysis/$runfolder/LIS/$CASE_ID.txt /xifin/result-data/$CASE_ID.txt 
				cp /data/CLIA-Data/PGxOne_V3/Production/BI_Data_Analysis/$runfolder/LIS/$CASE_ID.txt /data/CLIA-Data/PGxOne_APP/ 
				awk -F '\t' -v ID=$ID '$1 == ID {print $0}' $1 >> /data/AmendReports/.Amend_record.txt
				sed -i "/$ID*/d" $1 ## remove processed sample from request file
				status=1
			else
				status=0
			fi
		elif [[ "$TYPE" == *"edication"* ]]
		then
			echo cond2:Med
			python3 /home/yifei.wan/AH_Project/Amend_report/PGx_report_amend.py $runfolder $ID "$TYPE" -M "$MED"
			bash /home/yifei.wan/AH_Project/PGx_Run/PGxOne_Scripts.sh $runfolder
			DDI_count=$(wc -l $DDI_check | cut -d " " -f -1)
			if [[ $DDI_count < 2 ]]
			then
				CASE_ID=$(awk -F"\t" -v ID=$ID '$1 == ID {print $4}' /data/CLIA-Data/PGxOne_V3/Production/BI_Data_Analysis/$runfolder/sample_codes_drugs.txt) ## find corresponding CASE ID based on requistion ID
				#echo /data/CLIA-Data/PGxOne_V3/Production/BI_Data_Analysis/$runfolder/LIS/$CASE_ID.txt
				cp /data/CLIA-Data/PGxOne_V3/Production/BI_Data_Analysis/$runfolder/LIS/$CASE_ID.txt /xifin/result-data/$CASE_ID.txt 
				cp /data/CLIA-Data/PGxOne_V3/Production/BI_Data_Analysis/$runfolder/LIS/$CASE_ID.txt /data/CLIA-Data/PGxOne_APP/ 
				awk -F '\t' -v ID=$ID '$1 == ID {print $0}' $1 >> /data/AmendReports/.Amend_record.txt
				sed -i "/$ID*/d" $1 ## remove processed sample from request file
				status=1
			else
				status=0
			fi
		elif [[ $TYPE == *"ICD"* ]]
		then
			echo cond3:ICD
			python3 /home/yifei.wan/AH_Project/Amend_report/PGx_report_amend.py $runfolder $ID "$TYPE" -I "$ICD"
			bash /home/yifei.wan/AH_Project/PGx_Run/PGxOne_Scripts.sh $runfolder
			DDI_count=$(wc -l $DDI_check | cut -d " " -f -1)
			if [[ $DDI_count < 2 ]]
			then
				CASE_ID=$(awk -F"\t" -v ID=$ID '$1 == ID {print $4}' /data/CLIA-Data/PGxOne_V3/Production/BI_Data_Analysis/$runfolder/sample_codes_drugs.txt) ## find corresponding CASE ID based on requistion ID
				#echo /data/CLIA-Data/PGxOne_V3/Production/BI_Data_Analysis/$runfolder/LIS/$CASE_ID.txt
				cp /data/CLIA-Data/PGxOne_V3/Production/BI_Data_Analysis/$runfolder/LIS/$CASE_ID.txt /xifin/result-data/$CASE_ID.txt 
				cp /data/CLIA-Data/PGxOne_V3/Production/BI_Data_Analysis/$runfolder/LIS/$CASE_ID.txt /data/CLIA-Data/PGxOne_APP/ 
				awk -F '\t' -v ID=$ID '$1 == ID {print $0}' $1 >> /data/AmendReports/.Amend_record.txt
				sed -i "/$ID*/d" $1 ## remove processed sample from request file
				status=1
			else
				status=0
			fi
		else
			echo cond4:Others
			python3 /home/yifei.wan/AH_Project/Amend_report/PGx_report_amend.py $runfolder $ID "$TYPE" -I "$ICD"
			bash /home/yifei.wan/AH_Project/PGx_Run/PGxOne_Scripts.sh $runfolder
			CASE_ID=$(awk -F"\t" -v ID=$ID '$1 == ID {print $4}' /data/CLIA-Data/PGxOne_V3/Production/BI_Data_Analysis/$runfolder/sample_codes_drugs.txt) ## find corresponding CASE ID based on requistion ID
			#echo /data/CLIA-Data/PGxOne_V3/Production/BI_Data_Analysis/$runfolder/LIS/$CASE_ID.txt
			cp /data/CLIA-Data/PGxOne_V3/Production/BI_Data_Analysis/$runfolder/LIS/$CASE_ID.txt /xifin/result-data/$CASE_ID.txt 
			cp /data/CLIA-Data/PGxOne_V3/Production/BI_Data_Analysis/$runfolder/LIS/$CASE_ID.txt /data/CLIA-Data/PGxOne_APP/ 
			awk -F '\t' -v ID=$ID '$1 == ID {print $0}' $1 >> /data/AmendReports/.Amend_record.txt
			sed -i "/$ID*/d" $1 ## remove processed sample from request file
			echo [`date`] The content: $TYPE of $ID from $run_index has been updated! $MESSAGE $TYPE\". | tee -a /data/AmendReports/.Amend_log.txt | mail -a FROM:yifei.wan@admerahealth.com -s "Pleas resign $ID" yifei.wan@admerahealth.com zhuosheng.gu@admerahealth.com alvina.williams@admerahealth.com tom.sousa@admerahealth.com
		fi
	else
		echo [`date`] Cannot find any run folder including $ID | tee -a /data/AmendReports/.Amend_log.txt | mail -a FROM:yifei.wan@admerahealth.com -s "Cannot find $ID" yifei.wan@admerahealth.com zhuosheng.gu@admerahealth.com tom.sousa@admerahealth.com 
                ## generate log file and send remindering e-mail 
	fi

# Final e-mail
	if [[ $TYPE == *"edication"* || $TYPE == *"ICD"* ]] && [[ $status == 1 ]]
	then
		echo [`date`] The content: $TYPE of $ID from $run_index has been updated! $MESSAGE $TYPE\". | tee -a /data/AmendReports/.Amend_log.txt | mail -a FROM:yifei.wan@admerahealth.com -s "Pleas resign $ID" yifei.wan@admerahealth.com zhuosheng.gu@admerahealth.com tom.sousa@admerahealth.com
		echo [`date`] $TYPE of $ID from $run_index has been updated and $ID has been sent to sign. | mail -a FROM:yifei.wan@admerahealth.com -s "Amending: $ID" yifei.wan@admerahealth.com frances.ramos@admerahealth.com shadae.waiters@admerahealth.com alvina.williams@admerahealth.com tom.sousa@admerahealth.com
                ## send reminder to client care team 
	elif [[ $status == 0 ]]
	then
		echo Please check DDI file for $ID in $run_index! | tee -a /data/AmendReports/.Amend_log.txt | mail -a FROM:yifei.wan@admerahealth.com -s "Please check DDI" yifei.wan@admerahealth.com
	fi

	unset runfolder
	unset TYPE
done
