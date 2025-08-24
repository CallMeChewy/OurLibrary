# Remote User Setup Guide for AndyLibrary

## For Library Owner (You)

### Step 1: Share Your Google Drive Folder

1. **Open Google Drive** and locate your AndyLibrary folder (containing `MyLibrary.db`)
2. **Right-click the folder** → Select "Share"
3. **Click "Change to anyone with the link"**
4. **Set permissions to "Viewer"** (they only need to read/download)
5. **Copy the share link** - it will look like:
   ```
   https://drive.google.com/drive/folders/1A2B3C4D5E6F7G8H9I0J1K2L3M4N5O6P?usp=sharing
   ```
6. **Send this link to the remote user**

### Step 2: What to Tell the Remote User

Send them this message:
```
Hi! I'm sharing my educational library with you. Here's how to access it:

1. Download the AndyLibrary Windows app from [your distribution method]
2. Run the app - it will ask for a setup
3. Paste this link when prompted: [YOUR_GOOGLE_DRIVE_LINK]
4. Enter my name as the library owner: [YOUR_NAME]
5. The app will automatically download and setup the library

The library contains [X] educational books across multiple subjects.
```

### Step 3: Verify Your Folder Structure

Make sure your Google Drive folder contains:
```
📁 Your Shared Folder/
  └── MyLibrary.db (the main database file)
  └── (optional) Other library files
```

---

## For Remote User (Windows Machine)

### What You Need

1. **The Google Drive share link** from the library owner
2. **The library owner's name** (for display purposes)
3. **Internet connection** for initial setup

### Setup Process

1. **Run the AndyLibrary Windows EXE**
2. **Setup Page Opens** - Enter:
   - **Google Drive Link**: Paste the share link you received
   - **Owner Name**: Enter the library owner's name
3. **Click "Connect to Library"**
4. **Wait for Download** - The app will:
   - Verify the shared folder is accessible
   - Find the MyLibrary.db database
   - Download it to your computer
   - Set up your local library environment
5. **Access Library** - Once setup is complete, you can browse the books

### No Google Account Required

- **You don't need a Google account** - the folder is publicly accessible
- **No authentication needed** - just the share link
- **Works offline** after initial download

### Troubleshooting

**"Cannot access shared folder"**:
- Ask the library owner to verify the folder is shared with "Anyone with the link"
- Check your internet connection

**"MyLibrary.db not found"**:
- Ask the library owner to confirm the database file is in the shared folder
- Verify they shared the correct folder

**"Download failed"**:
- Check internet connection
- Try again - sometimes Google Drive has temporary issues
- Make sure you have enough disk space

---

## Technical Details

### How It Works

1. **Share Link Analysis**: The app extracts the Google Drive folder ID from the share URL
2. **Public API Access**: Uses Google Drive's public API (no authentication needed)
3. **Database Discovery**: Searches for `MyLibrary.db` in the shared folder
4. **Direct Download**: Downloads the database file directly from Google Drive
5. **Local Setup**: Creates a local library environment with the downloaded data

### Security & Privacy

- **Read-Only Access**: Remote users can only view/download, not modify your files
- **No Account Access**: They cannot see your other Google Drive files
- **Public Folder Only**: Only the specific folder you share is accessible
- **Local Storage**: Database is downloaded and stored locally on their machine

### Network Requirements

- **Initial Setup**: Internet required to download database (~10-50MB typical)
- **Ongoing Use**: Works completely offline after setup
- **Updates**: User would need new share link if you update the database

---

## Advanced Options

### Multiple Database Versions

If you have multiple versions:
```
📁 Shared Folder/
  ├── MyLibrary.db (current version)
  ├── MyLibrary_backup.db (backup)
  └── MyLibrary_v2.db (newer version)
```

The app will automatically use `MyLibrary.db` first, or the first `.db` file found.

### Custom Folder Structure

The app searches for any `.db` file in the shared folder, so you can organize however you prefer:
```
📁 Educational Library/
  ├── Database/
  │   └── MyLibrary.db
  └── Documentation/
      └── README.txt
```

### Updating the Database

When you update your database:
1. **Replace** `MyLibrary.db` in the shared folder
2. **Remote users** can re-run setup to get the latest version
3. **No new share link needed** - same link works

---

## Summary

**For You (Library Owner)**:
- Share Google Drive folder with "Anyone with the link" 
- Send share link to remote user
- No additional setup required

**For Remote User**:
- Just needs the share link you provide
- No Google account required
- No manual file downloads
- Automatic setup through the app

The system is designed to be **simple and secure** - remote users get read-only access to your educational content without any complex authentication or account requirements.