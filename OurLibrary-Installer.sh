#!/bin/bash
# File: OurLibrary-Installer.sh
# Path: /home/herb/Desktop/OurLibrary/OurLibrary-Installer.sh
# Standard: AIDEV-PascalCase-2.3
# Created: 2025-01-25
# Last Modified: 2025-01-25 07:52PM

# OurLibrary Installation Script
# "Getting education into the hands of people who can least afford it"
# Email: ProjectHimalaya@BowersWorld.com

echo "=============================================="
echo "🚀 OurLibrary Installation Script"
echo "=============================================="
echo "📚 Setting up your personal educational library"
echo ""

# Get user's home directory
HOME_DIR="$HOME"
LIBRARY_DIR="$HOME_DIR/OurLibrary"

# Check if directory already exists
if [ -d "$LIBRARY_DIR" ]; then
    echo "⚠️  OurLibrary directory already exists at: $LIBRARY_DIR"
    echo "Do you want to continue? This will not overwrite existing files. (y/n)"
    read -r response
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        echo "Installation cancelled."
        exit 0
    fi
fi

echo "🏗️  Creating OurLibrary directory structure..."

# Create main OurLibrary directory
mkdir -p "$LIBRARY_DIR"
echo "✅ Created: $LIBRARY_DIR"

# Create subdirectories  
mkdir -p "$LIBRARY_DIR/database"
mkdir -p "$LIBRARY_DIR/downloads"
mkdir -p "$LIBRARY_DIR/user_data"
mkdir -p "$LIBRARY_DIR/cache"

echo "✅ Created subdirectory: $LIBRARY_DIR/database"
echo "✅ Created subdirectory: $LIBRARY_DIR/downloads" 
echo "✅ Created subdirectory: $LIBRARY_DIR/user_data"
echo "✅ Created subdirectory: $LIBRARY_DIR/cache"

# Download database if not exists
DATABASE_FILE="$LIBRARY_DIR/database/library_catalog.db"
if [ ! -f "$DATABASE_FILE" ]; then
    echo ""
    echo "📥 Downloading book catalog database..."
    
    # Check if curl or wget is available
    if command -v curl > /dev/null 2>&1; then
        curl -L -o "$DATABASE_FILE" "https://callmechewy.github.io/OurLibrary/library_web.db"
    elif command -v wget > /dev/null 2>&1; then
        wget -O "$DATABASE_FILE" "https://callmechewy.github.io/OurLibrary/library_web.db"
    else
        echo "⚠️  Neither curl nor wget found. Please download library_web.db manually"
        echo "   URL: https://callmechewy.github.io/OurLibrary/library_web.db"
        echo "   Save to: $DATABASE_FILE"
    fi
    
    if [ -f "$DATABASE_FILE" ]; then
        echo "✅ Database downloaded successfully"
    else
        echo "⚠️  Database download may have failed. Check internet connection."
    fi
else
    echo "✅ Database already exists: $DATABASE_FILE"
fi

# Create configuration file
CONFIG_FILE="$LIBRARY_DIR/user_data/config.json"
if [ ! -f "$CONFIG_FILE" ]; then
    cat > "$CONFIG_FILE" << EOF
{
  "version": "1.0.0",
  "setupDate": "$(date -Iseconds)",
  "libraryPath": "$LIBRARY_DIR",
  "theme": "default",
  "autoUpdate": true
}
EOF
    echo "✅ Created configuration file"
fi

# Create README with instructions
cat > "$LIBRARY_DIR/README.txt" << EOF
OurLibrary - Personal Educational Library
========================================

Installation completed: $(date)
Library location: $LIBRARY_DIR

📁 Directory Structure:
   database/   - Book catalog database files
   downloads/  - Downloaded books for offline reading  
   user_data/  - Reading progress and preferences
   cache/      - Temporary files and thumbnails

🌐 Access Your Library:
   Open: https://callmechewy.github.io/OurLibrary/

📧 Support: ProjectHimalaya@BowersWorld.com
🎯 Mission: "Getting education into the hands of people who can least afford it"

Enjoy your personal library! 📚
EOF

# Set appropriate permissions
chmod 755 "$LIBRARY_DIR"
chmod 755 "$LIBRARY_DIR/database" "$LIBRARY_DIR/downloads" "$LIBRARY_DIR/user_data" "$LIBRARY_DIR/cache"
chmod 644 "$LIBRARY_DIR/README.txt"

echo ""
echo "=============================================="
echo "🎉 OurLibrary Installation Complete!"
echo "=============================================="
echo "📍 Your library is located at: $LIBRARY_DIR"
echo "📚 Access your library: https://callmechewy.github.io/OurLibrary/"
echo ""
echo "Directory contents:"
ls -la "$LIBRARY_DIR"
echo ""
echo "✨ Your personal educational library is ready to use!"
echo "=============================================="