import pytest
from fastapi.testclient import TestClient
from api import app

client = TestClient(app)

test_book = {
    "title": "Test Kitabı",
    "author": "Test Yazarı", 
    "isbn": "9999999999999",  
    "publication_year": 2023
}

test_book_2 = {
    "title": "İkinci Test Kitabı",
    "author": "Başka Yazar",
    "isbn": "0987654321",
    "publication_year": 2022
}

class TestAPI:
    def test_root_endpoint(self):
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "kitap_sayısı" in data
        assert data["message"] == "Kütüphane API"
    
    # Kitap ekleme testi
    def test_add_book_success(self):
        response = client.post("/books", json=test_book)
                
        if response.status_code == 200:
            data = response.json()
            assert data["message"] == "Kitap eklendi"
            assert "kitap" in data
            assert data["kitap"]["title"] == test_book["title"]
        else:
            assert response.status_code == 400
            assert "zaten mevcut" in response.json()["detail"]
    
    # Kitap ekleme testi
    def test_add_book_duplicate_isbn(self):
        client.post("/books", json=test_book)
        response = client.post("/books", json=test_book)
        assert response.status_code == 400
        assert "ISBN zaten mevcut" in response.json()["detail"]

    # Kitap ekleme testi (geçersiz veri)
    def test_add_book_invalid_data(self):
        invalid_book = {
            "title": "Test",
            "author": "Test",
            "isbn": "123", # ISBN 10 haneli olmalı
            "publication_year": 1000  # Yıl 1000'den büyük olmalı
        }
        response = client.post("/books", json=invalid_book)
        assert response.status_code == 422  # Doğrulama hatası
    
    # Tüm kitapları çekme testi
    def test_get_all_books(self):
        client.post("/books", json=test_book_2)
        
        response = client.get("/books")
        assert response.status_code == 200
        books = response.json()
        assert isinstance(books, list)
        assert len(books) >= 1
        
        # Kitap yapısını kontrol et
        if books:
            book = books[0]
            assert "title" in book
            assert "author" in book
            assert "isbn" in book
            assert "borrowed" in book

    # Başlık ile arama testi
    def test_search_books_by_title(self):
        client.post("/books", json=test_book)
        
        response = client.get("/books/search", params={"title": "Test Kitabı"})
        assert response.status_code == 200
        book = response.json()
        assert book["title"] == "Test Kitabı"
    
    # Yazar ile arama testi
    def test_search_books_by_author(self):
        client.post("/books", json=test_book)
        
        response = client.get("/books/search", params={"author": "Test Yazarı"})
        assert response.status_code == 200
        book = response.json()
        assert book["author"] == "Test Yazarı"
    
    # ISBN ile arama testi
    def test_search_books_by_isbn(self):
        client.post("/books", json=test_book)
        
        response = client.get("/books/search", params={"isbn": test_book["isbn"]})
        assert response.status_code == 200
        book = response.json()
        assert book["isbn"] == test_book["isbn"]
    
    # Arama kriteri olmadan arama
    def test_search_books_no_criteria(self):
        response = client.get("/books/search")
        assert response.status_code == 400
        assert "En az bir arama kriteri gerekli" in response.json()["detail"]

    # Mevcut olmayan kitap arama testi
    def test_search_books_not_found(self):
        response = client.get("/books/search", params={"title": "Olmayan Kitap"})
        assert response.status_code == 404
        assert "Kitap bulunamadı" in response.json()["detail"]
    
    # Ödünç alma testi
    def test_borrow_book_success(self):
        client.post("/books", json=test_book)
        
        response = client.patch(f"/books/{test_book['isbn']}/borrow")
        assert response.status_code == 200
        data = response.json()
        assert "ödünç alındı" in data["message"]
    
    # Zaten ödünç alınmış kitabı ödünç alma testi
    def test_borrow_book_already_borrowed(self):
        client.post("/books", json=test_book)
        client.patch(f"/books/{test_book['isbn']}/borrow")  # Önce ödünç al
        
        # Tekrar ödünç almaya çalış
        response = client.patch(f"/books/{test_book['isbn']}/borrow")
        assert response.status_code == 400
        assert "zaten ödünç verildi" in response.json()["detail"]
    
    # İade testi
    def test_return_book_success(self):
        client.post("/books", json=test_book)
        client.patch(f"/books/{test_book['isbn']}/borrow")  # Önce ödünç al
        
        response = client.patch(f"/books/{test_book['isbn']}/return")
        assert response.status_code == 200
        data = response.json()
        assert "iade edildi" in data["message"]
    
    # Ödünç alınmamış kitabı iade etme testi
    def test_return_book_not_borrowed(self):
        client.post("/books", json=test_book)
        
        # Ödünç alınmamış kitabı iade etmeye çalış
        response = client.patch(f"/books/{test_book['isbn']}/return")
        assert response.status_code == 400
        assert "ödünç verilmedi" in response.json()["detail"]
    
    # Mevcut olmayan kitabı ödünç alma testi
    def test_borrow_nonexistent_book(self):
        response = client.patch("/books/9999999999/borrow")
        assert response.status_code == 404
        assert "Kitap bulunamadı" in response.json()["detail"]

    # Mevcut olmayan kitabı iade etme testi
    def test_return_nonexistent_book(self):
        response = client.patch("/books/9999999999/return")
        assert response.status_code == 404
        assert "Kitap bulunamadı" in response.json()["detail"]
    
    # Silme testi
    def test_remove_book_success(self):
        client.post("/books", json=test_book_2)
        
        response = client.delete("/books/0987654321")  # İkinci test kitabını sil
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Kitap silindi"
    
    # Mevcut olmayan kitabı silme testi
    def test_remove_nonexistent_book(self):
        response = client.delete("/books/9999999999")
        assert response.status_code == 404
        assert "Kitap bulunamadı" in response.json()["detail"]

    # İstatistikleri çekme testi
    def test_get_stats(self):
        response = client.get("/stats")
        assert response.status_code == 200
        stats = response.json()
        
        # Gerekli alanları kontrol et
        assert "kütüphane" in stats
        assert "toplam_kitap" in stats
        assert "mevcut_kitap" in stats
        assert "ödünç_kitap" in stats

        # Değerleri kontrol et
        assert stats["toplam_kitap"] >= 0
        assert stats["mevcut_kitap"] >= 0
        assert stats["ödünç_kitap"] >= 0
        assert stats["mevcut_kitap"] + stats["ödünç_kitap"] == stats["toplam_kitap"]

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
