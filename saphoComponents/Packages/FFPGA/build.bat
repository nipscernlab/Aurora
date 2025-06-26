@echo off
REM Enhanced Fractal Visualizer - Windows Build Script
REM Usage: build.bat [pyinstaller|cx_freeze|nuitka] [debug]

setlocal enabledelayedexpansion

echo ================================================
echo Enhanced Fractal Visualizer Build Script
echo ================================================

REM Set default values
set BUILD_TYPE=pyinstaller
set DEBUG_FLAG=
set VERBOSE_FLAG=

REM Parse command line arguments
if not "%1"=="" set BUILD_TYPE=%1
if "%2"=="debug" set DEBUG_FLAG=--debug
if "%2"=="verbose" set VERBOSE_FLAG=--verbose
if "%3"=="verbose" set VERBOSE_FLAG=--verbose

echo Build Type: %BUILD_TYPE%
echo Debug Mode: %DEBUG_FLAG%
echo Verbose: %VERBOSE_FLAG%
echo.

REM Check Python installation
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ and add it to your PATH
    pause
    exit /b 1
)

echo Python installation found
python --version

REM Check pip installation
pip --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: pip is not available
    echo Please ensure pip is installed with Python
    pause
    exit /b 1
)

echo pip installation found
echo.

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
    echo Virtual environment created successfully
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)

echo Virtual environment activated
echo.

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip
if errorlevel 1 (
    echo WARNING: Failed to upgrade pip, continuing...
)

REM Install requirements
echo Installing requirements...
if exist "requirements.txt" (
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ERROR: Failed to install requirements
        pause
        exit /b 1
    )
    echo Requirements installed successfully
) else (
    echo WARNING: requirements.txt not found, installing basic dependencies...
    pip install customtkinter pillow numpy scipy pyinstaller
)

echo.

REM Ensure main script exists
if not exist "fractal_visualizer.py" (
    echo ERROR: Main script 'fractal_visualizer.py' not found
    echo Please ensure the main Python file is in the current directory
    pause
    exit /b 1
)

REM Run the build script
echo Starting build process...
echo Command: python build.py --build-type %BUILD_TYPE% %DEBUG_FLAG% %VERBOSE_FLAG%
echo.

python build.py --build-type %BUILD_TYPE% %DEBUG_FLAG% %VERBOSE_FLAG%

if errorlevel 1 (
    echo.
    echo =====================================
    echo BUILD FAILED!
    echo =====================================
    echo Check the logs directory for details
    echo.
    pause
    exit /b 1
) else (
    echo.
    echo =====================================
    echo BUILD COMPLETED SUCCESSFULLY!
    echo =====================================
    echo.
    echo Executable location: dist\
    echo Build report: dist\BUILD_REPORT.md
    echo Logs directory: logs\
    echo.
    
    REM Open dist directory
    if exist "dist" (
        echo Opening dist directory...
        start "" explorer "dist"
    )
    
    echo.
    echo Press any key to exit...
    pause >nul
)

REM Deactivate virtual environment
deactivate

endlocal