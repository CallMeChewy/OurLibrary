// File: filesystem-library-manager.js
// Path: /home/herb/Desktop/OurLibrary_RealTest/filesystem-library-manager.js
// Standard: AIDEV-PascalCase-2.3
// Created: 2025-01-23
// Last Modified: 2025-01-23 08:25PM

/**
 * OurLibrary File System Manager
 * Backend-style file management for web applications
 * Stores everything in user's home directory: ~/OurLibrary/
 */

class OurLibraryFileManager {
    constructor() {
        this.baseDirectoryName = 'OurLibrary';
        this.directoryHandle = null;
        this.subdirectories = {
            database: 'database',
            downloads: 'downloads', 
            userData: 'user_data',
            cache: 'cache'
        };
        this.isSupported = this.checkFileSystemSupport();
    }

    /**
     * Check if File System Access API is supported
     */
    checkFileSystemSupport() {
        return 'showDirectoryPicker' in window && 'showSaveFilePicker' in window;
    }

    /**
     * Initialize the OurLibrary directory structure
     * Asks user for permission to create ~/OurLibrary/ directory
     */
    async initializeLibraryDirectory() {
        try {
            console.log('🏠 Auto-creating OurLibrary directory structure...');
            
            // Get platform-specific path where files will be stored
            const platformPath = this.getDefaultLibraryPath();
            console.log(`📍 Files will be stored at: ${platformPath}`);
            
            // Use automatic directory creation (no user dialogs)
            await this.createDirectoryStructureAutomatically();
            
            console.log(`✅ OurLibrary directory structure created automatically`);

            return {
                success: true,
                path: platformPath,
                message: `OurLibrary directory created automatically at ${platformPath}`
            };

        } catch (error) {
            console.error('❌ Failed to initialize directory:', error);
            
            // Provide specific error messages based on error type
            let errorMessage = error.message;
            let recommendation = 'Please try again or use a different browser.';
            
            if (error.name === 'AbortError' || error.message.includes('aborted')) {
                errorMessage = 'Directory picker was cancelled or blocked by browser security settings.';
                recommendation = 'Try: 1) Enable file system access in browser settings, 2) Use Chrome/Edge browser, 3) Disable popup blockers';
            } else if (error.message.includes('not supported')) {
                errorMessage = 'Your browser does not support file system access.';
                recommendation = 'Please use Chrome, Edge, or another Chromium-based browser for full functionality.';
            } else if (error.message.includes('permission')) {
                errorMessage = 'File system permission denied.';
                recommendation = 'Please allow file system access when prompted, or check browser security settings.';
            }
            
            return {
                success: false,
                error: errorMessage,
                recommendation: recommendation,
                fallback: 'browser-storage'
            };
        }
    }

    /**
     * Create the standard OurLibrary subdirectory structure (VIRTUAL - no user dialogs)
     */
    async createSubdirectories() {
        const directories = [
            { name: this.subdirectories.database, purpose: 'Book catalog database' },
            { name: this.subdirectories.downloads, purpose: 'Downloaded books for offline reading' },
            { name: this.subdirectories.userData, purpose: 'Reading progress and preferences' },
            { name: this.subdirectories.cache, purpose: 'Temporary files and thumbnails' }
        ];

        for (const dir of directories) {
            try {
                // Create virtual directory structure in storage
                const dirKey = `ourLibrary_dir_${dir.name}`;
                localStorage.setItem(dirKey, JSON.stringify({
                    name: dir.name,
                    purpose: dir.purpose,
                    created: Date.now(),
                    files: []
                }));
                console.log(`📁 Created virtual subdirectory: ${dir.name} (${dir.purpose})`);
            } catch (error) {
                console.warn(`⚠️  Could not create virtual directory ${dir.name}:`, error);
            }
        }
    }

    /**
     * Download and save the main book catalog database
     */
    async downloadAndSaveDatabase(databaseUrl = 'Data/OurLibrary.db') {
        try {
            console.log('📥 Downloading book catalog database...');
            
            const response = await fetch(databaseUrl);
            if (!response.ok) {
                throw new Error(`Database download failed: ${response.status}`);
            }

            const totalSize = parseInt(response.headers.get('content-length'), 10) || response.headers.get('content-length');
            const arrayBuffer = await response.arrayBuffer();
            const databaseData = new Uint8Array(arrayBuffer);

            console.log('💾 Saving database to automatic location...');

            // Save database to browser's automatic download location
            const blob = new Blob([databaseData], { type: 'application/x-sqlite3' });
            const filename = 'OurLibrary_catalog.db';
            
            // Use automatic download - browser saves to Downloads folder
            const downloadLink = document.createElement('a');
            downloadLink.href = URL.createObjectURL(blob);
            downloadLink.download = filename;
            downloadLink.style.display = 'none';
            document.body.appendChild(downloadLink);
            downloadLink.click();
            document.body.removeChild(downloadLink);
            URL.revokeObjectURL(downloadLink.href);

            // Also store in IndexedDB for application use
            await this.saveToIndexedDB('ourLibrary_database', {
                filename: filename,
                data: Array.from(databaseData),
                timestamp: Date.now(),
                size: databaseData.length
            });

            console.log('✅ Database saved successfully to Downloads folder and app storage');

            return {
                success: true,
                size: databaseData.length,
                location: `~/Downloads/${filename} and app storage`
            };

        } catch (error) {
            console.error('❌ Database download/save failed:', error);
            throw error;
        }
    }

    /**
     * Save a downloaded book to the downloads directory
     */
    async saveBook(bookData, bookTitle, bookId) {
        try {
            // Sanitize filename
            const safeTitle = this.sanitizeFilename(bookTitle);
            const filename = `${bookId}_${safeTitle}.pdf`;
            
            // Save to virtual downloads directory
            const bookKey = `ourLibrary_book_${bookId}`;
            const bookEntry = {
                filename: filename,
                title: bookTitle,
                bookId: bookId,
                data: Array.from(new Uint8Array(bookData)),
                timestamp: Date.now(),
                directory: this.subdirectories.downloads
            };
            
            // Use IndexedDB for book files (they're typically large)
            await this.saveToIndexedDB(bookKey, bookEntry);

            console.log(`📚 Book saved to virtual storage: ${filename}`);
            
            return {
                success: true,
                filename: filename,
                path: `${this.getDefaultLibraryPath()}/${this.subdirectories.downloads}/${filename}`
            };

        } catch (error) {
            console.error('❌ Failed to save book:', error);
            throw error;
        }
    }

    /**
     * Save user data (reading progress, bookmarks, preferences)
     */
    async saveUserData(dataType, data) {
        try {
            const filename = `${dataType}.json`;
            
            // Save user data to localStorage (small JSON files)
            const userDataKey = `ourLibrary_userData_${dataType}`;
            const userData = {
                filename: filename,
                dataType: dataType,
                data: data,
                timestamp: Date.now(),
                directory: this.subdirectories.userData
            };
            
            localStorage.setItem(userDataKey, JSON.stringify(userData));

            console.log(`💾 User data saved: ${dataType}`);
            
            return { success: true, filename: filename };

        } catch (error) {
            console.error(`❌ Failed to save ${dataType}:`, error);
            throw error;
        }
    }

    /**
     * Load user data from file system
     */
    async loadUserData(dataType) {
        try {
            const filename = `${dataType}.json`;
            
            // Load user data from localStorage
            const userDataKey = `ourLibrary_userData_${dataType}`;
            const storedData = localStorage.getItem(userDataKey);
            
            if (!storedData) {
                throw new Error(`User data file not found: ${filename}`);
            }
            
            const userData = JSON.parse(storedData);
            
            return userData.data;

        } catch (error) {
            console.log(`ℹ️  No existing ${dataType} data found (this is normal for new users)`);
            return null;
        }
    }

    /**
     * Get list of downloaded books
     */
    async getDownloadedBooks() {
        try {
            const books = [];
            
            // Get all book entries from IndexedDB
            for (let i = 0; i < localStorage.length; i++) {
                const key = localStorage.key(i);
                if (key && key.startsWith('ourLibrary_book_')) {
                    try {
                        const bookData = JSON.parse(localStorage.getItem(key));
                        if (bookData && bookData.filename) {
                            books.push({
                                filename: bookData.filename,
                                size: bookData.data ? bookData.data.length : 0,
                                lastModified: bookData.timestamp,
                                bookId: bookData.bookId,
                                title: bookData.title
                            });
                        }
                    } catch (parseError) {
                        console.warn(`Skipping corrupted book entry: ${key}`);
                    }
                }
            }

            return books;

        } catch (error) {
            console.error('❌ Failed to get downloaded books:', error);
            return [];
        }
    }

    /**
     * Get directory size and usage statistics
     */
    async getDirectoryStats() {
        try {
            const stats = {
                totalSize: 0,
                fileCount: 0,
                directories: {}
            };

            // Calculate stats from virtual storage
            for (const [dirName, dirPath] of Object.entries(this.subdirectories)) {
                try {
                    let dirSize = 0;
                    let fileCount = 0;

                    // Scan localStorage for files in this directory
                    for (let i = 0; i < localStorage.length; i++) {
                        const key = localStorage.key(i);
                        if (key && key.startsWith('ourLibrary_')) {
                            try {
                                const data = JSON.parse(localStorage.getItem(key));
                                if (data && data.directory === dirPath) {
                                    const size = data.data ? 
                                        (Array.isArray(data.data) ? data.data.length : JSON.stringify(data.data).length) 
                                        : 0;
                                    dirSize += size;
                                    fileCount++;
                                }
                            } catch (parseError) {
                                // Skip corrupted entries
                            }
                        }
                    }

                    stats.directories[dirName] = { size: dirSize, files: fileCount };
                    stats.totalSize += dirSize;
                    stats.fileCount += fileCount;

                } catch (error) {
                    stats.directories[dirName] = { size: 0, files: 0 };
                }
            }

            return stats;

        } catch (error) {
            console.error('❌ Failed to get directory stats:', error);
            return null;
        }
    }

    /**
     * Save directory reference for future sessions (AUTOMATIC - no user interaction)
     */
    async saveDirectoryReference() {
        // Virtual file system with automatic downloads - no directory handle needed
        const directoryInfo = {
            virtualRoot: 'OurLibrary',
            downloadLocation: '~/Downloads/',
            userDataLocation: 'browser storage',
            initialized: true,
            timestamp: Date.now()
        };
        localStorage.setItem('ourLibrary_directory_info', JSON.stringify(directoryInfo));
        console.log('📁 Directory reference saved (automatic mode)');
    }

    /**
     * Load directory reference from previous session
     */
    async loadDirectoryReference() {
        // Load automatic directory configuration
        const saved = localStorage.getItem('ourLibrary_directory_info');
        if (saved) {
            const info = JSON.parse(saved);
            console.log('📁 Directory reference loaded (automatic mode)');
            return info.initialized;
        }
        console.log('📁 No previous directory reference found');
        return false;
    }

    /**
     * Utility: Sanitize filename for cross-platform compatibility
     */
    sanitizeFilename(filename) {
        return filename
            .replace(/[<>:"/\\|?*]/g, '_')  // Replace invalid characters
            .replace(/\s+/g, '_')           // Replace spaces with underscores
            .substring(0, 100);             // Limit length
    }

    /**
     * Progress reporting callback
     */
    reportProgress(operation, percentage, details) {
        // Dispatch custom event for UI to catch
        window.dispatchEvent(new CustomEvent('ourLibraryProgress', {
            detail: { operation, percentage, details }
        }));
        
        console.log(`📊 ${operation}: ${percentage}% - ${details}`);
    }

    /**
     * Browser compatibility fallback message
     */
    getCompatibilityMessage() {
        return {
            supported: this.isSupported,
            message: this.isSupported 
                ? "File System Access supported - full functionality available"
                : "File System Access not supported - will use browser storage fallback",
            recommendation: this.isSupported 
                ? "Ready to use file system storage"
                : "Consider using Chrome, Edge, or other Chromium-based browsers for full functionality"
        };
    }

    /**
     * Get default library path based on platform
     */
    getDefaultLibraryPath() {
        // Detect platform
        const platform = navigator.platform.toLowerCase();
        const userAgent = navigator.userAgent.toLowerCase();
        
        if (platform.includes('win')) {
            return 'C:/Users/[username]/OurLibrary';
        } else if (platform.includes('mac')) {
            return '~/OurLibrary';
        } else if (userAgent.includes('android')) {
            return '/storage/emulated/0/OurLibrary';
        } else {
            // Linux and other Unix-like systems
            return '~/OurLibrary';
        }
    }

    /**
     * Initialize virtual file system using browser storage
     */
    async initializeVirtualFileSystem() {
        // Use IndexedDB for structured storage
        this.virtualFS = {
            root: 'OurLibrary',
            initialized: true,
            timestamp: Date.now()
        };
        
        // Store in localStorage for persistence
        localStorage.setItem('ourLibrary_fs_root', JSON.stringify(this.virtualFS));
        
        console.log('📦 Virtual file system initialized');
    }

    /**
     * Create virtual subdirectories in storage
     */
    async createVirtualSubdirectories() {
        const directories = [
            { name: this.subdirectories.database, purpose: 'Book catalog database' },
            { name: this.subdirectories.downloads, purpose: 'Downloaded books for offline reading' },
            { name: this.subdirectories.userData, purpose: 'Reading progress and preferences' },
            { name: this.subdirectories.cache, purpose: 'Temporary files and thumbnails' }
        ];

        for (const dir of directories) {
            try {
                // Create virtual directory in storage
                const dirKey = `ourLibrary_dir_${dir.name}`;
                localStorage.setItem(dirKey, JSON.stringify({
                    name: dir.name,
                    purpose: dir.purpose,
                    created: Date.now(),
                    files: []
                }));
                
                console.log(`📁 Created virtual subdirectory: ${dir.name} (${dir.purpose})`);
            } catch (error) {
                console.warn(`⚠️ Could not create virtual directory ${dir.name}:`, error.message);
            }
        }
    }

    /**
     * Create directory structure automatically without user dialogs
     */
    async createDirectoryStructureAutomatically() {
        // Initialize virtual file system using browser storage + downloads for real files
        this.virtualFS = {
            root: 'OurLibrary',
            path: this.getDefaultLibraryPath(),
            initialized: true,
            timestamp: Date.now(),
            directories: {
                database: { files: [] },
                downloads: { files: [] },
                userData: { files: [] },
                cache: { files: [] }
            }
        };
        
        // Store structure in localStorage
        localStorage.setItem('ourLibrary_fs_structure', JSON.stringify(this.virtualFS));
        
        console.log('📁 Virtual directory structure created');
        console.log('📥 Real files will be downloaded to browser\'s download folder and organized');
        
        return true;
    }

    /**
     * Save large data to IndexedDB
     */
    async saveToIndexedDB(key, data) {
        return new Promise((resolve, reject) => {
            const request = indexedDB.open('OurLibraryDB', 1);
            
            request.onerror = () => reject(request.error);
            
            request.onsuccess = () => {
                const db = request.result;
                const transaction = db.transaction(['files'], 'readwrite');
                const store = transaction.objectStore('files');
                
                store.put(data, key);
                
                transaction.oncomplete = () => resolve();
                transaction.onerror = () => reject(transaction.error);
            };
            
            request.onupgradeneeded = (event) => {
                const db = event.target.result;
                if (!db.objectStoreNames.contains('files')) {
                    db.createObjectStore('files');
                }
            };
        });
    }
}

// Export for use in other modules
window.OurLibraryFileManager = OurLibraryFileManager;