:: Bertin F. 26-05-2024

@echo off
Title create CTG.exe
mkdir %TEMP%\CTG_exe
@echo ceate %TEMP%\CTG_exe successfully

:: create a venv with python 3.9.7
:: adapted from https://stackoverflow.com/questions/45833736/how-to-store-python-version-in-a-variable-inside-bat-file-in-an-easy-way?noredirect=1
for /F "tokens=* USEBACKQ" %%F in (`python --version`) do (set var=%%F)
echo create a virtual environment with %var%
cd %TEMP%\CTG_exe
python -m venv venv


:: activate the venv
set VIRTUAL_ENV=%TEMP%\CTG_exe\venv
if defined _OLD_VIRTUAL_PYTHONHOME set PYTHONHOME=%_OLD_VIRTUAL_PYTHONHOME%
if defined PYTHONHOME set _OLD_VIRTUAL_PYTHONHOME=%PYTHONHOME%
set PYTHONHOME=
if defined _OLD_VIRTUAL_PATH set PATH=%_OLD_VIRTUAL_PATH%
if not defined _OLD_VIRTUAL_PATH set _OLD_VIRTUAL_PATH=%PATH%
set PATH=%VIRTUAL_ENV%\Scripts;%PATH%


:: builds the CTG_METER python program
set "PGM=%TEMP%\CTG_exe\CTG_METER.py"
echo from CTG_Utils.CTG_GUI import AppMain > %PGM%
echo app_main = AppMain() >> %PGM%
echo app_main.mainloop() >> %PGM%

:: install packages

pip install CTG_Utils
pip install auto-py-to-exe

:: remote the directories buib and dist
:: set the directories buid and dist used when making the executable

set "BUILD=%TEMP%\CTG_exe\build"
set "DIST=%TEMP%\CTG_exe\dist"
rmdir /s /q %BUILD%
rmdir /s /q %DIST%

:: set the default directories
:: ICON contains the icon file with the format.ico
:: PGM contain the application lauch python program

set "ICON=%TEMP%/CTG_exe/venv/Lib/site-packages/ctgutils/CTG_Func/CTG_RefFiles/logoctg4.ico"
set "DATA=%TEMP%/CTG_exe/venv/Lib/site-packages/ctgutils;ctgutils/"

:: make the executable 
pyinstaller --noconfirm --onefile --console^
 --icon "%ICON%"^
 --add-data "%DATA%"^
 "%PGM%"
 
:: rename the directory dist to aaaa_mm_jj BiblioMeter 
:: adapted from http://stackoverflow.com/a/10945887/1810071
for /f "skip=1" %%x in ('wmic os get localdatetime') do if not defined MyDate set MyDate=%%x
for /f %%x in ('wmic path win32_localtime get /format:list ^| findstr "="') do set %%x
set fmonth=00%Month%
set fday=00%Day%
set dirname="%Year%-%fmonth:~-2%-%fday:~-2% CTG_Meter"
rename dist %dirname%
 
set "new_file_name=%dirname%.exe"
ren %TEMP%\CTG_exe\%dirname%\CTG_METER.exe %new_file_name%
echo %new_file_name% is located in %TEMP%\CTG_exe\%dirname% 

:: Copy Exe
set /p "rep=do you want to copy this file in a folder (y/n) : "
if NOT %rep%==y GOTO FIN
set /p "new_dir=enter the full path of the folder : "
set input_file=%TEMP%\CTG_exe\%dirname%\%dirname%.exe%
set output_file=%new_dir%\%dirname%.exe%
copy  %input_file% %output_file%
echo copy %input_file% %output_file%
:FIN

pause