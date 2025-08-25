// File: environment.js
// Path: /home/herb/Desktop/OurLibrary/JS/environment.js
// Standard: AIDEV-PascalCase-2.3
// Created: 2025-01-23
// Last Modified: 2025-01-23 03:20PM

/**
 * OurLibrary User Environment Manager
 * Handles user environment detection and setup flow routing
 * Determines whether user needs setup or can go directly to library
 */

class OurLibraryEnvironment {
    constructor() {
        this.setupCompleteKey = 'ourLibrary_setupComplete';
        this.userPrefsKey = 'ourLibrary_userPrefs';
        this.dbVersionKey = 'ourLibrary_dbVersion';
        this.isSetupComplete = false;
        this.needsSetup = false;
        this.setupInfo = null;
    }

    /**
     * Initialize and check user environment
     * Returns routing decision: 'setup', 'library', or 'error'
     */
    async initialize() {
        try {
            console.log('Checking user environment...');
            
            // Check if setup has been completed before
            const setupInfo = await this.checkSetupStatus();
            
            if (setupInfo && setupInfo.isComplete) {
                console.log('Setup previously completed, validating environment...');
                
                // Validate that the environment is still intact
                const isValid = await this.validateEnvironment();
                
                if (isValid) {
                    console.log('Environment validation passed - routing to library');
                    this.isSetupComplete = true;
                    return 'library';
                } else {
                    console.log('Environment validation failed - needs re-setup');
                    await this.clearSetupStatus();
                    return 'setup';
                }
            } else {
                console.log('No previous setup found - routing to setup');
                this.needsSetup = true;
                return 'setup';
            }
            
        } catch (error) {
            console.error('Environment initialization failed:', error);
            return 'error';
        }
    }

    /**
     * Check if setup has been completed previously
     */
    async checkSetupStatus() {
        try {
            const setupData = localStorage.getItem(this.setupCompleteKey);
            
            if (!setupData) {
                return null;
            }
            
            const setupInfo = JSON.parse(setupData);
            
            // Validate setup data structure
            if (!setupInfo.timestamp || !setupInfo.version) {
                return null;
            }
            
            // Check if setup is not too old (30 days)
            const thirtyDays = 30 * 24 * 60 * 60 * 1000;
            if (Date.now() - setupInfo.timestamp > thirtyDays) {
                console.log('Setup is older than 30 days - recommending refresh');
                return null;
            }
            
            this.setupInfo = setupInfo;
            return {
                ...setupInfo,
                isComplete: true
            };
            
        } catch (error) {
            console.error('Error checking setup status:', error);
            return null;
        }
    }

    /**
     * Validate that the environment is still working
     */
    async validateEnvironment() {
        try {
            // Check browser support
            if (!this.checkBrowserSupport()) {
                console.log('Browser support validation failed');
                return false;
            }
            
            // Check IndexedDB database exists and is accessible
            const dbExists = await this.checkDatabaseExists();
            if (!dbExists) {
                console.log('Database validation failed');
                return false;
            }
            
            // Quick database functionality test
            const dbWorks = await this.testDatabaseFunctionality();
            if (!dbWorks) {
                console.log('Database functionality test failed');
                return false;
            }
            
            // Check storage quota hasn't been exceeded
            const storageOK = await this.checkStorageQuota();
            if (!storageOK) {
                console.log('Storage quota validation failed');
                return false;
            }
            
            return true;
            
        } catch (error) {
            console.error('Environment validation error:', error);
            return false;
        }
    }

    /**
     * Check browser support for required features
     */
    checkBrowserSupport() {
        const requiredFeatures = [
            'indexedDB',
            'caches',
            'localStorage',
            'fetch',
            'Promise'
        ];
        
        for (const feature of requiredFeatures) {
            if (!(feature in window)) {
                console.log(`Missing required feature: ${feature}`);
                return false;
            }
        }
        
        return true;
    }

    /**
     * Check if the database exists in IndexedDB
     */
    async checkDatabaseExists() {
        return new Promise((resolve) => {
            const dbName = window.ourLibraryDB?.indexedDBName || 'OurLibrary_v1';
            const request = indexedDB.open(dbName);
            
            request.onsuccess = () => {
                const db = request.result;
                const hasStore = db.objectStoreNames.contains('database');
                db.close();
                resolve(hasStore);
            };
            
            request.onerror = () => resolve(false);
            request.onblocked = () => resolve(false);
        });
    }

    /**
     * Test basic database functionality
     */
    async testDatabaseFunctionality() {
        try {
            // Initialize database if not already done
            if (!window.ourLibraryDB) {
                console.log('Database manager not available');
                return false;
            }
            
            if (!window.ourLibraryDB.isInitialized) {
                await window.ourLibraryDB.initialize();
            }
            
            // Perform a basic query test
            const testResult = window.ourLibraryDB.searchBooks('', null, null, 1);
            
            // Should have at least one book
            if (!testResult || testResult.length === 0) {
                console.log('Database query returned no results');
                return false;
            }
            
            return true;
            
        } catch (error) {
            console.error('Database functionality test error:', error);
            return false;
        }
    }

    /**
     * Check storage quota and availability
     */
    async checkStorageQuota() {
        try {
            if (!navigator.storage || !navigator.storage.estimate) {
                return true; // Can't check, assume OK
            }
            
            const estimate = await navigator.storage.estimate();
            const quota = estimate.quota || 0;
            const usage = estimate.usage || 0;
            const available = quota - usage;
            
            // Need at least 20MB available for operation
            const minRequired = 20 * 1024 * 1024;
            
            if (available < minRequired) {
                console.log(`Insufficient storage: ${Math.round(available / (1024 * 1024))}MB available, ${Math.round(minRequired / (1024 * 1024))}MB required`);
                return false;
            }
            
            return true;
            
        } catch (error) {
            console.error('Storage quota check error:', error);
            return true; // Assume OK if can't check
        }
    }

    /**
     * Mark setup as complete
     */
    markSetupComplete(additionalInfo = {}) {
        const setupInfo = {
            timestamp: Date.now(),
            version: '1.0',
            booksCount: 1219,
            setupTime: additionalInfo.setupTime || 0,
            ...additionalInfo
        };
        
        localStorage.setItem(this.setupCompleteKey, JSON.stringify(setupInfo));
        this.isSetupComplete = true;
        this.setupInfo = setupInfo;
        
        console.log('Setup marked as complete:', setupInfo);
    }

    /**
     * Clear setup status (force re-setup)
     */
    async clearSetupStatus() {
        try {
            localStorage.removeItem(this.setupCompleteKey);
            localStorage.removeItem(this.userPrefsKey);
            
            // Clear IndexedDB database
            if (window.ourLibraryDB?.indexedDBName) {
                const dbName = window.ourLibraryDB.indexedDBName;
                await this.deleteIndexedDB(dbName);
            }
            
            // Clear PDF cache
            if ('caches' in window) {
                await caches.delete('OurLibrary_PDFs');
            }
            
            this.isSetupComplete = false;
            this.needsSetup = true;
            
            console.log('Setup status cleared');
            
        } catch (error) {
            console.error('Error clearing setup status:', error);
        }
    }

    /**
     * Delete IndexedDB database
     */
    deleteIndexedDB(dbName) {
        return new Promise((resolve, reject) => {
            const deleteRequest = indexedDB.deleteDatabase(dbName);
            
            deleteRequest.onsuccess = () => {
                console.log(`IndexedDB ${dbName} deleted successfully`);
                resolve();
            };
            
            deleteRequest.onerror = () => {
                console.error(`Failed to delete IndexedDB ${dbName}`);
                reject(deleteRequest.error);
            };
            
            deleteRequest.onblocked = () => {
                console.warn(`IndexedDB ${dbName} deletion blocked`);
                resolve(); // Continue anyway
            };
        });
    }

    /**
     * Get setup information
     */
    getSetupInfo() {
        return this.setupInfo;
    }

    /**
     * Check if user is returning (has setup info)
     */
    isReturningUser() {
        return !!this.setupInfo;
    }

    /**
     * Route user based on environment check
     */
    static async routeUser() {
        const env = new OurLibraryEnvironment();
        const route = await env.initialize();
        
        switch (route) {
            case 'setup':
                console.log('Routing to setup page');
                window.location.href = 'library.html';
                break;
                
            case 'library':
                console.log('Environment ready - staying on library page');
                // User can stay on current page
                break;
                
            case 'error':
                console.error('Environment initialization failed');
                alert('Failed to initialize your library environment. Please try refreshing the page or contact support.');
                break;
                
            default:
                console.error('Unknown routing result:', route);
                break;
        }
        
        return route;
    }
}

// Create global environment manager instance
window.ourLibraryEnvironment = new OurLibraryEnvironment();

// Auto-route if this script is loaded on the library page
document.addEventListener('DOMContentLoaded', function() {
    // Check if we're on the library page
    if (window.location.pathname.includes('library.html') || 
        window.location.pathname === '/' && document.getElementById('booksGrid')) {
        
        // Only route if we don't already have setup completion
        const setupData = localStorage.getItem('ourLibrary_setupComplete');
        if (!setupData) {
            console.log('No setup found on library page - routing to setup');
            window.location.href = 'library.html';
        }
    }
});