#! /bin/bash
set -e # exit when error occur
cd /data/CLIA-Data/PGxOne_V3/Production/BI_Data_Analysis/$1/
echo "Run folder: $1"
perl PGxOneV3_Phenotype.pl
echo "1. Phenotype down!"
perl PGxOneV3_Create_DrugList.pl
echo "2. Create_DrugList down!"
perl PGxOneV3_DrugAction.pl
echo "3. DrugAction down!"
perl PGxOneV3_DrugAction_LIS.pl
echo "4. DrugAction_LIS down!"
python PGxOneV3_Drug_Cleanup.py
echo "5. Cleanup down!"
python PGxOneV3_Drug_DDI.py
echo "6. DDI down!"
