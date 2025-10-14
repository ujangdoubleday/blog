@echo off
REM Blog Generator Installation Script for Windows
REM This script will setup virtual environment and install dependencies

echo.
echo [96m==================================
echo    Blog Generator Installation
echo ==================================[0m
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [91mError: Python is not installed![0m
    echo [93mPlease install Python 3.8+ first.[0m
    pause
    exit /b 1
)

echo [93mUsing Python:[0m
python --version
echo.

REM Check if virtual environment already exists
if exist "venv" (
    echo [93mVirtual environment already exists. Skipping creation...[0m
) else (
    echo [93mCreating virtual environment...[0m
    python -m venv venv
    if errorlevel 1 (
        echo [91mError: Failed to create virtual environment![0m
        echo [93mMake sure you have venv module installed.[0m
        pause
        exit /b 1
    )
    echo [92m✅ Virtual environment created successfully![0m
)

echo.

REM Activate virtual environment
echo [93mActivating virtual environment...[0m
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo [91mError: Failed to activate virtual environment![0m
    pause
    exit /b 1
)
echo [92m✅ Virtual environment activated![0m

echo.

REM Install dependencies
echo [93mInstalling dependencies...[0m
python -m pip install --upgrade pip
pip install -r requirements.txt
if errorlevel 1 (
    echo [91mError: Failed to install dependencies![0m
    pause
    exit /b 1
)
echo [92m✅ Dependencies installed successfully![0m

echo.
echo [96m==================================
echo    Installation Complete! 🎉
echo ==================================[0m
echo.

echo [92mNext steps:[0m
echo 1. Configure your site: [93mconfig/config.yaml[0m
echo 2. Create your first post: [93mcontent/posts/my-post.md[0m
echo 3. Build your blog: [93mbuild.bat[0m
echo 4. Serve locally: [93mbuild.bat --serve[0m

echo.
echo [96mHappy blogging! 📝[0m
echo.
pause
