from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from web_manager import WebManager
from library import PydanticBook
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

web_manager = WebManager("Kütüphane Web Demo", "web_library.db")

# Ana sayfa
@app.get("/", summary="Ana Sayfa")
def root():
    return {"message": "Kütüphane API", "kitap_sayısı": web_manager.library.total_books}

# Kitap ekleme
@app.post("/books", summary="Kitap Ekle")
def add_book(book_data: PydanticBook):
    result = web_manager.add_manual_book(book_data.model_dump())
    if result["success"]:
        return {"message": result["message"], "kitap": result["book"]}
    raise HTTPException(400, result["message"])

# Tüm kitapları listeleme
@app.get("/books", summary="Tüm Kitapları Listele")
def get_books():
    return web_manager.get_all_books()

# Kitap bulma
@app.get("/books/search", summary="Kitap Ara")
def search_books(title: str = "", author: str = "", isbn: str = ""):
    if not title and not author and not isbn:
        raise HTTPException(400, "En az bir arama kriteri gerekli")
    
    result = web_manager.search_books(title, author, isbn)
    if result:
        return result
    raise HTTPException(404, "Kitap bulunamadı")

# Kitap silme
@app.delete("/books/{isbn}")
def remove_book(isbn: str):
    result = web_manager.remove_book(isbn)
    if result["success"]:
        return {"message": result["message"]}
    raise HTTPException(404, result["message"])

# Kitap ödünç alma
@app.patch("/books/{isbn}/borrow")
def borrow_book(isbn: str):
    result = web_manager.borrow_book(isbn)
    if result["success"]:
        return {"message": result["message"]}
    raise HTTPException(400, result["message"])

# Kitap iade etme
@app.patch("/books/{isbn}/return")
def return_book(isbn: str):
    result = web_manager.return_book(isbn)
    if result["success"]:
        return {"message": result["message"]}
    raise HTTPException(400, result["message"])

# Kütüphane istatistikleri
@app.get("/stats")
def get_stats():
    return web_manager.get_stats()

# ISBN ile kitap ekleme
@app.post("/books/isbn", summary="ISBN ile Kitap Ekle")
def add_book_by_isbn(isbn_data: dict):
    isbn = isbn_data.get("isbn", "").strip()
    if not isbn:
        raise HTTPException(400, detail="ISBN gerekli")
    
    result = web_manager.add_book_by_isbn(isbn)
    if result["success"]:
        return {"message": result["message"], "kitap": result["book"]}    
    raise HTTPException(400, detail=result["message"])

if __name__ == "__main__":
    import uvicorn
    display = UnicodeDisplay()
    display.info("Kütüphane API başlatılıyor...")
    display.info("Swagger Dokümantasyonu: http://localhost:8000/docs")
    display.info("ReDoc Dokümantasyonu: http://localhost:8000/redoc")
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
