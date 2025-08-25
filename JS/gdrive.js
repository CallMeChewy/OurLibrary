// File: gdrive.js
// Path: /home/herb/Desktop/OurLibrary/JS/gdrive.js
// Standard: AIDEV-PascalCase-2.3
// Created: 2025-01-23
// Last Modified: 2025-01-23 02:40PM

/**
 * OurLibrary Google Drive Integration
 * Handles PDF downloads from 2TB Google Drive storage
 * Uses anderson-library-service@anderson-library.iam.gserviceaccount.com
 */

class OurLibraryGDrive {
    constructor() {
        // File: gdrive.js
// Path: /home/herb/Desktop/OurLibrary/archive/JS/gdrive.js
// Standard: AIDEV-PascalCase-2.3
// Created: 2025-01-23
// Last Modified: 2025-08-24 12:45PM

/**
 * OurLibrary Google Drive Integration (Refactored to use OurLibraryFileManager)
 * Handles PDF downloads and saves them directly to the user's chosen directory.
 */
class OurLibraryGDrive {
    constructor() {
        this.baseURL = 'https://drive.google.com/uc?export=download&id=';
        this.fileIdMap = {};
        this.fileMapLoaded = false;
    }

    /**
     * Load file ID mapping from server.
     * Maps book IDs to Google Drive file IDs.
     */
    async loadFileIdMap() {
        if (this.fileMapLoaded) return;

        try {
            const response = await fetch('/assets/data/gdrive_file_map.json');
            if (response.ok) {
                this.fileIdMap = await response.json();
                this.fileMapLoaded = true;
                console.log('Google Drive file ID map loaded.');
            } else {
                console.warn('File ID map not found, book downloads may fail.');
            }
        } catch (error) {
            console.error('Error loading file ID map:', error);
        }
    }

    /**
     * Gets a PDF book.
     * 1. Checks if the book is already downloaded in the user's directory.
     * 2. If not, downloads it from Google Drive.
     * 3. Saves the downloaded book to the user's directory.
     * @param {number} bookId - Book ID from the database.
     * @param {Object} bookInfo - Book information from the database.
     * @returns {Blob|null} PDF blob or null if an error occurs.
     */
    async getBook(bookId, bookInfo = {}) {
        try {
            const fileName = this.generateFileName(bookId, bookInfo.title);

            // 1. Check if the file exists in the user's downloads directory.
            const existingFile = await window.OurLibraryFileManager.readFile('downloads', fileName);
            if (existingFile) {
                console.log(`Book '${fileName}' loaded from local file system.`);
                return existingFile;
            }

            // 2. If not, download from Google Drive.
            console.log(`Downloading book '${fileName}' from Google Drive...`);
            const pdfBlob = await this.downloadFromGDrive(bookId, bookInfo);

            if (pdfBlob) {
                // 3. Save the downloaded file for future use.
                await window.OurLibraryFileManager.writeFile('downloads', fileName, pdfBlob);
                console.log(`Book '${fileName}' saved to local file system.`);
                return pdfBlob;
            }

            return null;

        } catch (error) {
            console.error(`Error getting book ${bookId}:`, error);
            return null;
        }
    }

    /**
     * Downloads the actual PDF content from Google Drive.
     * @param {number} bookId - The ID of the book.
     * @param {Object} bookInfo - Metadata about the book.
     * @returns {Blob|null} The PDF content as a Blob.
     */
    async downloadFromGDrive(bookId, bookInfo) {
        try {
            // Ensure the file map is loaded before trying to download.
            if (!this.fileMapLoaded) {
                await this.loadFileIdMap();
            }

            const fileId = this.fileIdMap[bookId];
            if (!fileId) {
                throw new Error(`No Google Drive file ID found for book ID ${bookId}`);
            }

            const downloadURL = `${this.baseURL}${fileId}`;
            const response = await fetch(downloadURL);

            if (!response.ok) {
                throw new Error(`Download failed: ${response.status} ${response.statusText}`);
            }

            return await response.blob();

        } catch (error) {
            console.error(`Error downloading book ${bookId} from GDrive:`, error);
            return null;
        }
    }
    
    /**
     * Generates a sanitized, consistent file name for a book.
     * @param {number} bookId - The book's ID.
     * @param {string} title - The book's title.
     * @returns {string} A safe filename.
     */
    generateFileName(bookId, title = 'book') {
        const sanitizedTitle = title.replace(/[^a-z0-9]/gi, '_').toLowerCase();
        return `${bookId}_${sanitizedTitle}.pdf`;
    }

    /**
     * Checks if a book PDF already exists in the user's downloads directory.
     * @param {number} bookId - The book's ID.
     * @param {string} title - The book's title.
     * @returns {Promise<boolean>} True if the file exists.
     */
    async isBookDownloaded(bookId, title) {
        const fileName = this.generateFileName(bookId, title);
        const file = await window.OurLibraryFileManager.readFile('downloads', fileName);
        return !!file;
    }
}

// Create a global Google Drive instance.
window.ourLibraryGDrive = new OurLibraryGDrive();

        this.baseURL = 'https://drive.google.com/uc?export=download&id=';
        this.apiBaseURL = 'https://www.googleapis.com/drive/v3';
        this.cacheStoreName = 'OurLibrary_PDFs';
        this.fileMapCache = null;
        this.isInitialized = false;
        
        // File ID mapping will be loaded from server
        this.fileIdMap = {};
        
        // Initialize PDF cache
        this.initializePDFCache();
    }

    /**
     * Initialize PDF caching system using Cache API
     */
    async initializePDFCache() {
        try {
            this.pdfCache = await caches.open(this.cacheStoreName);
            this.isInitialized = true;
            console.log('PDF cache initialized');
        } catch (error) {
            console.error('Failed to initialize PDF cache:', error);
        }
    }

    /**
     * Load file ID mapping from server
     * Maps book IDs to Google Drive file IDs
     */
    async loadFileIdMap() {
        if (this.fileMapCache) return this.fileMapCache;

        try {
            const response = await fetch('/assets/data/gdrive_file_map.json');
            if (response.ok) {
                this.fileMapCache = await response.json();
                this.fileIdMap = this.fileMapCache;
                return this.fileMapCache;
            } else {
                console.warn('File ID map not found, using fallback method');
                return {};
            }
        } catch (error) {
            console.error('Error loading file ID map:', error);
            return {};
        }
    }

    /**
     * Get PDF book - check cache first, download if needed
     * @param {number} bookId - Book ID from database
     * @param {Object} bookInfo - Book information from database
     * @returns {Blob|null} PDF blob or null if error
     */
    async getBook(bookId, bookInfo = {}) {
        if (!this.isInitialized) {
            await this.initializePDFCache();
        }

        try {
            // 1. Check local cache first
            const cacheKey = `book_${bookId}.pdf`;
            const cachedResponse = await this.pdfCache.match(cacheKey);
            
            if (cachedResponse) {
                console.log(`Book ${bookId} loaded from cache`);
                await this.recordMetric('cache_hit', bookId);
                return await cachedResponse.blob();
            }

            // 2. Download from Google Drive
            console.log(`Downloading book ${bookId} from Google Drive...`);
            const pdfBlob = await this.downloadFromGDrive(bookId, bookInfo);
            
            if (pdfBlob) {
                // 3. Cache for future use
                await this.cacheBook(cacheKey, pdfBlob);
                
                // 4. Record download metric
                await this.recordMetric('download', bookId, {
                    title: bookInfo.title || 'Unknown',
                    fileSize: pdfBlob.size
                });
                
                return pdfBlob;
            }

            return null;

        } catch (error) {
            console.error(`Error getting book ${bookId}:`, error);
            await this.recordMetric('error', bookId, { error: error.message });
            return null;
        }
    }

    /**
     * Download PDF from Google Drive
     * @param {number} bookId - Book ID
     * @param {Object} bookInfo - Book metadata
     * @returns {Blob|null} PDF blob
     */
    async downloadFromGDrive(bookId, bookInfo) {
        try {
            // Load file ID mapping if not already loaded
            await this.loadFileIdMap();

            let fileId = this.fileIdMap[bookId];
            
            // Fallback: construct file ID based on book path if mapping not available
            if (!fileId && bookInfo.FilePath) {
                fileId = await this.searchFileByPath(bookInfo.FilePath);
            }

            if (!fileId) {
                console.error(`No file ID found for book ${bookId}`);
                return null;
            }

            // Download via direct link (works for public files)
            const downloadURL = `${this.baseURL}${fileId}`;
            const response = await fetch(downloadURL);

            if (!response.ok) {
                throw new Error(`Download failed: ${response.status} ${response.statusText}`);
            }

            const contentType = response.headers.get('content-type');
            if (!contentType || !contentType.includes('pdf')) {
                console.warn(`Unexpected content type for book ${bookId}: ${contentType}`);
            }

            return await response.blob();

        } catch (error) {
            console.error(`Error downloading book ${bookId}:`, error);
            return null;
        }
    }

    /**
     * Search for file by path (fallback method)
     * This would require API access - placeholder for now
     */
    async searchFileByPath(filePath) {
        // Placeholder - in production, this would use Google Drive API
        // to search for files by name/path
        console.warn('File ID mapping not available, search by path not implemented');
        return null;
    }

    /**
     * Cache book PDF for offline access
     * @param {string} cacheKey - Cache key
     * @param {Blob} pdfBlob - PDF blob to cache
     */
    async cacheBook(cacheKey, pdfBlob) {
        try {
            const response = new Response(pdfBlob, {
                headers: {
                    'Content-Type': 'application/pdf',
                    'Cache-Control': 'max-age=86400', // 24 hours
                    'Last-Modified': new Date().toUTCString()
                }
            });

            await this.pdfCache.put(cacheKey, response);
            console.log(`Book cached: ${cacheKey}`);

        } catch (error) {
            console.error(`Error caching book ${cacheKey}:`, error);
        }
    }

    /**
     * Record usage metrics (batched for privacy)
     * @param {string} action - Action type (download, cache_hit, error)
     * @param {number} bookId - Book ID
     * @param {Object} metadata - Additional metadata
     */
    async recordMetric(action, bookId, metadata = {}) {
        try {
            const metric = {
                timestamp: Date.now(),
                action: action,
                bookId: bookId,
                metadata: metadata,
                userAgent: navigator.userAgent.substring(0, 50), // Truncated for privacy
                sessionId: this.getSessionId()
            };

            // Batch metrics locally
            const pendingMetrics = JSON.parse(localStorage.getItem('pendingMetrics') || '[]');
            pendingMetrics.push(metric);
            localStorage.setItem('pendingMetrics', JSON.stringify(pendingMetrics));

            // Sync when batch reaches threshold or periodically
            if (pendingMetrics.length >= 10 || this.shouldSyncMetrics()) {
                await this.syncMetrics();
            }

        } catch (error) {
            console.error('Error recording metric:', error);
        }
    }

    /**
     * Get or create session ID for analytics
     */
    getSessionId() {
        let sessionId = sessionStorage.getItem('ourlibrary_session');
        if (!sessionId) {
            sessionId = 'ses_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
            sessionStorage.setItem('ourlibrary_session', sessionId);
        }
        return sessionId;
    }

    /**
     * Check if metrics should be synced (time-based)
     */
    shouldSyncMetrics() {
        const lastSync = localStorage.getItem('lastMetricSync');
        if (!lastSync) return true;
        
        const oneHour = 60 * 60 * 1000;
        return (Date.now() - parseInt(lastSync)) > oneHour;
    }

    /**
     * Sync metrics to server/Google Drive
     */
    async syncMetrics() {
        try {
            const pendingMetrics = JSON.parse(localStorage.getItem('pendingMetrics') || '[]');
            if (pendingMetrics.length === 0) return;

            // Send to server endpoint for processing
            const response = await fetch('/api/metrics.php', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    metrics: pendingMetrics,
                    timestamp: Date.now()
                })
            });

            if (response.ok) {
                // Clear pending metrics on successful sync
                localStorage.removeItem('pendingMetrics');
                localStorage.setItem('lastMetricSync', Date.now().toString());
                console.log(`Synced ${pendingMetrics.length} metrics`);
            } else {
                console.warn('Metrics sync failed, will retry later');
            }

        } catch (error) {
            console.error('Error syncing metrics:', error);
        }
    }

    /**
     * Get cache statistics
     */
    async getCacheStats() {
        if (!this.pdfCache) return { totalSize: 0, fileCount: 0 };

        try {
            const keys = await this.pdfCache.keys();
            let totalSize = 0;

            for (const request of keys) {
                const response = await this.pdfCache.match(request);
                if (response) {
                    const blob = await response.blob();
                    totalSize += blob.size;
                }
            }

            return {
                fileCount: keys.length,
                totalSize: totalSize,
                totalSizeMB: Math.round(totalSize / (1024 * 1024) * 10) / 10
            };

        } catch (error) {
            console.error('Error getting cache stats:', error);
            return { totalSize: 0, fileCount: 0 };
        }
    }

    /**
     * Clear PDF cache (for maintenance)
     */
    async clearCache() {
        try {
            const keys = await this.pdfCache.keys();
            await Promise.all(keys.map(key => this.pdfCache.delete(key)));
            console.log('PDF cache cleared');
        } catch (error) {
            console.error('Error clearing cache:', error);
        }
    }

    /**
     * Check if book is cached
     * @param {number} bookId - Book ID
     * @returns {boolean} True if book is cached
     */
    async isBookCached(bookId) {
        if (!this.pdfCache) return false;

        try {
            const cacheKey = `book_${bookId}.pdf`;
            const cachedResponse = await this.pdfCache.match(cacheKey);
            return !!cachedResponse;
        } catch (error) {
            console.error('Error checking cache:', error);
            return false;
        }
    }

    /**
     * Preload popular books for offline access
     * @param {Array} bookIds - Array of book IDs to preload
     */
    async preloadBooks(bookIds = []) {
        console.log(`Preloading ${bookIds.length} books...`);
        
        for (const bookId of bookIds) {
            try {
                if (!(await this.isBookCached(bookId))) {
                    const bookInfo = window.ourLibraryDB ? 
                        window.ourLibraryDB.getBook(bookId) : {};
                    await this.getBook(bookId, bookInfo);
                    
                    // Small delay to avoid overwhelming the system
                    await new Promise(resolve => setTimeout(resolve, 500));
                }
            } catch (error) {
                console.error(`Error preloading book ${bookId}:`, error);
            }
        }
        
        console.log('Book preloading completed');
    }
}

// Create global Google Drive instance
window.ourLibraryGDrive = new OurLibraryGDrive();