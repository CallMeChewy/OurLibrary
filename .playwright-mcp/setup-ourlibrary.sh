#!/bin/bash
# OurLibrary Directory Setup Script
echo "🏠 Creating OurLibrary directory structure..."

HOME_DIR="$HOME"
LIBRARY_DIR="$HOME_DIR/OurLibrary"

# Create main OurLibrary directory
mkdir -p "$LIBRARY_DIR"
echo "📁 Created: $LIBRARY_DIR"

# Create subdirectories  
mkdir -p "$LIBRARY_DIR/database"
mkdir -p "$LIBRARY_DIR/downloads"
mkdir -p "$LIBRARY_DIR/user_data"
mkdir -p "$LIBRARY_DIR/cache"

echo "📁 Created subdirectory: $LIBRARY_DIR/database"
echo "📁 Created subdirectory: $LIBRARY_DIR/downloads" 
echo "📁 Created subdirectory: $LIBRARY_DIR/user_data"
echo "📁 Created subdirectory: $LIBRARY_DIR/cache"

# Create README
cat > "$LIBRARY_DIR/README.txt" << EOF
OurLibrary Directory Structure
=============================

📁 database/   - Book catalog database files
📁 downloads/  - Downloaded books for offline reading  
📁 user_data/  - Reading progress and preferences
📁 cache/      - Temporary files and thumbnails

Your library location: $LIBRARY_DIR
EOF

echo "✅ OurLibrary directory structure created at: $LIBRARY_DIR"
ls -la "$LIBRARY_DIR"