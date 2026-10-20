@echo off
REM  backup.bat <video>  - us video ki awaaz (wav), text, srt aur mp4 ki copy 2 jagah rakhta hai:
REM     1) Desktop\RJP_BACKUP\<video>
REM     2) D:\RJP_BACKUP\<video>   (agar D drive hai)
REM  Frames aur .blend copy nahi hote (wo dobara ban jaate hain).
if "%1"=="" exit /b 1
set SRC=%~dp0%1
if not exist "%SRC%" exit /b 1
set D1=%USERPROFILE%\Desktop\RJP_BACKUP\%1
robocopy "%SRC%" "%D1%" *.wav *.txt *.srt *.mp4 /XD frames test /NFL /NDL /NJH /NJS /NP >nul
if errorlevel 8 (echo [BACKUP] Desktop par copy nahi ho payi - Windows ne roka ho sakta hai. File Explorer se haath se copy kar lein.) else (echo [BACKUP] Desktop\RJP_BACKUP\%1 mein copy ho gaya.)
if exist D:\ (
  robocopy "%SRC%" "D:\RJP_BACKUP\%1" *.wav *.txt *.srt *.mp4 /XD frames test /NFL /NDL /NJH /NJS /NP >nul
  if errorlevel 8 (echo [BACKUP] D: par copy nahi ho payi.) else (echo [BACKUP] D:\RJP_BACKUP\%1 mein bhi copy ho gaya.)
)
exit /b 0
