#!/bin/bash
set -e
cd /data/CLIA-Data/PGxOne_V3/Production/BI_Data_Analysis/$1/
#This counts the number of columns in the first row, and the exits after first row so it doesn't repeat
columncount=$(awk -F'\t' '{print NF; exit}' sample_output_genotype.txt)
if [ $columncount -eq 54 ]
	then
	echo 'There are 54 columns in sample_output_genotype.txt'
else
	inpexit=0
while [ $inpexit -ne 1 ]
	do
	echo "There are ${columncount} columns in sample_output_genotype.txt, would you like to continue? [Y/N]: "
	read contvar
	if [ $contvar == 'y' ] || [ $contvar == 'Y' ]
		then 
		inpexit=1
	elif [ $contvar == 'n' ] || [ $contvar == 'N' ]
		then
		echo "Error thrown: Invalid column count"
		exit 1
	else
		inpexit=0
		echo "Please enter a valid value."
	fi
	done
fi
