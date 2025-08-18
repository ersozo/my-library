const API_BASE = 'http://localhost:8000';

// Alpine.js uygulaması
function libraryApp() {
    return {
        // Data
        books: [],
        message: '',
        messageType: 'info',
        stats: {
            toplam_kitap: 0,
            mevcut_kitap: 0,
            ödünç_kitap: 0,
            kütüphane: 'Kütüphane Web Demo'
        },
        
        // Formlar
        bookForm: {
            title: '',
            author: '',
            isbn: '',
            publication_year: new Date().getFullYear(),
            loading: false
        },
        
        isbnForm: {
            isbn: '',
            loading: false
        },
        
        searchForm: {
            title: '',
            author: '',
            isbn: '',
            loading: false
        },
        
        searchResults: [],
        searchPerformed: false,

        // Hesaplanan
        get messageClass() {
            const baseClasses = 'p-4 rounded-lg shadow-sm';
            switch (this.messageType) {
                case 'success':
                    return `${baseClasses} bg-green-100 border border-green-200 text-green-800`;
                case 'error':
                    return `${baseClasses} bg-red-100 border border-red-200 text-red-800`;
                case 'warning':
                    return `${baseClasses} bg-yellow-100 border border-yellow-200 text-yellow-800`;
                default:
                    return `${baseClasses} bg-blue-100 border border-blue-200 text-blue-800`;
            }
        },

        get statsText() {
            return `Toplam: ${this.stats.toplam_kitap} | Mevcut: ${this.stats.mevcut_kitap} | Ödünç: ${this.stats.ödünç_kitap}`;
        },

        // Yaşam döngüsü
        async init() {
            await this.loadBooks();
            await this.loadStats();
            this.showMessage('📚 Kütüphane sistemi yüklendi - SQLite veritabanı aktif!', 'success');
        },

        // API methodları
        async apiCall(endpoint, options = {}) {
            try {
                const response = await fetch(`${API_BASE}${endpoint}`, {
                    headers: {
                        'Content-Type': 'application/json',
                        ...options.headers
                    },
                    ...options
                });

                if (!response.ok) {
                    const error = await response.json().catch(() => ({ detail: 'Bilinmeyen hata' }));
                    throw new Error(error.detail || `HTTP ${response.status}`);
                }

                return await response.json();
            } catch (error) {
                console.error('API Hatası:', error);
                throw error;
            }
        },

        // Veri yükleme
        async loadBooks() {
            try {
                this.books = await this.apiCall('/books');
            } catch (error) {
                this.showMessage(`📚 Kitaplar yüklenirken hata: ${error.message}`, 'error');
            }
        },

        async loadStats() {
            try {
                this.stats = await this.apiCall('/stats');
            } catch (error) {
                this.showMessage(`📊 İstatistikler yüklenirken hata: ${error.message}`, 'error');
            }
        },

        // Kitap işlemleri
        async addBook() {
            if (this.bookForm.loading) return;
            
            this.bookForm.loading = true;
            try {
                const result = await this.apiCall('/books', {
                    method: 'POST',
                    body: JSON.stringify({
                        title: this.bookForm.title.trim(),
                        author: this.bookForm.author.trim(),
                        isbn: this.bookForm.isbn.trim(),
                        publication_year: parseInt(this.bookForm.publication_year)
                    })
                });

                this.showMessage(`✅ ${result.message}: "${result.kitap.title}"`, 'success');
                this.resetBookForm();
                await this.loadBooks();
                await this.loadStats();
            } catch (error) {
                this.showMessage(`❌ Kitap eklenirken hata: ${error.message}`, 'error');
            } finally {
                this.bookForm.loading = false;
            }
        },

        async addBookByIsbn() {
            if (this.isbnForm.loading) return;
            
            const isbn = this.isbnForm.isbn.trim();
            if (!isbn) {
                this.showMessage('❌ ISBN numarası gerekli', 'error');
                return;
            }

            this.isbnForm.loading = true;
            this.showMessage('📡 OpenLibrary API\'den kitap bilgileri alınıyor... (15 saniye bekleyebilir)', 'info');

            try {
                const result = await this.apiCall('/books/isbn', {
                    method: 'POST',
                    body: JSON.stringify({ isbn: isbn })
                });

                this.showMessage(`✅ ${result.message}: "${result.kitap.title}" - ${result.kitap.author}`, 'success');
                this.isbnForm.isbn = '';
                await this.loadBooks();
                await this.loadStats();
            } catch (error) {
                this.showMessage(`❌ ISBN ile kitap eklenirken hata: ${error.message}`, 'error');
            } finally {
                this.isbnForm.loading = false;
            }
        },

        async removeBook(isbn) {
            if (!confirm('Bu kitabı silmek istediğinizden emin misiniz?')) {
                return;
            }

            try {
                const result = await this.apiCall(`/books/${isbn}`, {
                    method: 'DELETE'
                });

                this.showMessage(`✅ ${result.message}`, 'success');
                await this.loadBooks();
                await this.loadStats();
            } catch (error) {
                this.showMessage(`❌ Kitap silinirken hata: ${error.message}`, 'error');
            }
        },

        async toggleBorrow(isbn, currentlyBorrowed) {
            const action = currentlyBorrowed ? 'return' : 'borrow';
            const actionText = currentlyBorrowed ? 'iade edilirken' : 'ödünç alınırken';

            try {
                const result = await this.apiCall(`/books/${isbn}/${action}`, {
                    method: 'PATCH'
                });

                this.showMessage(`✅ ${result.message}`, 'success');
                await this.loadBooks();
                await this.loadStats();
            } catch (error) {
                this.showMessage(`❌ Kitap ${actionText} hata: ${error.message}`, 'error');
            }
        },

        // Arama işlemleri
        async searchBooks() {
            if (this.searchForm.loading) return;

            const { title, author, isbn } = this.searchForm;
            
            // En az bir alanın doldurulması gerekiyor
            if (!title.trim() && !author.trim() && !isbn.trim()) {
                this.showMessage('❌ En az bir arama kriteri giriniz', 'error');
                return;
            }

            this.searchForm.loading = true;
            this.searchPerformed = false;

            try {
                const params = new URLSearchParams();
                if (title.trim()) params.append('title', title.trim());
                if (author.trim()) params.append('author', author.trim());
                if (isbn.trim()) params.append('isbn', isbn.trim());

                const result = await this.apiCall(`/books/search?${params.toString()}`);
                
                // API bir kitap nesnesi döndürür, tutarlılık için diziye çevir
                this.searchResults = result ? [result] : [];
                this.searchPerformed = true;
                
                if (this.searchResults.length > 0) {
                    this.showMessage(`✅ ${this.searchResults.length} kitap bulundu`, 'success');
                } else {
                    this.showMessage('ℹ️ Arama kriterlerine uygun kitap bulunamadı', 'info');
                }
            } catch (error) {
                this.searchResults = [];
                this.searchPerformed = true;
                this.showMessage(`❌ Arama yapılırken hata: ${error.message}`, 'error');
            } finally {
                this.searchForm.loading = false;
            }
        },

        clearSearch() {
            this.searchForm = {
                title: '',
                author: '',
                isbn: '',
                loading: false
            };
            this.searchResults = [];
            this.searchPerformed = false;
            this.showMessage('🗑️ Arama temizlendi', 'info');
        },

        // Yardımcı methodlar
        showMessage(text, type = 'info') {
            this.message = text;
            this.messageType = type;
            
            // bilgilendirme mesajlarının otomatik gizlenmesi (5sn)
            if (type === 'success' || type === 'info') {
                setTimeout(() => {
                    this.message = '';
                }, 5000);
            }
        },

        resetBookForm() {
            this.bookForm = {
                title: '',
                author: '',
                isbn: '',
                publication_year: new Date().getFullYear(),
                loading: false
            };
        }
    }
}

document.addEventListener('DOMContentLoaded', function() {
    console.log('📚 Kütüphane Web Uygulaması başlatıldı');
    console.log('🗄️ SQLite veritabanı backend ile çalışıyor');
    console.log('🌐 API Base URL:', API_BASE);
});
