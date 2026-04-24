@echo off
REM ============================================================
REM  install_hooks.bat
REM  Installs a Git pre-commit hook that runs CI checks before
REM  every local commit.  Run once after cloning the repo.
REM ============================================================

SET HOOK_DIR=%~dp0..\.git\hooks
SET HOOK_FILE=%HOOK_DIR%\pre-commit

IF NOT EXIST "%HOOK_DIR%" (
    echo ERROR: .git\hooks folder not found. Are you in the repo root?
    pause
    exit /b 1
)

echo Writing pre-commit hook to %HOOK_FILE%

(
echo #!/bin/sh
echo # Utilitics pre-commit CI check
echo echo "[pre-commit] Running syntax and secrets check..."
echo python ci/check_syntax.py
echo if [ $? -ne 0 ]; then
echo     echo "[pre-commit] FAILED — fix errors above before committing."
echo     exit 1
echo fi
echo echo "[pre-commit] All checks passed."
) > "%HOOK_FILE%"

echo  Pre-commit hook installed at %HOOK_FILE%
echo  Every 'git commit' will now run CI checks automatically.
echo.
pause
