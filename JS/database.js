// File: database.js
// Path: /home/herb/Desktop/OurLibrary/JS/database.js
// Standard: AIDEV-PascalCase-2.3
// Created: 2025-01-23
// Last Modified: 2025-01-23 02:35PM

/**
 * OurLibrary Database Manager
 * Handles SQLite database operations via sql.js WebAssembly
 * Implements exact schema from Phase 2 requirements
 */

class OurLibraryDatabase {
    constructor() {
        this.db = null;
        this.SQL = null;
        this.isInitialized = false;
        this.dbVersion = 1;
        this.indexedDBName = 'OurLibrary_v1';
        this.dbStoreName = 'database';
    }

    /**
     * Initialize sql.js WebAssembly and load database
     */
    async initialize() {
        if (this.isInitialized) return this.db;

        try {
            // Load sql.js WebAssembly
            console.log('Loading sql.js WebAssembly...');
            this.SQL = await initSqlJs({
                locateFile: file => `/JS/lib/${file}`
            });

            // Try to load from IndexedDB first (for persistence)
            let dbBuffer = await this.loadFromIndexedDB();
            
            if (!dbBuffer) {
                // Download from server on first run
                console.log('Downloading database from server...');
                dbBuffer = await this.downloadDatabase();
                
                // Store in IndexedDB for future use
                await this.storeInIndexedDB(dbBuffer);
            }

            // Initialize SQLite database
            // File: database.js
// Path: /home/herb/Desktop/OurLibrary/archive/JS/database.js
// Standard: AIDEV-PascalCase-2.3
// Created: 2025-01-23
// Last Modified: 2025-08-24 12:30PM

/**
 * OurLibrary Database Manager (Refactored to use OurLibraryFileManager)
 * Handles SQLite database operations via sql.js WebAssembly.
 * All file operations are delegated to the OurLibraryFileManager.
 */
class OurLibraryDatabase {
    constructor() {
        this.db = null;
        this.SQL = null;
        this.isInitialized = false;
        this.dbFileName = 'library.db';
    }

    /**
     * Initialize sql.js WebAssembly and load the database from the user-selected directory.
     */
    async initialize() {
        if (this.isInitialized) return this.db;

        try {
            // Load sql.js WebAssembly
            console.log('Loading sql.js WebAssembly...');
            this.SQL = await initSqlJs({
                locateFile: file => `/JS/lib/${file}`
            });

            // Try to load the database file from the user's chosen directory via the file manager
            console.log(`Attempting to load '${this.dbFileName}' from the 'database' subdirectory...`);
            let dbFile = await window.OurLibraryFileManager.readFile('database', this.dbFileName);
            let dbBuffer;

            if (dbFile) {
                console.log('Database file found in user directory.');
                dbBuffer = await dbFile.arrayBuffer();
            } else {
                // If it doesn't exist, download it from the server
                console.log('Database not found. Downloading from server...');
                dbBuffer = await this.downloadDatabase();
                
                // And save it to the user's directory for future use
                console.log('Saving database to user directory...');
                await window.OurLibraryFileManager.writeFile('database', this.dbFileName, dbBuffer);
            }

            // Initialize SQLite database
            this.db = new this.SQL.Database(new Uint8Array(dbBuffer));
            this.isInitialized = true;

            console.log('Database initialized successfully');
            return this.db;

        } catch (error) {
            console.error('Failed to initialize database:', error);
            throw new Error(`Database initialization failed: ${error.message}`);
        }
    }

    /**
     * Download the initial database from the server.
     */
    async downloadDatabase() {
        const response = await fetch('/library_web.db');
        if (!response.ok) {
            throw new Error(`Failed to download database: ${response.status}`);
        }
        return await response.arrayBuffer();
    }

    /**
     * Persist any changes to the database file in the user's directory.
     */
    async persistChanges() {
        if (!this.db) return;

        try {
            console.log('Persisting database changes to file...');
            const dbBuffer = this.db.export();
            await window.OurLibraryFileManager.writeFile('database', this.dbFileName, dbBuffer);
            console.log('Database changes saved successfully.');
        } catch (error) {
            console.error('Error persisting database changes:', error);
        }
    }

    /**
     * Search books with exact Phase 2 schema
     * @param {string} query - Search term
     * @param {number|null} categoryId - Filter by category
     * @param {number|null} subjectId - Filter by subject
     * @param {number} limit - Maximum results
     * @returns {Array} Search results
     */
    searchBooks(query = '', categoryId = null, subjectId = null, limit = 50) {
        if (!this.db) {
            throw new Error('Database not initialized');
        }

        let sql = `
            SELECT 
                b.id, 
                b.title, 
                b.author, 
                b.FilePath, 
                b.FileSize, 
                b.PageCount,
                b.Rating,
                b.Notes,
                b.ThumbnailImage,
                c.category, 
                s.subject,
                b.LastOpened
            FROM books b
            LEFT JOIN categories c ON b.category_id = c.id
            LEFT JOIN subjects s ON b.subject_id = s.id
        `;

        const params = [];
        const conditions = [];

        // Search conditions
        if (query && query.trim()) {
            conditions.push('(b.title LIKE ? OR b.author LIKE ? OR s.subject LIKE ?)');
            const searchTerm = `%${query.trim()}%`;
            params.push(searchTerm, searchTerm, searchTerm);
        }

        if (categoryId !== null && categoryId !== '') {
            conditions.push('b.category_id = ?');
            params.push(categoryId);
        }

        if (subjectId !== null && subjectId !== '') {
            conditions.push('b.subject_id = ?');
            params.push(subjectId);
        }

        // Add WHERE clause if we have conditions
        if (conditions.length > 0) {
            sql += ' WHERE ' + conditions.join(' AND ');
        }

        // Order and limit
        sql += ' ORDER BY b.title LIMIT ?';
        params.push(limit);

        try {
            const stmt = this.db.prepare(sql);
            const results = [];

            // Bind parameters
            stmt.bind(params);

            while (stmt.step()) {
                const row = stmt.getAsObject();
                // Convert BLOB thumbnail to base64 if present
                if (row.ThumbnailImage) {
                    const uint8Array = new Uint8Array(row.ThumbnailImage);
                    row.ThumbnailImageBase64 = btoa(String.fromCharCode.apply(null, uint8Array));
                }
                results.push(row);
            }

            stmt.free();
            return results;

        } catch (error) {
            console.error('Search error:', error);
            return [];
        }
    }

    /**
     * Get all categories
     */
    getCategories() {
        if (!this.db) return [];

        try {
            const stmt = this.db.prepare('SELECT * FROM categories ORDER BY category');
            const results = [];

            while (stmt.step()) {
                results.push(stmt.getAsObject());
            }

            stmt.free();
            return results;

        } catch (error) {
            console.error('Error getting categories:', error);
            return [];
        }
    }

    /**
     * Get subjects for a category
     */
    getSubjects(categoryId = null) {
        if (!this.db) return [];

        let sql = 'SELECT * FROM subjects';
        const params = [];

        if (categoryId !== null && categoryId !== '') {
            sql += ' WHERE category_id = ?';
            params.push(categoryId);
        }

        sql += ' ORDER BY subject';

        try {
            const stmt = this.db.prepare(sql);
            if (params.length > 0) {
                stmt.bind(params);
            }

            const results = [];
            while (stmt.step()) {
                results.push(stmt.getAsObject());
            }

            stmt.free();
            return results;

        } catch (error) {
            console.error('Error getting subjects:', error);
            return [];
        }
    }

    /**
     * Get book by ID
     */
    getBook(bookId) {
        if (!this.db) return null;

        try {
            const stmt = this.db.prepare(`
                SELECT 
                    b.*, 
                    c.category, 
                    s.subject
                FROM books b
                LEFT JOIN categories c ON b.category_id = c.id
                LEFT JOIN subjects s ON b.subject_id = s.id
                WHERE b.id = ?
            `);

            stmt.bind([bookId]);

            if (stmt.step()) {
                const result = stmt.getAsObject();
                // Convert BLOB thumbnail to base64 if present
                if (result.ThumbnailImage) {
                    const uint8Array = new Uint8Array(result.ThumbnailImage);
                    result.ThumbnailImageBase64 = btoa(String.fromCharCode.apply(null, uint8Array));
                }
                stmt.free();
                return result;
            }

            stmt.free();
            return null;

        } catch (error) {
            console.error('Error getting book:', error);
            return null;
        }
    }

    /**
     * Update book's last opened timestamp
     */
    async updateLastOpened(bookId) {
        if (!this.db) return false;

        try {
            const stmt = this.db.prepare('UPDATE books SET LastOpened = ? WHERE id = ?');
            stmt.run([new Date().toISOString(), bookId]);
            stmt.free();

            // Persist changes to the file
            await this.persistChanges();
            return true;

        } catch (error) {
            console.error('Error updating last opened:', error);
            return false;
        }
    }

    /**
     * Update book rating and notes
     */
    async updateRating(bookId, rating, notes = '') {
        if (!this.db || rating < 0 || rating > 5) return false;

        try {
            const stmt = this.db.prepare('UPDATE books SET Rating = ?, Notes = ? WHERE id = ?');
            stmt.run([rating, notes, bookId]);
            stmt.free();

            // Persist changes to the file
            await this.persistChanges();
            return true;

        } catch (error) {
            console.error('Error updating rating:', error);
            return false;
        }
    }

    /**
     * Get database statistics
     */
    getStats() {
        if (!this.db) return {};

        try {
            const stats = {};
            let stmt;

            // Total books
            stmt = this.db.prepare('SELECT COUNT(*) as count FROM books');
            stmt.step();
            stats.totalBooks = stmt.getAsObject().count;
            stmt.free();

            // Total categories
            stmt = this.db.prepare('SELECT COUNT(*) as count FROM categories');
            stmt.step();
            stats.totalCategories = stmt.getAsObject().count;
            stmt.free();

            // Total subjects
            stmt = this.db.prepare('SELECT COUNT(*) as count FROM subjects');
            stmt.step();
            stats.totalSubjects = stmt.getAsObject().count;
            stmt.free();

            return stats;

        } catch (error) {
            console.error('Error getting stats:', error);
            return {};
        }
    }
}

// Create global database instance
window.ourLibraryDB = new OurLibraryDatabase();

            this.isInitialized = true;

            console.log('Database initialized successfully');
            return this.db;

        } catch (error) {
            console.error('Failed to initialize database:', error);
            throw new Error(`Database initialization failed: ${error.message}`);
        }
    }

    /**
     * Download database from BowersWorld.com
     */
    async downloadDatabase() {
        const response = await fetch('/library_web.db');
        if (!response.ok) {
            throw new Error(`Failed to download database: ${response.status}`);
        }
        return await response.arrayBuffer();
    }

    /**
     * Load database from IndexedDB (for offline persistence)
     */
    async loadFromIndexedDB() {
        return new Promise((resolve, reject) => {
            const request = indexedDB.open(this.indexedDBName, 1);
            
            request.onerror = () => resolve(null);
            
            request.onsuccess = () => {
                const db = request.result;
                const transaction = db.transaction([this.dbStoreName], 'readonly');
                const store = transaction.objectStore(this.dbStoreName);
                const getRequest = store.get('library.db');
                
                getRequest.onsuccess = () => {
                    const result = getRequest.result;
                    resolve(result ? result.data : null);
                };
                
                getRequest.onerror = () => resolve(null);
            };
            
            request.onupgradeneeded = () => {
                const db = request.result;
                if (!db.objectStoreNames.contains(this.dbStoreName)) {
                    db.createObjectStore(this.dbStoreName, { keyPath: 'id' });
                }
            };
        });
    }

    /**
     * Store database in IndexedDB for persistence
     */
    async storeInIndexedDB(dbBuffer) {
        return new Promise((resolve, reject) => {
            const request = indexedDB.open(this.indexedDBName, 1);
            
            request.onsuccess = () => {
                const db = request.result;
                const transaction = db.transaction([this.dbStoreName], 'readwrite');
                const store = transaction.objectStore(this.dbStoreName);
                
                const putRequest = store.put({
                    id: 'library.db',
                    data: dbBuffer,
                    timestamp: Date.now(),
                    version: this.dbVersion
                });
                
                putRequest.onsuccess = () => resolve();
                putRequest.onerror = () => reject(putRequest.error);
            };
            
            request.onerror = () => reject(request.error);
        });
    }

    /**
     * Search books with exact Phase 2 schema
     * @param {string} query - Search term
     * @param {number|null} categoryId - Filter by category
     * @param {number|null} subjectId - Filter by subject
     * @param {number} limit - Maximum results
     * @returns {Array} Search results
     */
    searchBooks(query = '', categoryId = null, subjectId = null, limit = 50) {
        if (!this.db) {
            throw new Error('Database not initialized');
        }

        let sql = `
            SELECT 
                b.id, 
                b.title, 
                b.author, 
                b.FilePath, 
                b.FileSize, 
                b.PageCount,
                b.Rating,
                b.Notes,
                b.ThumbnailImage,
                c.category, 
                s.subject,
                b.LastOpened
            FROM books b
            LEFT JOIN categories c ON b.category_id = c.id
            LEFT JOIN subjects s ON b.subject_id = s.id
        `;

        const params = [];
        const conditions = [];

        // Search conditions
        if (query && query.trim()) {
            conditions.push('(b.title LIKE ? OR b.author LIKE ? OR s.subject LIKE ?)');
            const searchTerm = `%${query.trim()}%`;
            params.push(searchTerm, searchTerm, searchTerm);
        }

        if (categoryId !== null) {
            conditions.push('b.category_id = ?');
            params.push(categoryId);
        }

        if (subjectId !== null) {
            conditions.push('b.subject_id = ?');
            params.push(subjectId);
        }

        // Add WHERE clause if we have conditions
        if (conditions.length > 0) {
            sql += ' WHERE ' + conditions.join(' AND ');
        }

        // Order and limit
        sql += ' ORDER BY b.title LIMIT ?';
        params.push(limit);

        try {
            const stmt = this.db.prepare(sql);
            const results = [];

            // Bind parameters
            stmt.bind(params);

            while (stmt.step()) {
                const row = stmt.getAsObject();
                // Convert BLOB thumbnail to base64 if present
                if (row.ThumbnailImage) {
                    const uint8Array = new Uint8Array(row.ThumbnailImage);
                    row.ThumbnailImageBase64 = btoa(String.fromCharCode(...uint8Array));
                }
                results.push(row);
            }

            stmt.free();
            return results;

        } catch (error) {
            console.error('Search error:', error);
            return [];
        }
    }

    /**
     * Get all categories
     */
    getCategories() {
        if (!this.db) return [];

        try {
            const stmt = this.db.prepare('SELECT * FROM categories ORDER BY category');
            const results = [];

            while (stmt.step()) {
                results.push(stmt.getAsObject());
            }

            stmt.free();
            return results;

        } catch (error) {
            console.error('Error getting categories:', error);
            return [];
        }
    }

    /**
     * Get subjects for a category
     */
    getSubjects(categoryId = null) {
        if (!this.db) return [];

        let sql = 'SELECT * FROM subjects';
        const params = [];

        if (categoryId !== null) {
            sql += ' WHERE category_id = ?';
            params.push(categoryId);
        }

        sql += ' ORDER BY subject';

        try {
            const stmt = this.db.prepare(sql);
            if (params.length > 0) {
                stmt.bind(params);
            }

            const results = [];
            while (stmt.step()) {
                results.push(stmt.getAsObject());
            }

            stmt.free();
            return results;

        } catch (error) {
            console.error('Error getting subjects:', error);
            return [];
        }
    }

    /**
     * Get book by ID
     */
    getBook(bookId) {
        if (!this.db) return null;

        try {
            const stmt = this.db.prepare(`
                SELECT 
                    b.*, 
                    c.category, 
                    s.subject
                FROM books b
                LEFT JOIN categories c ON b.category_id = c.id
                LEFT JOIN subjects s ON b.subject_id = s.id
                WHERE b.id = ?
            `);

            stmt.bind([bookId]);

            if (stmt.step()) {
                const result = stmt.getAsObject();
                // Convert BLOB thumbnail to base64 if present
                if (result.ThumbnailImage) {
                    const uint8Array = new Uint8Array(result.ThumbnailImage);
                    result.ThumbnailImageBase64 = btoa(String.fromCharCode(...uint8Array));
                }
                stmt.free();
                return result;
            }

            stmt.free();
            return null;

        } catch (error) {
            console.error('Error getting book:', error);
            return null;
        }
    }

    /**
     * Update book's last opened timestamp
     */
    updateLastOpened(bookId) {
        if (!this.db) return false;

        try {
            const stmt = this.db.prepare('UPDATE books SET LastOpened = ? WHERE id = ?');
            stmt.run([new Date().toISOString(), bookId]);
            stmt.free();

            // Persist changes to IndexedDB
            this.persistChanges();
            return true;

        } catch (error) {
            console.error('Error updating last opened:', error);
            return false;
        }
    }

    /**
     * Update book rating
     */
    updateRating(bookId, rating, notes = '') {
        if (!this.db || rating < 0 || rating > 5) return false;

        try {
            const stmt = this.db.prepare('UPDATE books SET Rating = ?, Notes = ? WHERE id = ?');
            stmt.run([rating, notes, bookId]);
            stmt.free();

            // Persist changes to IndexedDB
            this.persistChanges();
            return true;

        } catch (error) {
            console.error('Error updating rating:', error);
            return false;
        }
    }

    /**
     * Get database statistics
     */
    getStats() {
        if (!this.db) return {};

        try {
            const stats = {};

            // Total books
            let stmt = this.db.prepare('SELECT COUNT(*) as count FROM books');
            stmt.step();
            stats.totalBooks = stmt.getAsObject().count;
            stmt.free();

            // Total categories
            stmt = this.db.prepare('SELECT COUNT(*) as count FROM categories');
            stmt.step();
            stats.totalCategories = stmt.getAsObject().count;
            stmt.free();

            // Total subjects
            stmt = this.db.prepare('SELECT COUNT(*) as count FROM subjects');
            stmt.step();
            stats.totalSubjects = stmt.getAsObject().count;
            stmt.free();

            // Books with ratings
            stmt = this.db.prepare('SELECT COUNT(*) as count FROM books WHERE Rating > 0');
            stmt.step();
            stats.ratedBooks = stmt.getAsObject().count;
            stmt.free();

            return stats;

        } catch (error) {
            console.error('Error getting stats:', error);
            return {};
        }
    }

    /**
     * Persist database changes to IndexedDB
     */
    async persistChanges() {
        if (!this.db) return;

        try {
            const dbBuffer = this.db.export();
            await this.storeInIndexedDB(dbBuffer.buffer);
        } catch (error) {
            console.error('Error persisting changes:', error);
        }
    }

    /**
     * Update database with new version
     */
    async updateDatabase(newDbBuffer) {
        try {
            // Close current database
            if (this.db) {
                this.db.close();
            }

            // Load new database
            this.db = new this.SQL.Database(new Uint8Array(newDbBuffer));

            // Store in IndexedDB
            await this.storeInIndexedDB(newDbBuffer);

            console.log('Database updated successfully');
            return true;

        } catch (error) {
            console.error('Error updating database:', error);
            return false;
        }
    }
}

// Create global database instance
window.ourLibraryDB = new OurLibraryDatabase();