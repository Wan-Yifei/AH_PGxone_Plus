@echo off
set /p Run_ID= Please input the output folder on Miseqoutput:
echo.
rem echo %Run_ID%
set ID=%Run_ID:~7%
set date=%Run_ID:~0,6%
echo date: %date%
echo Run ID: %ID%
echo.
set /p Run_ind= Please input the index Run:
set Run_rank=_CLIA_Plus_%Run_ind%_
set Run_folder=%date%%Run_rank%%ID%
echo %Run_folder%

rem Create Run folder under MiseqAnalysis
mkdir V:\%Run_folder%
mkdir V:\%Run_folder%\Data
mkdir V:\%Run_folder%\Data\Intensities
mkdir V:\%Run_folder%\Data\Intensities\BaseCalls
mkdir V:\%Run_folder%\Data\Intensities\BaseCalls\CLC

echo Copy Sample sheet to Run folder
copy W:\%Run_ID%\SampleSheet.csv V:\%Run_folder%
echo.
echo The path of output
echo PGxOne_Plus_Run_%Run_ind%
echo.
copy D:\Output\PGxOne_Plus_%Run_ind%\* V:\%Run_folder%\Data\Intensities\BaseCalls\CLC

echo.
echo Output transfering Success!
pause
