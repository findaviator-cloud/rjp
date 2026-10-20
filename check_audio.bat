@echo off
REM  Dekhta hai ki kis scene ki wav (awaaz) abhi banani baaki hai.
set MISS=0
for %%V in (lkg1 lkg2 lkg3 c1_ginti c1_jodna c1_english) do (
  for %%F in ("%~dp0%%V\scene*.txt") do (
    if not exist "%~dp0%%V\%%~nF.wav" (
      echo BAAKI: %%V\%%~nF.wav
      set MISS=1
    )
  )
)
if "%MISS%"=="0" echo Sab wav files maujood hain. Ab render.bat chala sakte hain.
pause
