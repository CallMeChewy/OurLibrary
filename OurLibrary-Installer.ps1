# File: OurLibrary-Installer.ps1
# Path: /home/herb/Desktop/OurLibrary/OurLibrary-Installer.ps1
# Standard: AIDEV-PascalCase-2.3
# Created: 2025-08-27
# Last Modified: 2025-08-27 03:05PM

# OurLibrary PowerShell Installation Script
# "Getting education into the hands of people who can least afford it"
# Email: ProjectHimalaya@BowersWorld.com

Write-Host "==============================================" -ForegroundColor Cyan
Write-Host "🚀 OurLibrary PowerShell Installation Script" -ForegroundColor Yellow
Write-Host "==============================================" -ForegroundColor Cyan
Write-Host "📚 Setting up your personal educational library" -ForegroundColor Green
Write-Host ""

# Get user's home directory
$HomeDir = $env:USERPROFILE
$LibraryDir = Join-Path $HomeDir "OurLibrary"

# Check if directory already exists
if (Test-Path $LibraryDir) {
    Write-Host "⚠️  OurLibrary directory already exists at: $LibraryDir" -ForegroundColor Yellow
    $response = Read-Host "Do you want to continue? This will not overwrite existing files. (y/n)"
    if ($response -ne "y" -and $response -ne "Y") {
        Write-Host "Installation cancelled." -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 0
    }
}

Write-Host "🏗️  Creating OurLibrary directory structure..." -ForegroundColor Blue

# Create main OurLibrary directory
New-Item -ItemType Directory -Force -Path $LibraryDir | Out-Null
Write-Host "✅ Created: $LibraryDir" -ForegroundColor Green

# Create subdirectories  
$subdirs = @("database", "downloads", "user_data", "cache")
foreach ($subdir in $subdirs) {
    $path = Join-Path $LibraryDir $subdir
    New-Item -ItemType Directory -Force -Path $path | Out-Null
    Write-Host "✅ Created subdirectory: $path" -ForegroundColor Green
}

# Download database if not exists
$DatabaseFile = Join-Path (Join-Path $LibraryDir "database") "library_catalog.db"
if (-not (Test-Path $DatabaseFile)) {
    Write-Host ""
    Write-Host "📥 Downloading book catalog database..." -ForegroundColor Blue
    
    try {
        # Use modern Invoke-WebRequest
        $ProgressPreference = 'SilentlyContinue'  # Hide progress bar for speed
        Invoke-WebRequest -Uri "https://callmechewy.github.io/OurLibrary/library_web.db" -OutFile $DatabaseFile -UseBasicParsing
        Write-Host "✅ Database downloaded successfully" -ForegroundColor Green
    }
    catch {
        Write-Host "⚠️  Database download failed: $($_.Exception.Message)" -ForegroundColor Yellow
        Write-Host "   URL: https://callmechewy.github.io/OurLibrary/library_web.db" -ForegroundColor Gray
        Write-Host "   Save to: $DatabaseFile" -ForegroundColor Gray
    }
} else {
    Write-Host "✅ Database already exists: $DatabaseFile" -ForegroundColor Green
}

# Create configuration file
$ConfigFile = Join-Path (Join-Path $LibraryDir "user_data") "config.json"
if (-not (Test-Path $ConfigFile)) {
    $config = @{
        version = "1.0.0"
        setupDate = (Get-Date).ToString("o")
        libraryPath = $LibraryDir
        platform = "windows"
        theme = "default"
        autoUpdate = $true
    } | ConvertTo-Json -Depth 2
    
    $config | Out-File -FilePath $ConfigFile -Encoding UTF8
    Write-Host "✅ Created configuration file" -ForegroundColor Green
}

# Create README with instructions
$ReadmeContent = @"
OurLibrary - Personal Educational Library
========================================

Installation completed: $(Get-Date)
Library location: $LibraryDir
Platform: Windows PowerShell

📁 Directory Structure:
   database\   - Book catalog database files
   downloads\  - Downloaded books for offline reading  
   user_data\  - Reading progress and preferences
   cache\      - Temporary files and thumbnails

🌐 Access Your Library:
   Open: https://callmechewy.github.io/OurLibrary/

📧 Support: ProjectHimalaya@BowersWorld.com
🎯 Mission: "Getting education into the hands of people who can least afford it"

Enjoy your personal library! 📚
"@

$ReadmeFile = Join-Path $LibraryDir "README.txt"
$ReadmeContent | Out-File -FilePath $ReadmeFile -Encoding UTF8

Write-Host ""
Write-Host "==============================================" -ForegroundColor Cyan
Write-Host "🎉 OurLibrary Installation Complete!" -ForegroundColor Yellow
Write-Host "==============================================" -ForegroundColor Cyan
Write-Host "📍 Your library is located at: $LibraryDir" -ForegroundColor Green
Write-Host "📚 Access your library: https://callmechewy.github.io/OurLibrary/" -ForegroundColor Blue
Write-Host ""
Write-Host "Directory contents:" -ForegroundColor White
Get-ChildItem $LibraryDir | Format-Table Name, Length, LastWriteTime -AutoSize
Write-Host ""
Write-Host "✨ Your personal educational library is ready to use!" -ForegroundColor Yellow
Write-Host "==============================================" -ForegroundColor Cyan
Write-Host ""

# Offer to open the library folder
$openFolder = Read-Host "Would you like to open the library folder? (y/n)"
if ($openFolder -eq "y" -or $openFolder -eq "Y") {
    Start-Process "explorer.exe" -ArgumentList $LibraryDir
}

Write-Host "Installation complete. Press Enter to exit..." -ForegroundColor Green
Read-Host