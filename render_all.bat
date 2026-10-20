@echo off
REM  Saare 6 videos ek ke baad ek render karta hai (raat ko chalane ke liye).
REM  Pehle sab videos ki scene wav files (awaaz) banayi honi chahiye (check_audio.bat se dekhein).
REM  Har video ban jaane par uska backup Desktop\RJP_BACKUP aur D:\RJP_BACKUP mein khud ban jaata hai.
set BLENDER="C:\Program Files\Blender Foundation\Blender 3.6\blender.exe"
for %%V in (lkg1 lkg2 lkg3 c1_ginti c1_jodna c1_english) do (
  echo ===== %%V =====
  %BLENDER% -b -P "%~dp0build_video.py" -- %%V
  call "%~dp0backup.bat" %%V
)
echo Sab ho gaya.
pause
