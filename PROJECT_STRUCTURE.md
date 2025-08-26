# OurLibrary Project Structure - Installer-First Architecture
# File: PROJECT_STRUCTURE.md
# Path: /home/herb/Desktop/OurLibrary/PROJECT_STRUCTURE.md
# Standard: AIDEV-PascalCase-2.3
# Created: 2025-01-25
# Last Modified: 2025-01-25 08:05PM

## New Project Organization

```
OurLibrary/
├── installers/                    # Multi-OS installer files
│   ├── OurLibrary-Installer.sh    # Linux installer ✅
│   ├── OurLibrary-Setup.exe       # Windows installer (planned)
│   └── OurLibrary-Installer.dmg   # macOS installer (planned)
│
├── app/                           # Web interface files (deployed locally)
│   ├── index.html                 # Main library interface
│   ├── css/                       # Styling
│   ├── js/                        # JavaScript functionality
│   └── assets/                    # Images, icons, fonts
│
├── server/                        # Local web server files
│   ├── server.py                  # Python HTTP server
│   ├── server.js                  # Node.js server (fallback)
│   └── launch.sh/.bat            # Cross-platform launcher
│
├── website/                       # GitHub Pages marketing site
│   ├── index.html                 # Download landing page
│   ├── download.js                # OS detection & download logic
│   └── assets/                    # Marketing images, styles
│
├── archive/                       # Previous development files
│   ├── *.html                     # Old web-first interface files
│   ├── auth-system/               # Firebase auth components
│   └── previous-versions/         # Preserved development history
│
├── Data/                          # Source data and utilities
├── Docs/                          # Documentation
├── Scripts/                       # Development scripts
├── Config/                        # Configuration templates
├── library_web.db                 # Master database (10MB)
├── INSTALLER_FIRST_PLAN.md        # Architecture plan ✅
├── PROJECT_STRUCTURE.md           # This file
├── CLAUDE.md                      # Project instructions
└── README.md                      # Project overview
```

## Development Phases

### Phase 1: Enhanced Linux Installer ✅ Current Focus
- Update `installers/OurLibrary-Installer.sh`
- Create `app/` web interface files
- Create `server/` local web server
- Test complete local workflow

### Phase 2: Multi-OS Support
- Windows installer (.exe)
- macOS installer (.dmg)
- Cross-platform testing

### Phase 3: Marketing Website
- Transform GitHub Pages to download hub
- OS detection and appropriate installer download
- Demo/preview functionality

### Phase 4: Polish & Features
- Desktop integration
- Auto-updater
- Cloud sync (repurposed auth system)

## Key Files Status

✅ **Working:** `installers/OurLibrary-Installer.sh` - Creates directories, downloads DB
✅ **Working:** `library_web.db` - 10MB SQLite database
✅ **Documented:** Architecture plan and project structure
🔄 **Next:** Create app/ web interface files
🔄 **Next:** Create server/ local web server
⏳ **Later:** Multi-OS installers
⏳ **Later:** Marketing website

## Preserved Development Investment

All previous work is preserved in `archive/`:
- Firebase authentication system
- Email verification workflows
- Web interface components
- User management functionality

These will be repurposed for optional cloud sync features in Phase 4.