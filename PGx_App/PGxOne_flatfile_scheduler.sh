#! /bin/bash

# @author: Yifei Wan

# ========================================================================
# 04/02/2019	Basic version 0.0.1
# Move action files to admeraappflatfilesdev folder 
# 
# ** Input ** 
# 1. the action files in the PGxOne_APP folder under the CLIA-Data disk.
# ========================================================================
# 04/03/2019	Basic verson 0.0.2
# Redirect std and err
#
# Redirect standard output and error message to both file and console.
# ========================================================================

ACTIONFOLDER='/data/CLIA-Data/PGxOne_APP/'

## current date
date=$(date +%Y-%m-%d)

## Check wheter the date named output folder exists 

if [ -d /admeraappflatfilesdev/$date ]
then
	echo folder: $date exists!
else
	echo folder: $date does not exists!
	echo Create folder: $date
	mkdir /admeraappflatfilesdev/$date
fi

## Move flat files to admeraappflatfilesdev folder 


Move_flat() {
	cp -v $ACTIONFOLDER/*.txt /admeraappflatfilesdev/$1 > >(tee -a Bucket_log.txt) 2> >(tee -a Bucket_err_log.txt > &2)
}


## Run
{
	## try to move action files
	Move_flat $date
} || { ## sleep and try agian
	echo Hold 5 seconds!
	sleep 5
	Move_flat
}


