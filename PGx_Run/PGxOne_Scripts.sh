#! /bin/bash
set -e # exit when error occur
cd /data/CLIA-Data/PGxOne_V3/Production/BI_Data_Analysis/$1/
echo "Run folder: $1"
bash /home/yifei.wan/AH_Project/PGx_Run/columnCheck.sh $1 
perl PGxOneV3_Phenotype.pl
echo "1. Phenotype done!"
perl PGxOneV3_Create_DrugList.pl
echo "2. Create_DrugList done!"
perl PGxOneV3_DrugAction.pl
echo "3. DrugAction done!"
perl PGxOneV3_DrugAction_LIS.pl
echo "4. DrugAction_LIS done!"
python PGxOneV3_Drug_Cleanup.py
echo "5. Cleanup done!"
python PGxOneV3_Drug_DDI.py
echo "6. DDI done!"

{
    python3 /home/yifei.wan/AH_Project/PGx_Run/change_group.py $1
} || {
    echo ======================================
    echo Ignore chgrp command line!
    echo ======================================
}
#echo The groups of all files has been changed to CLIA!
echo Action files have been updated! 
echo ======================================
