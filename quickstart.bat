@echo off
setlocal

echo ==========================================
echo    ITU Ders Secici - Quick Setup
echo ==========================================

:: 1. Check/Install Git
where git >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [INFO] 'Git' not found. Installing via Winget...
    winget install -e --id Git.Git --accept-source-agreements --accept-package-agreements
    if %ERRORLEVEL% NEQ 0 (
        echo [ERROR] Failed to install Git.
        pause
        exit /b 1
    )
    echo [INFO] Refreshing Path variables...
    call :RefreshEnv
)

:: 2. Check for Project/Clone
if not exist "Justfile" (
    echo [INFO] Justfile not found. Cloning repository...
    git clone https://github.com/AtaTrkgl/itu-ders-secici
    if %ERRORLEVEL% NEQ 0 (
        echo [ERROR] Failed to clone repository.
        pause
        exit /b 1
    )
    cd itu-ders-secici
    echo [INFO] Entered project directory.
)

:: 3. Check/Install Just
where just >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [INFO] 'Just' not found. Installing via Winget...
    winget install -e --id Casey.Just --accept-source-agreements --accept-package-agreements
    if %ERRORLEVEL% NEQ 0 (
        echo [ERROR] Failed to install Just.
        pause
        exit /b 1
    )
    echo [INFO] Refreshing Path variables...
    call :RefreshEnv
)

:: 4. Verify Just is now available
where just >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] 'just' command not found even after install/refresh.
    echo Please restart your terminal and try again.
    pause
    exit /b 1
)

:: 5. Run System Requirements (Git, Python, uv)
echo.
echo [INFO] Installing System Requirements...
just system-reqs

echo [INFO] Refreshing Path variables again (for new tools)...
call :RefreshEnv

:: 6. Run Project Installation
echo.
echo [INFO] Installing Project Dependencies...
just install

echo.
echo ==========================================
echo    Setup Complete!
echo    Run 'just init' to configure settings,
echo    or 'just run' to start the bot.
echo ==========================================
pause
goto :eof

:: Function to refresh environment variables from registry
:RefreshEnv
for /f "tokens=2,*" %%I in ('reg query "HKCU\Environment" /v Path') do set "UserPath=%%J"
for /f "tokens=2,*" %%I in ('reg query "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment" /v Path 2^>nul') do set "SysPath=%%J"
if defined SysPath (
    set "PATH=%SysPath%;%UserPath%"
) else (
    set "PATH=%UserPath%"
)
exit /b