// File: database-sync.js
// Path: /home/herb/Desktop/OurLibrary/JS/database-sync.js
// Standard: AIDEV-PascalCase-2.3
// Created: 2025-08-28
// Last Modified: 2025-08-28 05:15PM

/**
 * OurLibrary Database Sync Manager
 * Handles Google Drive database synchronization
 * Downloads latest database from Google Drive and updates local storage
 */

class OurLibraryDatabaseSync {
    constructor() {
        this.gdriveAPI = null;
        this.localDB = window.ourLibraryDB;
        this.syncInterval = 24 * 60 * 60 * 1000; // 24 hours
        this.lastSyncKey = 'ourlibrary_last_sync';
        this.versionKey = 'ourlibrary_db_version';
        
        // Google Drive configuration
        this.gdriveBaseURL = 'https://drive.google.com/uc?export=download&id=';
        this.databaseFileId = null; // Will be loaded from configuration
        
        this.initializeSync();
    }

    /**
     * Initialize database sync system
     */
    async initializeSync() {
        try {
            // Load Google Drive file ID from configuration
            await this.loadConfiguration();
            
            // Check if sync is needed
            if (await this.shouldSync()) {
                console.log('Database sync required, checking for updates...');
                await this.checkForUpdates();
            }
            
            // Setup periodic sync
            this.setupPeriodicSync();
            
        } catch (error) {
            console.error('Failed to initialize database sync:', error);
        }
    }

    /**
     * Load Google Drive configuration
     */
    async loadConfiguration() {
        try {
            const response = await fetch('/Config/ourlibrary_google_config.json');
            if (response.ok) {
                const config = await response.json();
                this.databaseFileId = config.database_file_id;
                
                if (!this.databaseFileId) {
                    console.warn('No database file ID configured for Google Drive sync');
                }
            } else {
                console.warn('Google Drive configuration not found');
            }
        } catch (error) {
            console.error('Error loading Google Drive configuration:', error);
        }
    }

    /**
     * Check if database sync is needed
     */
    async shouldSync() {
        const lastSync = localStorage.getItem(this.lastSyncKey);
        if (!lastSync) return true;
        
        const timeSinceSync = Date.now() - parseInt(lastSync);
        return timeSinceSync > this.syncInterval;
    }

    /**
     * Check for database updates on Google Drive
     */
    async checkForUpdates() {
        if (!this.databaseFileId) {
            console.log('No database file ID configured, skipping sync');
            return false;
        }

        try {
            // Get remote database version/timestamp
            const remoteInfo = await this.getRemoteDatabaseInfo();
            if (!remoteInfo) return false;

            // Compare with local version
            const localVersion = localStorage.getItem(this.versionKey);
            
            if (!localVersion || remoteInfo.version > localVersion || 
                this.isRemoteNewer(remoteInfo.modifiedTime, localVersion)) {
                
                console.log('Remote database is newer, downloading update...');
                return await this.downloadAndUpdateDatabase();
            } else {
                console.log('Local database is up to date');
                this.updateSyncTimestamp();
                return false;
            }

        } catch (error) {
            console.error('Error checking for database updates:', error);
            return false;
        }
    }

    /**
     * Get remote database information
     */
    async getRemoteDatabaseInfo() {
        try {
            // Use Google Drive API to get file metadata
            const apiURL = `https://www.googleapis.com/drive/v3/files/${this.databaseFileId}?fields=id,name,size,modifiedTime,version`;
            
            const response = await fetch(apiURL);
            if (!response.ok) {
                console.warn('Could not fetch remote database info, using direct download');
                return { version: Date.now(), modifiedTime: new Date().toISOString() };
            }

            return await response.json();
            
        } catch (error) {
            console.error('Error getting remote database info:', error);
            return null;
        }
    }

    /**
     * Download and update local database
     */
    async downloadAndUpdateDatabase() {
        try {
            console.log('Downloading database from Google Drive...');
            
            // Download database from Google Drive
            const downloadURL = `${this.gdriveBaseURL}${this.databaseFileId}`;
            const response = await fetch(downloadURL);
            
            if (!response.ok) {
                throw new Error(`Download failed: ${response.status} ${response.statusText}`);
            }

            const dbBuffer = await response.arrayBuffer();
            
            // Validate database integrity
            if (!this.validateDatabase(dbBuffer)) {
                throw new Error('Downloaded database failed integrity check');
            }

            // Update local database
            console.log('Updating local database...');
            const success = await this.localDB.updateDatabase(dbBuffer);
            
            if (success) {
                // Update sync metadata
                this.updateSyncTimestamp();
                localStorage.setItem(this.versionKey, Date.now().toString());
                
                console.log('Database updated successfully from Google Drive');
                
                // Notify UI if callback exists
                if (window.onDatabaseUpdated) {
                    window.onDatabaseUpdated();
                }
                
                return true;
            } else {
                throw new Error('Failed to update local database');
            }

        } catch (error) {
            console.error('Error downloading and updating database:', error);
            return false;
        }
    }

    /**
     * Validate downloaded database
     */
    validateDatabase(dbBuffer) {
        try {
            // Basic validation - check if it's a valid SQLite database
            const header = new Uint8Array(dbBuffer.slice(0, 16));
            const sqliteHeader = new TextDecoder().decode(header);
            
            return sqliteHeader.startsWith('SQLite format 3');
            
        } catch (error) {
            console.error('Database validation error:', error);
            return false;
        }
    }

    /**
     * Check if remote database is newer
     */
    isRemoteNewer(remoteModifiedTime, localVersion) {
        if (!localVersion) return true;
        
        const remoteTime = new Date(remoteModifiedTime).getTime();
        const localTime = parseInt(localVersion);
        
        return remoteTime > localTime;
    }

    /**
     * Update sync timestamp
     */
    updateSyncTimestamp() {
        localStorage.setItem(this.lastSyncKey, Date.now().toString());
    }

    /**
     * Setup periodic sync checking
     */
    setupPeriodicSync() {
        // Check for updates every hour
        setInterval(async () => {
            if (await this.shouldSync()) {
                await this.checkForUpdates();
            }
        }, 60 * 60 * 1000); // 1 hour
    }

    /**
     * Force sync (manual trigger)
     */
    async forcSync() {
        console.log('Force syncing database...');
        localStorage.removeItem(this.lastSyncKey);
        return await this.checkForUpdates();
    }

    /**
     * Get sync status
     */
    getSyncStatus() {
        const lastSync = localStorage.getItem(this.lastSyncKey);
        const version = localStorage.getItem(this.versionKey);
        
        return {
            lastSyncTime: lastSync ? new Date(parseInt(lastSync)) : null,
            currentVersion: version,
            syncConfigured: !!this.databaseFileId,
            nextSyncDue: lastSync ? 
                new Date(parseInt(lastSync) + this.syncInterval) : 
                new Date()
        };
    }

    /**
     * Enable/disable automatic sync
     */
    setAutoSync(enabled) {
        localStorage.setItem('ourlibrary_auto_sync', enabled.toString());
    }

    /**
     * Check if auto sync is enabled
     */
    isAutoSyncEnabled() {
        const setting = localStorage.getItem('ourlibrary_auto_sync');
        return setting !== 'false'; // Default to enabled
    }
}

// Create global database sync instance
window.ourLibraryDBSync = new OurLibraryDatabaseSync();

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = OurLibraryDatabaseSync;
}