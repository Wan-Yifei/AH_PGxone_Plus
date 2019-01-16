#! /bin/bash

awk '{if($1~/A-*/){print $1,$2,$3}}' $1 | while read ID type Med ICD
do
	find /data/CLIA-Data/PGxOne_V3/Production/BI_Data_Analysis/ -name "$ID*.vcf" | while read path
	do
		dirname $path >> tmp.txt
	done
	$(sort -u -t_ -k4 tmp.txt) | echo
	echo "$ID"
done
