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
     * Downloads installer script for user to run (like Chrome, Python, MySQL installers)
     */
    async initializeLibraryDirectory() {
        try {
            console.log('🏠 Downloading OurLibrary installer...');
            
            // Get platform-specific path where installer will be downloaded
            const platformPath = this.getDefaultLibraryPath();
            console.log(`📍 Installer will create library at: ${platformPath}`);
            
            // Download the installer script
            await this.downloadInstaller();
            
            return {
                success: true,
                path: platformPath,
                message: 'OurLibrary installer downloaded successfully. Please run it to complete setup.',
                installerPath: '~/Downloads/OurLibrary-Installer.sh'
            };

        } catch (error) {
            console.error('❌ Failed to download installer:', error);
            
            return {
                success: false,
                error: 'Failed to download installer: ' + error.message,
                recommendation: 'Please check your internet connection and try again.',
                fallback: 'manual-download'
            };
        }
    }

    /**
     * Download the installation script (like Chrome installer, Python installer, etc.)
     */
    async downloadInstaller() {
        try {
            console.log('📥 Downloading OurLibrary installer script...');
            
            // Fetch the installer script
            const response = await fetch('OurLibrary-Installer.sh');
            if (!response.ok) {
                throw new Error(`Installer download failed: ${response.status}`);
            }
            
            const installerContent = await response.text();
            
            // Create and trigger download (like any software installer)
            const blob = new Blob([installerContent], { type: 'application/x-sh' });
            const url = URL.createObjectURL(blob);
            
            const a = document.createElement('a');
            a.href = url;
            a.download = 'OurLibrary-Installer.sh';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            
            URL.revokeObjectURL(url);
            
            console.log('✅ Installer downloaded to ~/Downloads/OurLibrary-Installer.sh');
            console.log('🔧 User can now run: chmod +x ~/Downloads/OurLibrary-Installer.sh && ~/Downloads/OurLibrary-Installer.sh');
            
            return { success: true };
            
        } catch (error) {
            console.error('❌ Installer download failed:', error);
            throw error;
        }
    }

    /**
     * Create the standard OurLibrary subdirectory structure (REAL directories)
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
                await this.directoryHandle.getDirectoryHandle(dir.name, { create: true });
                console.log(`📁 Created REAL subdirectory: ${dir.name} (${dir.purpose})`);
            } catch (error) {
                console.warn(`⚠️  Could not create ${dir.name}:`, error);
            }
        }
    }

    /**
     * Download and save the main book catalog database to REAL directory
     */
    async downloadAndSaveDatabase(databaseUrl = 'library_web.db') {
        try {
            console.log('📥 Downloading book catalog database...');
            
            const response = await fetch(databaseUrl);
            if (!response.ok) {
                throw new Error(`Database download failed: ${response.status}`);
            }

            const totalSize = parseInt(response.headers.get('content-length'), 10);
            const reader = response.body.getReader();
            let downloadedSize = 0;
            const chunks = [];

            // Download with progress tracking
            while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                chunks.push(value);
                downloadedSize += value.length;

                // Report progress
                const progress = Math.round((downloadedSize / totalSize) * 100);
                this.reportProgress('download', progress, `${downloadedSize} / ${totalSize} bytes`);
            }

            // Combine chunks into single array
            const databaseData = new Uint8Array(downloadedSize);
            let offset = 0;
            for (const chunk of chunks) {
                databaseData.set(chunk, offset);
                offset += chunk.length;
            }

            console.log('💾 Saving database to REAL ~/OurLibrary/database/ directory...');

            // Save to REAL database subdirectory
            const dbDir = await this.directoryHandle.getDirectoryHandle(this.subdirectories.database);
            const dbFile = await dbDir.getFileHandle('library_catalog.db', { create: true });
            const writable = await dbFile.createWritable();
            
            await writable.write(databaseData);
            await writable.close();

            console.log('✅ Database saved successfully to REAL directory');

            return {
                success: true,
                size: downloadedSize,
                location: `${this.directoryHandle.name}/${this.subdirectories.database}/library_catalog.db`
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
     * Save directory reference for future sessions 
     */
    async saveDirectoryReference() {
        try {
            // Store directory handle for future sessions (if supported by browser)
            if (this.directoryHandle && 'navigator' in window && 'storage' in navigator && 'persist' in navigator.storage) {
                await navigator.storage.persist();
            }
            console.log('📁 Directory reference saved');
        } catch (error) {
            console.warn('Could not save directory reference:', error);
        }
    }

    /**
     * Load directory reference from previous session
     */
    async loadDirectoryReference() {
        // Directory handle persistence is handled by the browser
        // This is called but no action needed - user will be prompted if needed
        console.log('📁 Directory reference handling managed by browser');
        return true;
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
     * Create directory structure - this method is no longer used
     * Directory creation now handled directly by initializeLibraryDirectory()
     */
    async createDirectoryStructureAutomatically() {
        // This method is deprecated - directory creation handled by initializeLibraryDirectory()
        console.log('📁 Directory creation handled by File System Access API');
        return true;
    }

    /**
     * Fallback directory structure using downloads + virtual storage
     */
    async createFallbackDirectoryStructure() {
        // Initialize virtual file system as fallback
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
        
        console.log('📁 Virtual directory structure created (fallback mode)');
        console.log('📥 Files will be downloaded to browser\'s download folder');
        
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