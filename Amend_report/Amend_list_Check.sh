#! /bin/bash

cat $1 | while read line 
do
	awk '{if($1~/A-*/){print $0}}'
done
