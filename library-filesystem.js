// File: library-filesystem.js
// Path: /home/herb/Desktop/OurLibrary_RealTest/library-filesystem.js
// Standard: AIDEV-PascalCase-2.3
// Created: 2025-01-23
// Last Modified: 2025-01-23 08:30PM

/**
 * OurLibrary Database Manager with File System Integration
 * Backend-style database operations for web applications
 */

class LibraryDatabaseManager {
    constructor() {
        this.fileManager = null;
        this.database = null;
        this.isInitialized = false;
        this.searchIndex = new Map();
    }

    /**
     * Initialize the library with file system integration
     */
    async initialize(fileManager) {
        try {
            this.fileManager = fileManager;
            console.log('🔄 Initializing library database manager...');

            // Load the SQLite database from file system
            await this.loadDatabaseFromFileSystem();
            
            // Build search index
            await this.buildSearchIndex();
            
            this.isInitialized = true;
            console.log('✅ Library database manager initialized successfully');
            
            return { success: true };
            
        } catch (error) {
            console.error('❌ Failed to initialize library database:', error);
            throw error;
        }
    }

    /**
     * Load SQLite database from the user's file system
     */
    async loadDatabaseFromFileSystem() {
        try {
            // Get database directory handle
            const dbDir = await this.fileManager.directoryHandle.getDirectoryHandle('database');
            const dbFile = await dbDir.getFileHandle('library_catalog.db');
            
            // Read database file
            const file = await dbFile.getFile();
            const arrayBuffer = await file.arrayBuffer();
            const dbData = new Uint8Array(arrayBuffer);
            
            console.log(`📚 Loaded database file: ${file.size} bytes`);
            
            // Initialize sql.js with the database
            const SQL = await initSqlJs({
                locateFile: file => `https://sql.js.org/dist/${file}`
            });
            
            this.database = new SQL.Database(dbData);
            console.log('✅ SQLite database loaded successfully');
            
            return { success: true, size: file.size };
            
        } catch (error) {
            console.error('❌ Failed to load database from file system:', error);
            throw error;
        }
    }

    /**
     * Build search index for fast book discovery
     */
    async buildSearchIndex() {
        if (!this.database) {
            throw new Error('Database not loaded');
        }

        try {
            console.log('🔍 Building search index...');
            
            // Get all books from database
            const stmt = this.database.prepare(`
                SELECT id, title, author, description, category, subject, keywords
                FROM books 
                ORDER BY title
            `);
            
            const books = [];
            while (stmt.step()) {
                const row = stmt.getAsObject();
                books.push(row);
                
                // Add to search index
                const searchTerms = [
                    row.title?.toLowerCase() || '',
                    row.author?.toLowerCase() || '',
                    row.description?.toLowerCase() || '',
                    row.category?.toLowerCase() || '',
                    row.subject?.toLowerCase() || '',
                    row.keywords?.toLowerCase() || ''
                ].join(' ');
                
                this.searchIndex.set(row.id, {
                    ...row,
                    searchTerms: searchTerms
                });
            }
            
            stmt.free();
            console.log(`✅ Search index built for ${books.length} books`);
            
            return books;
            
        } catch (error) {
            console.error('❌ Failed to build search index:', error);
            throw error;
        }
    }

    /**
     * Search books using the built index
     */
    searchBooks(query, filters = {}) {
        if (!this.isInitialized) {
            console.error('Database not initialized');
            return [];
        }

        const searchQuery = query.toLowerCase().trim();
        const results = [];

        // Search through index
        for (const [bookId, bookData] of this.searchIndex) {
            let matches = true;

            // Text search
            if (searchQuery && !bookData.searchTerms.includes(searchQuery)) {
                matches = false;
            }

            // Category filter
            if (filters.category && bookData.category !== filters.category) {
                matches = false;
            }

            // Subject filter
            if (filters.subject && bookData.subject !== filters.subject) {
                matches = false;
            }

            if (matches) {
                results.push(bookData);
            }
        }

        // Sort by relevance (title matches first)
        results.sort((a, b) => {
            const aTitle = a.title?.toLowerCase() || '';
            const bTitle = b.title?.toLowerCase() || '';
            
            const aTitleMatch = aTitle.includes(searchQuery);
            const bTitleMatch = bTitle.includes(searchQuery);
            
            if (aTitleMatch && !bTitleMatch) return -1;
            if (!aTitleMatch && bTitleMatch) return 1;
            
            return aTitle.localeCompare(bTitle);
        });

        console.log(`🔍 Search "${query}" returned ${results.length} results`);
        return results;
    }

    /**
     * Get all categories
     */
    getCategories() {
        if (!this.database) return [];

        try {
            const stmt = this.database.prepare(`
                SELECT DISTINCT category 
                FROM books 
                WHERE category IS NOT NULL 
                ORDER BY category
            `);
            
            const categories = [];
            while (stmt.step()) {
                const row = stmt.getAsObject();
                categories.push(row.category);
            }
            
            stmt.free();
            return categories;
            
        } catch (error) {
            console.error('❌ Failed to get categories:', error);
            return [];
        }
    }

    /**
     * Get all subjects for a category
     */
    getSubjects(category = null) {
        if (!this.database) return [];

        try {
            const query = category 
                ? `SELECT DISTINCT subject FROM books WHERE category = ? AND subject IS NOT NULL ORDER BY subject`
                : `SELECT DISTINCT subject FROM books WHERE subject IS NOT NULL ORDER BY subject`;
            
            const stmt = this.database.prepare(query);
            
            if (category) {
                stmt.bind([category]);
            }
            
            const subjects = [];
            while (stmt.step()) {
                const row = stmt.getAsObject();
                subjects.push(row.subject);
            }
            
            stmt.free();
            return subjects;
            
        } catch (error) {
            console.error('❌ Failed to get subjects:', error);
            return [];
        }
    }

    /**
     * Get book details by ID
     */
    getBookById(bookId) {
        if (!this.database) return null;

        try {
            const stmt = this.database.prepare(`
                SELECT * FROM books WHERE id = ?
            `);
            
            stmt.bind([bookId]);
            
            if (stmt.step()) {
                const book = stmt.getAsObject();
                stmt.free();
                return book;
            }
            
            stmt.free();
            return null;
            
        } catch (error) {
            console.error(`❌ Failed to get book ${bookId}:`, error);
            return null;
        }
    }

    /**
     * Download and save a book to user's library
     */
    async downloadBook(bookId, downloadUrl) {
        try {
            console.log(`📥 Downloading book ${bookId}...`);
            
            const book = this.getBookById(bookId);
            if (!book) {
                throw new Error('Book not found');
            }

            // Download book data
            const response = await fetch(downloadUrl);
            if (!response.ok) {
                throw new Error(`Download failed: ${response.status}`);
            }

            const bookData = await response.arrayBuffer();
            
            // Save to file system
            const result = await this.fileManager.saveBook(
                new Uint8Array(bookData), 
                book.title, 
                bookId
            );

            // Update reading progress
            await this.markBookAsDownloaded(bookId);
            
            console.log(`✅ Book downloaded: ${book.title}`);
            return result;
            
        } catch (error) {
            console.error(`❌ Failed to download book ${bookId}:`, error);
            throw error;
        }
    }

    /**
     * Mark book as downloaded in user data
     */
    async markBookAsDownloaded(bookId) {
        try {
            let downloadedBooks = await this.fileManager.loadUserData('downloaded_books') || [];
            
            if (!downloadedBooks.includes(bookId)) {
                downloadedBooks.push(bookId);
                await this.fileManager.saveUserData('downloaded_books', downloadedBooks);
            }
            
        } catch (error) {
            console.error('❌ Failed to update downloaded books list:', error);
        }
    }

    /**
     * Get list of downloaded books
     */
    async getDownloadedBooks() {
        try {
            const downloadedBookIds = await this.fileManager.loadUserData('downloaded_books') || [];
            const downloadedBooks = [];

            for (const bookId of downloadedBookIds) {
                const book = this.getBookById(bookId);
                if (book) {
                    downloadedBooks.push(book);
                }
            }

            return downloadedBooks;
            
        } catch (error) {
            console.error('❌ Failed to get downloaded books:', error);
            return [];
        }
    }

    /**
     * Update reading progress for a book
     */
    async updateReadingProgress(bookId, progress) {
        try {
            let readingProgress = await this.fileManager.loadUserData('reading_progress') || {};
            
            readingProgress[bookId] = {
                ...readingProgress[bookId],
                ...progress,
                lastUpdated: new Date().toISOString()
            };

            await this.fileManager.saveUserData('reading_progress', readingProgress);
            console.log(`📖 Updated reading progress for book ${bookId}`);
            
        } catch (error) {
            console.error('❌ Failed to update reading progress:', error);
        }
    }

    /**
     * Get reading progress for a book
     */
    async getReadingProgress(bookId) {
        try {
            const readingProgress = await this.fileManager.loadUserData('reading_progress') || {};
            return readingProgress[bookId] || null;
            
        } catch (error) {
            console.error('❌ Failed to get reading progress:', error);
            return null;
        }
    }

    /**
     * Add book to bookmarks
     */
    async addBookmark(bookId) {
        try {
            let bookmarks = await this.fileManager.loadUserData('bookmarks') || [];
            
            if (!bookmarks.includes(bookId)) {
                bookmarks.push(bookId);
                await this.fileManager.saveUserData('bookmarks', bookmarks);
                console.log(`⭐ Added book ${bookId} to bookmarks`);
            }
            
        } catch (error) {
            console.error('❌ Failed to add bookmark:', error);
        }
    }

    /**
     * Remove book from bookmarks
     */
    async removeBookmark(bookId) {
        try {
            let bookmarks = await this.fileManager.loadUserData('bookmarks') || [];
            
            bookmarks = bookmarks.filter(id => id !== bookId);
            await this.fileManager.saveUserData('bookmarks', bookmarks);
            console.log(`📌 Removed book ${bookId} from bookmarks`);
            
        } catch (error) {
            console.error('❌ Failed to remove bookmark:', error);
        }
    }

    /**
     * Get bookmarked books
     */
    async getBookmarks() {
        try {
            const bookmarkIds = await this.fileManager.loadUserData('bookmarks') || [];
            const bookmarks = [];

            for (const bookId of bookmarkIds) {
                const book = this.getBookById(bookId);
                if (book) {
                    bookmarks.push(book);
                }
            }

            return bookmarks;
            
        } catch (error) {
            console.error('❌ Failed to get bookmarks:', error);
            return [];
        }
    }

    /**
     * Get library statistics
     */
    async getLibraryStats() {
        try {
            const totalBooks = this.searchIndex.size;
            const categories = this.getCategories();
            const downloadedBooks = await this.getDownloadedBooks();
            const bookmarks = await this.getBookmarks();
            const fileStats = await this.fileManager.getDirectoryStats();

            return {
                totalBooks: totalBooks,
                totalCategories: categories.length,
                downloadedBooks: downloadedBooks.length,
                bookmarks: bookmarks.length,
                diskUsage: fileStats
            };
            
        } catch (error) {
            console.error('❌ Failed to get library stats:', error);
            return null;
        }
    }
}

// Export for use in other modules
window.LibraryDatabaseManager = LibraryDatabaseManager;