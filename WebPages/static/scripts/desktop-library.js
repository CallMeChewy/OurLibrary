/* File: desktop-library.js
 * Path: /home/herb/Desktop/AndyLibrary/WebPages/static/scripts/desktop-library.js
 * Standard: AIDEV-PascalCase-2.1
 * Created: 2025-08-04
 * Last Modified: 2025-08-04 10:32AM
 */

/**
 * Desktop Library JavaScript Functions
 * Handles search, book display, and user interactions
 */

class DesktopLibrary {
    constructor() {
        this.books = [];
        this.filteredBooks = [];
        this.currentSearch = '';
        this.isLoading = false;
        this.init();
    }

    async init() {
        this.setupEventListeners();
        await this.loadBooks();
        this.renderBooks();
    }

    setupEventListeners() {
        const searchInput = document.getElementById('searchInput');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                this.handleSearch(e.target.value);
            });
        }

        // Add keyboard navigation
        document.addEventListener('keydown', (e) => {
            if (e.key === '/' && e.target.tagName !== 'INPUT') {
                e.preventDefault();
                searchInput?.focus();
            }
        });
    }

    async loadBooks() {
        this.setLoading(true);
        try {
            const response = await fetch('/api/books');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();
            this.books = data.books || [];
            this.filteredBooks = [...this.books];
        } catch (error) {
            console.error('Error loading books:', error);
            this.showError('Failed to load books. Please try again later.');
        } finally {
            this.setLoading(false);
        }
    }

    handleSearch(query) {
        this.currentSearch = query.toLowerCase().trim();
        
        if (!this.currentSearch) {
            this.filteredBooks = [...this.books];
        } else {
            this.filteredBooks = this.books.filter(book => {
                return (
                    book.title?.toLowerCase().includes(this.currentSearch) ||
                    book.author?.toLowerCase().includes(this.currentSearch) ||
                    book.subject?.toLowerCase().includes(this.currentSearch) ||
                    book.description?.toLowerCase().includes(this.currentSearch)
                );
            });
        }
        
        this.renderBooks();
    }

    renderBooks() {
        const container = document.getElementById('booksContainer');
        if (!container) return;

        if (this.isLoading) {
            container.innerHTML = '<div class="loading">Loading books...</div>';
            return;
        }

        if (this.filteredBooks.length === 0) {
            const message = this.currentSearch 
                ? `No books found matching "${this.currentSearch}"`
                : 'No books available';
            container.innerHTML = `<div class="loading">${message}</div>`;
            return;
        }

        const booksHTML = this.filteredBooks.map(book => this.createBookCard(book)).join('');
        container.innerHTML = booksHTML;

        // Add click handlers to book cards
        this.attachBookCardHandlers();
    }

    createBookCard(book) {
        const title = this.escapeHtml(book.title || 'Unknown Title');
        const author = this.escapeHtml(book.author || 'Unknown Author');
        const subject = this.escapeHtml(book.subject || 'General');
        const bookId = book.id || book.book_id || '';

        return `
            <div class="book-card" data-book-id="${bookId}">
                <div class="book-title">${title}</div>
                <div class="book-author">by ${author}</div>
                <div class="book-subject">${subject}</div>
                ${book.description ? `<div class="book-description">${this.escapeHtml(book.description.substring(0, 100))}${book.description.length > 100 ? '...' : ''}</div>` : ''}
            </div>
        `;
    }

    attachBookCardHandlers() {
        const bookCards = document.querySelectorAll('.book-card');
        bookCards.forEach(card => {
            card.addEventListener('click', () => {
                const bookId = card.dataset.bookId;
                if (bookId) {
                    this.openBook(bookId);
                }
            });

            // Add hover effect
            card.addEventListener('mouseenter', () => {
                card.style.transform = 'translateY(-2px)';
            });

            card.addEventListener('mouseleave', () => {
                card.style.transform = 'translateY(0)';
            });
        });
    }

    async openBook(bookId) {
        try {
            // Try to get book URL from API
            const response = await fetch(`/api/books/${bookId}/url`);
            if (response.ok) {
                const data = await response.json();
                if (data.url) {
                    window.open(data.url, '_blank');
                    return;
                }
            }
            
            // Fallback: open book detail page
            window.open(`/api/books/${bookId}`, '_blank');
        } catch (error) {
            console.error('Error opening book:', error);
            this.showError('Failed to open book. Please try again.');
        }
    }

    setLoading(loading) {
        this.isLoading = loading;
        const container = document.getElementById('booksContainer');
        if (container && loading) {
            container.innerHTML = '<div class="loading">Loading books...</div>';
        }
    }

    showError(message) {
        const container = document.getElementById('booksContainer');
        if (container) {
            container.innerHTML = `<div class="error-message">${this.escapeHtml(message)}</div>`;
        }
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    // Public methods for external use
    refresh() {
        this.loadBooks().then(() => this.renderBooks());
    }

    search(query) {
        const searchInput = document.getElementById('searchInput');
        if (searchInput) {
            searchInput.value = query;
        }
        this.handleSearch(query);
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.libraryApp = new DesktopLibrary();
});

// Export for module use if needed
if (typeof module !== 'undefined' && module.exports) {
    module.exports = DesktopLibrary;
}