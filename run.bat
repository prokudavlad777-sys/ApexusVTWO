@echo off
chcp 65001 >nul
set PYTHONUTF8=1
cd /d "%~dp0"
title APEXUS 1V

set "PY="
where python >nul 2>nul && set "PY=python"
if not defined PY where py >nul 2>nul && set "PY=py -3"
if not defined PY goto nopython

%PY% main.py
if errorlevel 1 goto failed
exit /b 0

:nopython
echo.
echo [ПОМИЛКА] Python не знайдено.
echo Встановіть Python 3.12 або новіший: https://www.python.org/downloads/
echo Під час встановлення поставте галочку "Add python.exe to PATH".
echo.
pause
exit /b 1

:failed
echo.
echo [ПОМИЛКА] Застосунок завершився з помилкою. Прочитайте повідомлення вище.
echo.
pause
exit /b 1
