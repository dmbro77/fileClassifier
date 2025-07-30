@echo off
chcp 936 >nul
setlocal enabledelayedexpansion

:: File Classifier Packaging Script - EXE Version
:: This script packages the Python project into a standalone executable file

:: Set variables
set APP_NAME_EN=FileClassifier
set VERSION=1.0.0
set DIST_DIR=dist
set BUILD_DIR=build
set SPEC_DIR=spec

:: Display packaging information
echo Starting to package %APP_NAME_EN% v%VERSION% as executable...

:: Check if PyInstaller is installed
pip show pyinstaller >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Installing PyInstaller...
    pip install pyinstaller
    if %ERRORLEVEL% NEQ 0 (
        echo PyInstaller installation failed, please install manually and try again.
        exit /b 1
    )
)

:: Install project dependencies
echo Installing project dependencies...
pip install -r requirements.txt
if %ERRORLEVEL% NEQ 0 (
    echo Dependency installation failed, please check requirements.txt file.
    exit /b 1
)

:: Install Pillow for icon conversion
echo Installing Pillow for icon conversion...
pip install Pillow
if %ERRORLEVEL% NEQ 0 (
    echo Pillow installation failed, please install manually and try again.
    exit /b 1
)

:: Clean old build files
echo Cleaning old build files...
if exist "%DIST_DIR%" (
    rmdir /s /q "%DIST_DIR%"
)

if exist "%BUILD_DIR%" (
    rmdir /s /q "%BUILD_DIR%"
)

if exist "%SPEC_DIR%" (
    rmdir /s /q "%SPEC_DIR%"
)

:: Use PyInstaller to package the application
echo Packaging application with PyInstaller...
pyinstaller --noconfirm --onefile --windowed --icon=icon.png --name="%APP_NAME_EN%" --add-data="icon.png;." main.py

:: Check if packaging was successful
if %ERRORLEVEL% NEQ 0 (
    echo Packaging failed, please check error messages.
    exit /b 1
)

echo.
echo Packaging complete!
echo Executable file is located at: %DIST_DIR%\%APP_NAME_EN%.exe
echo.

pause