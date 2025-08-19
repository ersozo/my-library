from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from library import Library, Book, PydanticBook
from message_display import UnicodeDisplay

app = FastAPI(
    title="Kütüphane API",
    description="Kütüphane Yönetim Sistemi API",
    version="1.0.0"
)

# CORS middleware ekle
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

library = Library("Kütüphane Web Demo", "web_library.db")

# Ana sayfa
@app.get("/", summary="Ana Sayfa")
def root():
    return {"message": "Kütüphane API", "kitap_sayısı": library.total_books}

# Kitap ekleme
@app.post("/books", summary="Kitap Ekle")
def add_book(book_data: PydanticBook):
    book = Book(book_data.title, book_data.author, book_data.isbn)
    success = library.add_book(book)
    if success:
        return {"message": "Kitap eklendi", "kitap": book_data.model_dump()}
    raise HTTPException(400, "Kitap eklenemedi - ISBN zaten mevcut")

# Tüm kitapları listeleme
@app.get("/books", summary="Tüm Kitapları Listele")
def get_books():
    return [{"title": b.title, "author": b.author, "isbn": b.isbn, "borrowed": b.is_borrowed} 
            for b in library._books]

# Kitap bulma
@app.get("/books/search", summary="Kitap Ara")
def search_books(title: str = "", author: str = "", isbn: str = ""):
    if not title and not author and not isbn:
        raise HTTPException(400, "En az bir arama kriteri gerekli")
    
    # Başlık ile arama
    if title:
        book = library.find_book_by_title(title)
        if book:
            return {"title": book.title, "author": book.author, "isbn": book.isbn, "borrowed": book.is_borrowed}
    
    # Yazar ile arama
    if author:
        book = library.find_book_by_author(author)
        if book:
            return {"title": book.title, "author": book.author, "isbn": book.isbn, "borrowed": book.is_borrowed}
    
    # ISBN ile arama
    if isbn:
        book = library.find_book_by_isbn(isbn)
        if book:
            return {"title": book.title, "author": book.author, "isbn": book.isbn, "borrowed": book.is_borrowed}
    
    raise HTTPException(404, "Kitap bulunamadı")

# Kitap silme
@app.delete("/books/{isbn}")
def remove_book(isbn: str):
    success = library.remove_book(isbn)
    if success:
        return {"message": "Kitap silindi"}
    raise HTTPException(404, "Kitap bulunamadı")

# Kitap ödünç alma
@app.patch("/books/{isbn}/borrow")
def borrow_book(isbn: str):
    success = library.borrow_book(isbn)
    if success:
        book = library.find_book_by_isbn(isbn)
        return {"message": f"'{book.title}' ödünç alındı"}
    raise HTTPException(400, "Kitap ödünç alınamadı - kitap bulunamadı veya zaten ödünç verildi")

# Kitap iade etme
@app.patch("/books/{isbn}/return")
def return_book(isbn: str):
    success = library.return_book(isbn)
    if success:
        book = library.find_book_by_isbn(isbn)
        return {"message": f"'{book.title}' iade edildi"}
    raise HTTPException(400, "Kitap iade edilemedi - kitap bulunamadı veya zaten iade edildi")

# Kütüphane istatistikleri
@app.get("/stats")
def get_stats():
    total = library.total_books
    borrowed = sum(1 for book in library._books if book.is_borrowed)
    return {
        "kütüphane": library.name,
        "toplam_kitap": total,
        "mevcut_kitap": total - borrowed,
        "ödünç_kitap": borrowed
    }

# ISBN ile kitap ekleme
@app.post("/books/isbn", summary="ISBN ile Kitap Ekle")
def add_book_by_isbn(isbn_data: dict):
    isbn = isbn_data.get("isbn", "").strip()
    if not isbn:
        raise HTTPException(400, "ISBN gerekli")
    
    success = library.add_book_by_isbn(isbn)
    if success:
        book = library.find_book_by_isbn(isbn)
        if book:
            return {
                "message": "Kitap ISBN ile başarıyla eklendi", 
                "kitap": {
                    "title": book.title,
                    "author": book.author,
                    "isbn": book.isbn,
                    "borrowed": book.is_borrowed
                }
            }
    raise HTTPException(400, "Kitap eklenemedi - ISBN ile kitap bulunamadı veya zaten mevcut")

if __name__ == "__main__":
    import uvicorn
    display = UnicodeDisplay()
    display.info("Kütüphane API başlatılıyor...")
    display.info("Swagger Dokümantasyonu: http://localhost:8000/docs")
    display.info("ReDoc Dokümantasyonu: http://localhost:8000/redoc")
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
