#! /bin/bash
#To do: move new action file to batch uploading folder 

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
	runfolder=$(sort -u -t_ -rk4 tmp.txt | head -n 1 | cut -d / -f7) ## pathway of run folder
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
			python3 PGx_report_amend.py $runfolder $ID $TYPE -M $MED -I $ICD
			bash /home/yifei.wan/AH_PGxOne_Plus/PGx_Run/PGxOne_Scripts.sh $runfolder
			#cp /data/CLIA-Data/PGxOne_V3/Production/BI_Data_Analysis/$runfolder/LIS
			sed -i "/$ID/d" $1 ## remove processed sample from request file
		elif [[ $TYPE == *"Medication"* ]]
		then
			echo cond2:Med
			python3 PGx_report_amend.py $runfolder $ID $TYPE -M "$MED"
			bash /home/yifei.wan/AH_PGxOne_Plus/PGx_Run/PGxOne_Scripts.sh $runfolder
			sed -i "/$ID/d" $1 ## remove processed sample from request file
		elif [[ $TYPE == *"ICD"* ]]
		then
			echo cond3:ICD
			python3 PGx_report_amend.py $runfolder $ID $TYPE -I $ICD
			bash /home/yifei.wan/AH_PGxOne_Plus/PGx_Run/PGxOne_Scripts.sh $runfolder
			sed -i "/$ID/dt " $1 ## remove processed sample from request file
		else
			continue
		fi
	else
		echo Cannot find any run folder including $ID | tee -a Amend_log.txt | mail -s "Cannot find $ID" yifei.wan@admerahealth.com zhuosheng.gu@admerahealth.com ## generate log file and send remindering e-mail 
		sed -i '/$ID/d' $1 ## remove processed sample from request file
		continue
	fi
	if [[ $TYPE == *"Medication"* || $TYPE == *"ICD"* ]]
	then
		echo [`date`] The content: $TYPE of $ID from $run_index has been updated! $MESSAGE $TYPE\". | tee -a Amend_log.txt | mail -s "Pleas resign $ID" yifei.wan@admerahealth.com zhuosheng.gu@admerahealth.com 
	else
		echo [`date`] $TYPE of $ID has been update. Please check! | tee Amend_log.txt | mail -s "Pleas check $ID" yifei.wan@admerahealth.com
	fi
done
