#!/bin/bash
# OurLibrary Directory Setup Script
# This script creates the real ~/OurLibrary/ directory structure

echo "🏠 Creating OurLibrary directory structure..."

# Get user's home directory
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

# Create a README file
cat > "$LIBRARY_DIR/README.txt" << EOF
OurLibrary Directory Structure
=============================

This directory was created by OurLibrary to store your books and data:

📁 database/   - Book catalog database files
📁 downloads/  - Downloaded books for offline reading
📁 user_data/  - Reading progress and preferences
📁 cache/      - Temporary files and thumbnails

Your library location: $LIBRARY_DIR
EOF

echo "✅ OurLibrary directory structure created successfully at: $LIBRARY_DIR"
echo ""
echo "Directory contents:"
ls -la "$LIBRARY_DIR"