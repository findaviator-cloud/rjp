@echo off
REM  render.bat <video> [test] [draft] [workbench]
REM  Udaharan:  render.bat lkg1 test      (3 frame, time naapne ke liye)
REM             render.bat lkg1           (poora video; ho jaane par backup bhi khud banta hai)
REM  Blender ka rasta alag ho to neeche wali line badlein.
set BLENDER="C:\Program Files\Blender Foundation\Blender 3.6\blender.exe"
if "%1"=="" (
  echo Video ka naam likhein: lkg1 lkg2 lkg3 c1_ginti c1_jodna c1_english
  exit /b 1
)
%BLENDER% -b -P "%~dp0build_video.py" -- %1 %2 %3 %4
echo.
if "%2"=="" call "%~dp0backup.bat" %1
echo Kaam khatam. Upar dekhein ki koi ERROR to nahi aaya.
pause
