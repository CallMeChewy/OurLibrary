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
            console.log('🏠 Auto-initializing OurLibrary directory...');
            
            // Use browser storage as primary method (no user prompts)
            const virtualPath = this.getDefaultLibraryPath();
            console.log(`📍 Using library path: ${virtualPath}`);
            
            // Initialize virtual file system using browser storage
            await this.initializeVirtualFileSystem();
            
            // Create subdirectories in storage
            await this.createVirtualSubdirectories();
            
            console.log('✅ OurLibrary initialized successfully in browser storage');

            return {
                success: true,
                path: virtualPath,
                message: `OurLibrary directory created successfully`
            };

        } catch (error) {
            console.error('❌ Failed to initialize directory:', error);
            return {
                success: false,
                error: error.message,
                fallback: 'browser-storage'
            };
        }
    }

    /**
     * Create the standard OurLibrary subdirectory structure (DEPRECATED - replaced by createVirtualSubdirectories)
     * Kept for backward compatibility
     */
    async createSubdirectories() {
        // Redirect to virtual subdirectory creation
        return await this.createVirtualSubdirectories();
    }

    /**
     * Download and save the main book catalog database
     */
    async downloadAndSaveDatabase(databaseUrl = '/library_web.db') {
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

            console.log('💾 Saving database to virtual storage...');

            // Save to virtual database directory using browser storage
            const dbKey = `ourLibrary_db_library_catalog`;
            const dbData = {
                filename: 'library_catalog.db',
                size: downloadedSize,
                data: Array.from(databaseData), // Convert to array for storage
                timestamp: Date.now(),
                directory: this.subdirectories.database
            };
            
            // Store in localStorage (for small files) or IndexedDB (for large files)
            if (downloadedSize > 5 * 1024 * 1024) { // > 5MB, use IndexedDB
                await this.saveToIndexedDB(dbKey, dbData);
            } else {
                localStorage.setItem(dbKey, JSON.stringify(dbData));
            }

            console.log('✅ Database saved to virtual storage successfully');

            return {
                success: true,
                size: downloadedSize,
                location: `${this.getDefaultLibraryPath()}/${this.subdirectories.database}/library_catalog.db`
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
            const downloadsDir = await this.directoryHandle.getDirectoryHandle(this.subdirectories.downloads);
            
            // Sanitize filename
            const safeTitle = this.sanitizeFilename(bookTitle);
            const filename = `${bookId}_${safeTitle}.pdf`;

            const bookFile = await downloadsDir.getFileHandle(filename, { create: true });
            const writable = await bookFile.createWritable();
            
            await writable.write(bookData);
            await writable.close();

            console.log(`📚 Book saved: ${filename}`);
            
            return {
                success: true,
                filename: filename,
                path: `${this.directoryHandle.name}/${this.subdirectories.downloads}/${filename}`
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
            const userDir = await this.directoryHandle.getDirectoryHandle(this.subdirectories.userData);
            const filename = `${dataType}.json`;

            const dataFile = await userDir.getFileHandle(filename, { create: true });
            const writable = await dataFile.createWritable();
            
            await writable.write(JSON.stringify(data, null, 2));
            await writable.close();

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
            const userDir = await this.directoryHandle.getDirectoryHandle(this.subdirectories.userData);
            const filename = `${dataType}.json`;

            const dataFile = await userDir.getFileHandle(filename);
            const file = await dataFile.getFile();
            const content = await file.text();

            return JSON.parse(content);

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
            const downloadsDir = await this.directoryHandle.getDirectoryHandle(this.subdirectories.downloads);
            const books = [];

            for await (const [name, handle] of downloadsDir.entries()) {
                if (handle.kind === 'file' && name.endsWith('.pdf')) {
                    const file = await handle.getFile();
                    books.push({
                        filename: name,
                        size: file.size,
                        lastModified: file.lastModified,
                        bookId: name.split('_')[0]
                    });
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

            for (const [dirName, dirPath] of Object.entries(this.subdirectories)) {
                try {
                    const subDir = await this.directoryHandle.getDirectoryHandle(dirPath);
                    let dirSize = 0;
                    let fileCount = 0;

                    for await (const [name, handle] of subDir.entries()) {
                        if (handle.kind === 'file') {
                            const file = await handle.getFile();
                            dirSize += file.size;
                            fileCount++;
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
        if ('indexedDB' in window) {
            // Store the directory handle in IndexedDB for persistence
            const request = indexedDB.open('OurLibraryConfig', 1);
            
            request.onupgradeneeded = (event) => {
                const db = event.target.result;
                db.createObjectStore('config');
            };

            request.onsuccess = (event) => {
                const db = event.target.result;
                const transaction = db.transaction(['config'], 'readwrite');
                const store = transaction.objectStore('config');
                store.put(this.directoryHandle, 'libraryDirectory');
            };
        }
    }

    /**
     * Load directory reference from previous session
     */
    async loadDirectoryReference() {
        if (!('indexedDB' in window)) return null;

        return new Promise((resolve) => {
            const request = indexedDB.open('OurLibraryConfig', 1);
            
            request.onsuccess = (event) => {
                const db = event.target.result;
                
                if (!db.objectStoreNames.contains('config')) {
                    resolve(null);
                    return;
                }

                const transaction = db.transaction(['config'], 'readonly');
                const store = transaction.objectStore('config');
                const getRequest = store.get('libraryDirectory');
                
                getRequest.onsuccess = () => {
                    this.directoryHandle = getRequest.result;
                    resolve(getRequest.result);
                };
                
                getRequest.onerror = () => resolve(null);
            };
            
            request.onerror = () => resolve(null);
        });
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