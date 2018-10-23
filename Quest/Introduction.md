# Quest Sample result Transfer script

## Transfer flat files
Flat files:
### Action file

+ Find file under path:
```
'find /data/CLIA-Data/PGxOne_V3/Production/BI_Data_Analysis/18*/Plus -mtime 0 | grep "LIS.txt" | grep "%s"'%(reqID)
```
+ Add first row:
```
'sed "1 i\##RequisitionNumber: %s" %s> /tmp/%s'%(reqID, actionFile, actionFile.split("/")[-1])
```

### Patient information

+ get path

Use optional argument `-p`
```
'grep %s %s'%(reqID, masterPHIfile)
```
## Transfer PDF report

+ get path

Use optional argument `-R'
```
'find %s/ -mtime 0 | grep "PGQD" | grep "pdf"'%args.reportFolder
````

When use subcommand `Run`, the script will serach all today's reports in batch printing folder. No need to input ID.
