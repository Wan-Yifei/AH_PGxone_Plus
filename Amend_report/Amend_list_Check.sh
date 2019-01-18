#! /bin/bash

## Read amend requirement from require list
awk '{if($1~/A-*/){print $1,$2,$3}}' $1 | while read ID type Med ICD
do
## Find run folder based on ID
	find /data/CLIA-Data/PGxOne_V3/Production/BI_Data_Analysis/ -name "$ID*.vcf" | while read path
	do
		dirname $path >> tmp.txt
	done
	runfolder=$(sort -u -t_ -rk4 tmp.txt | head -n 1 | cut -d / -f7)
	run_index=$(echo $runfolder | cut -d _ -f4)
	echo Amend $ID from $run_index 
	#python3 PGx_report_amend.py $runfolder $type $Med $ICD
	if [ $type = "Medication" ];
	then
		echo $ID from $run_index has been updated $type!
	fi
done
