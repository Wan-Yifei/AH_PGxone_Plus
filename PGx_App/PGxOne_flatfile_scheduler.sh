#! /bin/bash

# @author: Yifei Wan

# ========================================================================
# 04/02/2019	Basic version 0.0.1
# Move action files to admeraappflatfilesdev folder 
# 
# ** Input ** 
# 1. the action files in the PGxOne_APP folder under the CLIA-Data disk.
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
	mkdir /admeraappflatfilesdev/$date
fi

## Move flat files to admeraappflatfilesdev folder 


Move_flat() {
	cp -v $ACTIONFOLDER/*.txt /admeraappflatfilesdev/
}


## Run
{
	## try to move action files
	Move_flat
} || { ## sleep and try agian
	sleep 5
	Move_flat
}


