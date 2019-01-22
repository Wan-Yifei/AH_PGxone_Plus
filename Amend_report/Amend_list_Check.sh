#! /bin/bash
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
	runfolder=$(sort -u -t_ -rk4 tmp.txt | head -n 1 | cut -d / -f7)
	run_index=$(echo $runfolder | cut -d _ -f4)
	echo Amend $ID from $run_index 
## Amend report
	#python3 PGx_report_amend.py $runfolder $TYPE $MED $ICD
	if [ $TYPE = "Medication" ]
	then
		echo `date`	The $TYPE list of $ID from $run_index has been updated! $MESSAGE $TYPE\". | tee Amend_log.txt | mail -s "Pleas resign $ID" yifei.wan@admerahealth.com 
	elif [ $TYPE = "ICD" ]
	then 
		echo `date`	The $TYPE codes of $ID from $run_index has been updated! $MESSAGE $TYPE\". | tee Amend_log.txt | mail -s "Pleas resign $ID" yifei.wan@admerahealth.com
	elif [ $TYPE = "Both" ]
	then
		echo `date`>The ICD and Medication of $ID from $run_index have been updated! $MESSAGE $TYPE\". | tee Amend_log.txt | mail -s "Pleas resign $ID" yifei.wan@admerahealth.com
	else
		echo `date`	$TYPE of $ID has been update. Please check! | tee Amend_log.txt | mail -s "Pleas check $ID" yifei.wan@admerahealth.com
	fi
done
