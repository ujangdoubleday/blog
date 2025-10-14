@echo off
REM Blog Generator Build Script for Windows
REM Usage: build.bat [options]
REM Options: --serve, --port 3000, --no-clean, etc.

echo.
echo [92mBlog Generator Build Script[0m
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo [91mError: Virtual environment not found![0m
    echo [93mPlease run: python -m venv venv[0m
    pause
    exit /b 1
)

REM Check if virtual environment is activated
if "%VIRTUAL_ENV%"=="" (
    echo [93mActivating virtual environment...[0m
    call venv\Scripts\activate.bat
    if errorlevel 1 (
        echo [91mError: Failed to activate virtual environment![0m
        pause
        exit /b 1
    )
)

REM Check if dependencies are installed (simple check)
if not exist "venv\Lib\site-packages" (
    echo [93mInstalling dependencies...[0m
    pip install -r requirements.txt
    if errorlevel 1 (
        echo [91mError: Failed to install dependencies![0m
        pause
        exit /b 1
    )
)

REM Run the build script with all arguments passed
echo [92mRunning blog generator...[0m
python scripts\build.py %*

REM Check if build was successful
if errorlevel 1 (
    echo [91m❌ Build failed![0m
    pause
    exit /b 1
) else (
    echo [92m✅ Build completed successfully![0m
)

REM Keep window open if running with --serve
echo %* | findstr /C:"--serve" >nul
if not errorlevel 1 (
    echo.
    echo [93mPress Ctrl+C to stop the server[0m
    pause >nul
)
