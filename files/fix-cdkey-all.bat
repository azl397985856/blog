@echo off
chcp 437 >nul
title Warcraft III CD-Key Fix (ALL variants)

set KEYPLAIN=H8DNBVNW7YNXFZVEFNDYH6HXNE
set KEYHEX=00,00,48,2a,f4,39,90,41,42,a2,1f,94,cf,db,e2,95

echo Writing ALL key variants to ALL registry locations...

:: === HKLM 64-bit view ===
reg add "HKLM\SOFTWARE\Blizzard Entertainment\Warcraft III" /v "War3X CD" /t REG_SZ /d %KEYPLAIN% /f
reg add "HKLM\SOFTWARE\Blizzard Entertainment\Warcraft III" /v "War3 CD" /t REG_SZ /d %KEYPLAIN% /f
reg add "HKLM\SOFTWARE\Blizzard Entertainment\Warcraft III" /v "War3X CD" /t REG_BINARY /d %KEYHEX% /f
reg add "HKLM\SOFTWARE\Blizzard Entertainment\Warcraft III" /v "War3 CD" /t REG_BINARY /d %KEYHEX% /f

:: === HKLM 32-bit view (WOW6432Node) ===
reg add "HKLM\SOFTWARE\WOW6432Node\Blizzard Entertainment\Warcraft III" /v "War3X CD" /t REG_SZ /d %KEYPLAIN% /f
reg add "HKLM\SOFTWARE\WOW6432Node\Blizzard Entertainment\Warcraft III" /v "War3 CD" /t REG_SZ /d %KEYPLAIN% /f
reg add "HKLM\SOFTWARE\WOW6432Node\Blizzard Entertainment\Warcraft III" /v "War3X CD" /t REG_BINARY /d %KEYHEX% /f
reg add "HKLM\SOFTWARE\WOW6432Node\Blizzard Entertainment\Warcraft III" /v "War3 CD" /t REG_BINARY /d %KEYHEX% /f

:: === HKCU ===
reg add "HKCU\Software\Blizzard Entertainment\Warcraft III" /v "War3X CD" /t REG_SZ /d %KEYPLAIN% /f
reg add "HKCU\Software\Blizzard Entertainment\Warcraft III" /v "War3 CD" /t REG_SZ /d %KEYPLAIN% /f
reg add "HKCU\Software\Blizzard Entertainment\Warcraft III" /v "War3X CD" /t REG_BINARY /d %KEYHEX% /f
reg add "HKCU\Software\Blizzard Entertainment\Warcraft III" /v "War3 CD" /t REG_BINARY /d %KEYHEX% /f

:: === 带空格变体值名(部分版本读取) ===
reg add "HKLM\SOFTWARE\Blizzard Entertainment\Warcraft III" /v "War3XCD" /t REG_SZ /d %KEYPLAIN% /f
reg add "HKCU\Software\Blizzard Entertainment\Warcraft III" /v "War3XCD" /t REG_SZ /d %KEYPLAIN% /f

echo.
echo ============================================
echo  ALL DONE! Now run War3.exe again.
echo ============================================
pause
