// File: gdrive-file-finder.js
// Path: /home/herb/Desktop/OurLibrary/JS/gdrive-file-finder.js
// Standard: AIDEV-PascalCase-2.3
// Created: 2025-08-28
// Last Modified: 2025-08-28 05:35PM

/**
 * OurLibrary Google Drive File Finder
 * Helps locate database file ID in Google Drive folders
 * Uses Google Drive API v3 to list folder contents
 */

class GoogleDriveFileFinder {
    constructor() {
        this.apiKey = null; // Would need a public API key for read-only access
        this.baseURL = 'https://www.googleapis.com/drive/v3/files';
        
        // Known folder IDs from user
        this.folders = {
            main: '1_JFXXXKoQBlfqiwSvJ3OkQ3Q8DCue3hA',
            database: '1d_LbPby6QCkJm7LYxTZjZ_D8aB_KIDUP', 
            books: '17PyEAd1I43IVxcA7LdRHNlJg4ClE0dDw'
        };
    }

    /**
     * Find the database file in the database folder
     * Looks for files named like library_web.db or similar
     */
    async findDatabaseFile() {
        try {
            console.log('Searching for database file in Google Drive folder...');
            console.log(`Database folder ID: ${this.folders.database}`);

            // List files in database folder
            const files = await this.listFolderContents(this.folders.database);
            
            if (!files || files.length === 0) {
                throw new Error('No files found in database folder');
            }

            console.log(`Found ${files.length} files in database folder:`);
            files.forEach(file => {
                console.log(`- ${file.name} (${file.id}) - ${this.formatFileSize(file.size)}`);
            });

            // Look for database files (by extension and size)
            const databaseFiles = files.filter(file => {
                const name = file.name.toLowerCase();
                const sizeMB = parseInt(file.size) / (1024 * 1024);
                
                return (name.endsWith('.db') || name.endsWith('.sqlite')) && 
                       sizeMB > 5 && sizeMB < 50; // Reasonable size range
            });

            if (databaseFiles.length === 0) {
                throw new Error('No database files found in folder');
            }

            if (databaseFiles.length > 1) {
                console.warn('Multiple database files found:', databaseFiles.map(f => f.name));
            }

            // Return the first/best match
            const dbFile = databaseFiles[0];
            console.log(`Selected database file: ${dbFile.name} (${dbFile.id})`);
            
            return {
                fileId: dbFile.id,
                fileName: dbFile.name,
                fileSize: parseInt(dbFile.size),
                fileSizeMB: Math.round(parseInt(dbFile.size) / (1024 * 1024) * 10) / 10,
                downloadUrl: `https://drive.google.com/uc?export=download&id=${dbFile.id}`,
                viewUrl: `https://drive.google.com/file/d/${dbFile.id}/view`
            };

        } catch (error) {
            console.error('Error finding database file:', error);
            
            // Return fallback information for manual setup
            return {
                fileId: 'MANUAL_SETUP_REQUIRED',
                fileName: 'library_web.db',
                error: error.message,
                manualInstructions: [
                    `1. Visit https://drive.google.com/drive/folders/${this.folders.database}`,
                    '2. Find the database file (usually library_web.db)',
                    '3. Right-click and select "Get link"', 
                    '4. Copy the file ID from the URL (between /d/ and /view)',
                    '5. Update the configuration with the real file ID'
                ]
            };
        }
    }

    /**
     * List contents of a Google Drive folder
     */
    async listFolderContents(folderId) {
        try {
            // Note: This requires a public API key for read-only access
            // For production, you would set up a Google Cloud project and get an API key
            
            const query = encodeURIComponent(`'${folderId}' in parents and trashed=false`);
            const fields = 'files(id,name,size,mimeType,modifiedTime)';
            
            // This would work with a real API key:
            // const url = `${this.baseURL}?q=${query}&fields=${fields}&key=${this.apiKey}`;
            
            // For now, we'll simulate the API call
            throw new Error('Google Drive API key required for folder listing');
            
        } catch (error) {
            console.error('Error listing folder contents:', error);
            return null;
        }
    }

    /**
     * Generate direct download URLs for testing
     */
    generateTestDownloadUrls() {
        const possibleFileIds = [
            // These would be found by actually listing the folder contents
            'PLACEHOLDER_DATABASE_FILE_ID_1',
            'PLACEHOLDER_DATABASE_FILE_ID_2'
        ];

        return possibleFileIds.map(fileId => ({
            fileId: fileId,
            downloadUrl: `https://drive.google.com/uc?export=download&id=${fileId}`,
            viewUrl: `https://drive.google.com/file/d/${fileId}/view`
        }));
    }

    /**
     * Test if a Google Drive file is accessible
     */
    async testFileAccess(fileId) {
        try {
            const downloadUrl = `https://drive.google.com/uc?export=download&id=${fileId}`;
            
            // Make a HEAD request to check if file exists and is accessible
            const response = await fetch(downloadUrl, { method: 'HEAD' });
            
            return {
                accessible: response.ok,
                status: response.status,
                contentLength: response.headers.get('content-length'),
                contentType: response.headers.get('content-type')
            };

        } catch (error) {
            return {
                accessible: false,
                error: error.message
            };
        }
    }

    /**
     * Format file size for display
     */
    formatFileSize(bytes) {
        if (!bytes) return 'Unknown size';
        
        const sizes = ['B', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(1024));
        
        return `${Math.round(bytes / Math.pow(1024, i) * 10) / 10} ${sizes[i]}`;
    }

    /**
     * Get folder information
     */
    getFolderInfo() {
        return {
            main: {
                id: this.folders.main,
                url: `https://drive.google.com/drive/folders/${this.folders.main}`,
                description: 'Main OurLibrary folder'
            },
            database: {
                id: this.folders.database,
                url: `https://drive.google.com/drive/folders/${this.folders.database}`,
                description: 'Database files folder'
            },
            books: {
                id: this.folders.books,
                url: `https://drive.google.com/drive/folders/${this.folders.books}`,
                description: 'PDF books folder'
            }
        };
    }

    /**
     * Generate configuration update for found database
     */
    generateConfigUpdate(databaseInfo) {
        return {
            database_file_id: databaseInfo.fileId,
            database_filename: databaseInfo.fileName,
            database_size_mb: databaseInfo.fileSizeMB,
            download_url: databaseInfo.downloadUrl,
            last_updated: new Date().toISOString().split('T')[0]
        };
    }
}

// Create global instance
window.gdriveFileFinder = new GoogleDriveFileFinder();

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = GoogleDriveFileFinder;
}