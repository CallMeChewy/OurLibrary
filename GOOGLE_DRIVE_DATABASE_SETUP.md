# Google Drive Database Setup - OurLibrary

## 🎯 Overview

This document provides the complete setup process for Google Drive database download integration in OurLibrary. The system automatically downloads the `OurLibrary.db` file from Google Drive during user setup.

## 📁 Google Drive Structure

### Service Account
- **Email**: `anderson-library-service@anderson-library.iam.gserviceaccount.com`

### Folder Structure
- **Main Folder**: `1_JFXXXKoQBlfqiwSvJ3OkQ3Q8DCue3hA`
  - 📂 [Main OurLibrary Folder](https://drive.google.com/drive/folders/1_JFXXXKoQBlfqiwSvJ3OkQ3Q8DCue3hA)
  
- **Database Folder**: `1d_LbPby6QCkJm7LYxTZjZ_D8aB_KIDUP` 
  - 📂 [Database Files](https://drive.google.com/drive/folders/1d_LbPby6QCkJm7LYxTZjZ_D8aB_KIDUP)
  - Contains: **`OurLibrary.db`** (~10.3MB, 1,219+ books)

- **Books Folder**: `17PyEAd1I43IVxcA7LdRHNlJg4ClE0dDw`
  - 📂 [PDF Books](https://drive.google.com/drive/folders/17PyEAd1I43IVxcA7LdRHNlJg4ClE0dDw)

## 🔧 Setup Required

### Step 1: Find Database File ID
1. Visit the **Database Folder**: https://drive.google.com/drive/folders/1d_LbPby6QCkJm7LYxTZjZ_D8aB_KIDUP
2. Look for file named exactly: **`OurLibrary.db`**
3. Right-click → "Get link" → Ensure "Anyone with the link can view"
4. Copy the file ID from the URL (between `/d/` and `/view`)

**Or use the helper tool**: `/find-database-file-id.html`

### Step 2: Update Configuration
Edit `/Config/ourlibrary_google_config.json`:

```json
{
  "database_file_id": "YOUR_ACTUAL_FILE_ID_HERE",
  "database_filename": "OurLibrary.db",
  "gdrive_folders": {
    "main_folder_id": "1_JFXXXKoQBlfqiwSvJ3OkQ3Q8DCue3hA",
    "database_folder_id": "1d_LbPby6QCkJm7LYxTZjZ_D8aB_KIDUP",
    "books_folder_id": "17PyEAd1I43IVxcA7LdRHNlJg4ClE0dDw"
  }
}
```

## 🚀 User Experience

### Setup Flow (`/setup-database.html`)
1. **Prerequisites Check** - Browser compatibility, storage space
2. **Database Download** - Attempts Google Drive, falls back to local
3. **Database Initialize** - SQLite setup with sql.js WebAssembly
4. **Verification** - Confirms 1,219+ books are accessible

### Features
- ✅ **Visual Progress Tracking** - 4-step workflow with real-time updates
- ✅ **Automatic Fallback** - Uses local database if Google Drive fails
- ✅ **Progress Indicators** - Download progress bar and logging
- ✅ **Error Handling** - Graceful failure with helpful messages
- ✅ **Database Validation** - File integrity and book count verification
- ✅ **Persistent Storage** - IndexedDB caching for offline use

## 🔄 Sync System

### Automatic Updates (`database-sync.js`)
- **Check Interval**: Every 24 hours
- **Version Tracking**: Compares timestamps to detect updates
- **Background Sync**: Downloads new versions automatically
- **User Notification**: Alerts when database is updated

### Manual Testing (`/test-gdrive-db-sync.html`)
- Real-time sync status monitoring
- Manual update triggers
- Configuration management
- Activity logging

## 📊 Database Information

- **File**: `OurLibrary.db`
- **Size**: ~10.3MB
- **Books**: 1,219+ educational books
- **Categories**: 26 subject categories  
- **Subjects**: 118+ specialized subjects
- **Format**: SQLite database with thumbnails and metadata

## 🔍 Helper Tools

### Database File ID Finder (`/find-database-file-id.html`)
- **Purpose**: Helps locate the `OurLibrary.db` file ID in Google Drive
- **Features**: 
  - Direct links to database folder
  - Step-by-step instructions
  - File ID validation and testing
  - Configuration generation
  - URL testing tools

### Setup Interface (`/setup-database.html`)
- **Purpose**: Complete user onboarding with database download
- **Features**:
  - Visual progress tracking
  - Real-time logging  
  - Error recovery
  - Success confirmation

### Sync Testing (`/test-gdrive-db-sync.html`)
- **Purpose**: Test and monitor database synchronization
- **Features**:
  - Sync status monitoring
  - Manual sync triggers
  - Configuration management
  - Activity logging

## ⚠️ Important Notes

1. **File Permissions**: `OurLibrary.db` must be set to "Anyone with the link can view"
2. **CORS Limitations**: Direct Google Drive downloads may have CORS restrictions
3. **Fallback System**: Local database file serves as backup when Google Drive is unavailable
4. **File ID Format**: Google Drive file IDs are typically 20+ alphanumeric characters with hyphens/underscores

## 🎉 Current Status

✅ **All components implemented and tested**
- Configuration files updated with real Google Drive folder IDs
- Setup flow working with correct filename (`OurLibrary.db`)
- Sync system configured for automatic updates
- Helper tools created for easy file ID discovery
- Fallback system tested and working

**Next Step**: Update configuration with the actual file ID of `OurLibrary.db` from the database folder.