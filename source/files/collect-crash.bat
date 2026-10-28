@echo off
chcp 437 >nul
setlocal
set "GAMEDIR="
for %%D in ("%~dp0" "C:\Warcraft III\" "C:\Games\Warcraft III\" "%USERPROFILE%\Desktop\Warcraft III\" "D:\Warcraft III\") do (
  if exist "%%~DGame.dll" set "GAMEDIR=%%~D"
)
if "%GAMEDIR%"=="" (
  echo [X] Warcraft III folder not found.
  echo     Put this bat INTO your Warcraft III folder ^(where war3.exe is^) and run again.
  pause
  exit /b
)
cd /d "%GAMEDIR%"
set "R=%USERPROFILE%\Desktop\crash-report.txt"
echo Collecting info from: %GAMEDIR%
(
echo === WC3 CRASH REPORT %date% %time% ===
echo [GameDir] %GAMEDIR%
echo.
echo [EXE/DLL list]
dir /b *.exe *.dll 2>nul
echo.
echo [Key file MD5]
for %%F in (Game.dll war3.exe War3.exe storm.dll Storm.dll opengl32.dll libgallium_wgl.dll libglapi.dll dxil.dll) do (
  if exist "%%F" (
    echo --- %%F
    certutil -hashfile "%%F" MD5 | findstr /r /c:"^[0-9a-fA-F]"
  )
)
echo.
echo [Maps Download folder]
dir /b "Maps\Download" 2>nul
echo.
echo [Registry]
reg query "HKLM\SOFTWARE\Blizzard Entertainment\Warcraft III" /s 2>nul
reg query "HKCU\Software\Blizzard Entertainment\Warcraft III" /s 2>nul
echo.
echo [Errors folder listing]
dir /b Errors 2>nul
echo.
for %%F in (Errors\*.txt) do (
  echo ================================ %%F ================================
  type "%%F"
  echo.
)
) > "%R%"
echo Report saved to: %R%
echo Uploading to host...
curl.exe --noproxy "*" -s -m 25 -X POST --data-binary "@%R%" "http://192.168.64.1:8899/upload?name=crash-report.txt" >nul 2>&1
if %errorlevel%==0 (
  echo [OK] Upload done. You can close this window.
) else (
  echo [!] Upload failed ^(normal if this PC is not the VM^).
  echo     Please send the file Desktop\crash-report.txt back for analysis.
)
pause
