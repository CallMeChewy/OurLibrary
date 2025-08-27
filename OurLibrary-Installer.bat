@echo off
REM File: OurLibrary-Installer.bat
REM Path: /home/herb/Desktop/OurLibrary/OurLibrary-Installer.bat
REM Standard: AIDEV-PascalCase-2.3
REM Created: 2025-08-27
REM Last Modified: 2025-08-27 03:02PM

REM OurLibrary Windows Installation Script
REM "Getting education into the hands of people who can least afford it"
REM Email: ProjectHimalaya@BowersWorld.com

echo ==============================================
echo 🚀 OurLibrary Windows Installation Script
echo ==============================================
echo 📚 Setting up your personal educational library
echo.

REM Get user's home directory
set "HOME_DIR=%USERPROFILE%"
set "LIBRARY_DIR=%HOME_DIR%\OurLibrary"

REM Check if directory already exists
if exist "%LIBRARY_DIR%" (
    echo ⚠️  OurLibrary directory already exists at: %LIBRARY_DIR%
    set /p response="Do you want to continue? This will not overwrite existing files. (y/n): "
    if /i not "%response%"=="y" (
        echo Installation cancelled.
        pause
        exit /b 0
    )
)

echo 🏗️  Creating OurLibrary directory structure...

REM Create main OurLibrary directory
mkdir "%LIBRARY_DIR%" 2>nul
echo ✅ Created: %LIBRARY_DIR%

REM Create subdirectories  
mkdir "%LIBRARY_DIR%\database" 2>nul
mkdir "%LIBRARY_DIR%\downloads" 2>nul
mkdir "%LIBRARY_DIR%\user_data" 2>nul
mkdir "%LIBRARY_DIR%\cache" 2>nul

echo ✅ Created subdirectory: %LIBRARY_DIR%\database
echo ✅ Created subdirectory: %LIBRARY_DIR%\downloads
echo ✅ Created subdirectory: %LIBRARY_DIR%\user_data
echo ✅ Created subdirectory: %LIBRARY_DIR%\cache

REM Download database if not exists
set "DATABASE_FILE=%LIBRARY_DIR%\database\library_catalog.db"
if not exist "%DATABASE_FILE%" (
    echo.
    echo 📥 Downloading book catalog database...
    
    REM Try PowerShell first (Windows 7+), then fallback to certutil
    powershell -Command "try { Invoke-WebRequest -Uri 'https://callmechewy.github.io/OurLibrary/library_web.db' -OutFile '%DATABASE_FILE%' } catch { exit 1 }" 2>nul
    if errorlevel 1 (
        echo Trying alternative download method...
        certutil -urlcache -split -f "https://callmechewy.github.io/OurLibrary/library_web.db" "%DATABASE_FILE%" >nul 2>&1
    )
    
    if exist "%DATABASE_FILE%" (
        echo ✅ Database downloaded successfully
    ) else (
        echo ⚠️  Database download failed. Please check internet connection.
        echo    URL: https://callmechewy.github.io/OurLibrary/library_web.db
        echo    Save to: %DATABASE_FILE%
    )
) else (
    echo ✅ Database already exists: %DATABASE_FILE%
)

REM Create configuration file
set "CONFIG_FILE=%LIBRARY_DIR%\user_data\config.json"
if not exist "%CONFIG_FILE%" (
    (
        echo {
        echo   "version": "1.0.0",
        echo   "setupDate": "%date% %time%",
        echo   "libraryPath": "%LIBRARY_DIR%",
        echo   "platform": "windows",
        echo   "theme": "default",
        echo   "autoUpdate": true
        echo }
    ) > "%CONFIG_FILE%"
    echo ✅ Created configuration file
)

REM Create README with instructions
(
    echo OurLibrary - Personal Educational Library
    echo ========================================
    echo.
    echo Installation completed: %date% %time%
    echo Library location: %LIBRARY_DIR%
    echo Platform: Windows
    echo.
    echo 📁 Directory Structure:
    echo    database\   - Book catalog database files
    echo    downloads\  - Downloaded books for offline reading  
    echo    user_data\  - Reading progress and preferences
    echo    cache\      - Temporary files and thumbnails
    echo.
    echo 🌐 Access Your Library:
    echo    Open: https://callmechewy.github.io/OurLibrary/
    echo.
    echo 📧 Support: ProjectHimalaya@BowersWorld.com
    echo 🎯 Mission: "Getting education into the hands of people who can least afford it"
    echo.
    echo Enjoy your personal library! 📚
) > "%LIBRARY_DIR%\README.txt"

echo.
echo ==============================================
echo 🎉 OurLibrary Installation Complete!
echo ==============================================
echo 📍 Your library is located at: %LIBRARY_DIR%
echo 📚 Access your library: https://callmechewy.github.io/OurLibrary/
echo.
echo Directory contents:
dir /B "%LIBRARY_DIR%"
echo.
echo ✨ Your personal educational library is ready to use!
echo ==============================================
echo.
echo Press any key to open your library folder...
pause >nul
explorer "%LIBRARY_DIR%"