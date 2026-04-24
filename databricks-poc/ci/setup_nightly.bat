@echo off
REM ============================================================
REM  setup_nightly.bat
REM  Registers a Windows Task Scheduler job to run the
REM  Utilitics nightly build every day at 02:00 AM.
REM
REM  Run this script once as Administrator.
REM  To remove the task later:
REM    schtasks /Delete /TN "Utilitics_NightlyBuild" /F
REM ============================================================

SET TASK_NAME=Utilitics_NightlyBuild
SET PROJECT_DIR=%~dp0..
SET PYTHON_EXE=%PROJECT_DIR%\venv\Scripts\python.exe
SET SCRIPT=%PROJECT_DIR%\ci\nightly_build.py

echo.
echo Creating Task Scheduler job: %TASK_NAME%
echo Python:  %PYTHON_EXE%
echo Script:  %SCRIPT%
echo Schedule: Daily at 02:00 AM
echo.

schtasks /Create /TN "%TASK_NAME%" ^
  /TR "\"%PYTHON_EXE%\" \"%SCRIPT%\"" ^
  /SC DAILY ^
  /ST 02:00 ^
  /RU "%USERNAME%" ^
  /F

IF %ERRORLEVEL% EQU 0 (
    echo.
    echo  SUCCESS: Nightly build scheduled for 02:00 AM daily.
    echo  To verify: schtasks /Query /TN "%TASK_NAME%"
    echo  To run now: schtasks /Run /TN "%TASK_NAME%"
) ELSE (
    echo.
    echo  FAILED: Could not create task. Try running as Administrator.
)

echo.
pause
