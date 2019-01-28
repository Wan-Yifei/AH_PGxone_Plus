#! /bin/bash
#To do: rm processed sample from request file
#To do: move new action file to batch uploading folder 

set -e
## message for Lab director
MESSAGE="Please resign with \"Update"

## Read amend requirement from require list
awk '{if($1~/A-*/){print $1,$2,$3}}' $1 | while read ID TYPE MED ICD
do
## Find run folder based on ID
	find /data/CLIA-Data/PGxOne_V3/Production/BI_Data_Analysis/ -name "$ID*.vcf" | while read path
	do
		dirname $path >> tmp.txt
	done
	runfolder=$(sort -u -t_ -rk4 tmp.txt | head -n 1 | cut -d / -f7) ## pathway of run folder
	run_index=$(echo $runfolder | cut -d _ -f4) ## e.g. Run700
	rm tmp.txt ## delet tmp
	echo -e
	echo ================================================================
	echo ================================================================
	echo -e
	echo Amend $ID from $run_index 
	echo -e

## Amend report
	if [ ! -z $runfolder ]
	then
		python3 PGx_report_amend.py $runfolder $ID $TYPE -M $MED -I $ICD
		sed -i '/$ID/d' $1
	else
		echo Cannot find any run folder including $ID | tee -a Amend_log.txt 
		continue
	fi
	bash /home/yifei.wan/AH_PGxOne_Plus/PGx_Run/PGxOne_Scripts.sh $runfolder
	if [[ $TYPE == *"Medication"* || $Type == *"ICD"* ]]
	then
		echo [`date`] The content: $TYPE of $ID from $run_index has been updated! $MESSAGE $TYPE\". | tee -a Amend_log.txt | mail -s "Pleas resign $ID" yifei.wan@admerahealth.com zhuosheng.gu@admerahealth.com 
	else
		echo [`date`] $TYPE of $ID has been update. Please check! | tee Amend_log.txt | mail -s "Pleas check $ID" yifei.wan@admerahealth.com
	fi
done
