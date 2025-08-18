import pytest
import httpx
from fastapi.testclient import TestClient
from api import app

# Create test client
client = TestClient(app)

# Test data
test_book = {
    "title": "Test Kitabı",
    "author": "Test Yazarı", 
    "isbn": "1234567890",
    "publication_year": 2023
}

test_book_2 = {
    "title": "İkinci Test Kitabı",
    "author": "Başka Yazar",
    "isbn": "0987654321",
    "publication_year": 2022
}

class TestAPI:
    """API test class"""
    
    def test_root_endpoint(self):
        """Test root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "kitap_sayısı" in data
        assert data["message"] == "Kütüphane API"
    
    def test_add_book_success(self):
        """Test successful book addition"""
        response = client.post("/books", json=test_book)
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Kitap eklendi"
        assert "kitap" in data
        assert data["kitap"]["title"] == test_book["title"]
    
    def test_add_book_duplicate_isbn(self):
        """Test adding book with duplicate ISBN"""
        # First add should succeed
        client.post("/books", json=test_book)
        
        # Second add with same ISBN should fail
        response = client.post("/books", json=test_book)
        assert response.status_code == 400
        assert "ISBN zaten mevcut" in response.json()["detail"]
    
    def test_add_book_invalid_data(self):
        """Test adding book with invalid data"""
        invalid_book = {
            "title": "Test",
            "author": "Test",
            "isbn": "123",  # Too short
            "publication_year": 1000  # Too old
        }
        response = client.post("/books", json=invalid_book)
        assert response.status_code == 422  # Validation error
    
    def test_get_all_books(self):
        """Test getting all books"""
        # Add a book first
        client.post("/books", json=test_book_2)
        
        response = client.get("/books")
        assert response.status_code == 200
        books = response.json()
        assert isinstance(books, list)
        assert len(books) >= 1
        
        # Check book structure
        if books:
            book = books[0]
            assert "title" in book
            assert "author" in book
            assert "isbn" in book
            assert "borrowed" in book
    
    def test_search_books_by_title(self):
        """Test searching books by title"""
        # First add a book to search for
        client.post("/books", json=test_book)
        
        response = client.get("/books/search", params={"title": "Test Kitabı"})
        assert response.status_code == 200
        book = response.json()
        assert book["title"] == "Test Kitabı"
    
    def test_search_books_by_author(self):
        """Test searching books by author"""
        # First add a book to search for
        client.post("/books", json=test_book)
        
        response = client.get("/books/search", params={"author": "Test Yazarı"})
        assert response.status_code == 200
        book = response.json()
        assert book["author"] == "Test Yazarı"
    
    def test_search_books_by_isbn(self):
        """Test searching books by ISBN"""
        # First add a book to search for
        client.post("/books", json=test_book)
        
        response = client.get("/books/search", params={"isbn": "1234567890"})
        assert response.status_code == 200
        book = response.json()
        assert book["isbn"] == "1234567890"
    
    def test_search_books_no_criteria(self):
        """Test search without any criteria"""
        response = client.get("/books/search")
        assert response.status_code == 400
        assert "En az bir arama kriteri gerekli" in response.json()["detail"]
    
    def test_search_books_not_found(self):
        """Test searching for non-existent book"""
        response = client.get("/books/search", params={"title": "Olmayan Kitap"})
        assert response.status_code == 404
        assert "Kitap bulunamadı" in response.json()["detail"]
    
    def test_borrow_book_success(self):
        """Test successful book borrowing"""
        # First add a book to borrow
        client.post("/books", json=test_book)
        
        response = client.patch("/books/1234567890/borrow")
        assert response.status_code == 200
        data = response.json()
        assert "ödünç alındı" in data["message"]
    
    def test_borrow_book_already_borrowed(self):
        """Test borrowing already borrowed book"""
        # First add and borrow a book
        client.post("/books", json=test_book)
        client.patch("/books/1234567890/borrow")  # First borrow
        
        # Try to borrow again
        response = client.patch("/books/1234567890/borrow")
        assert response.status_code == 400
        assert "zaten ödünç verildi" in response.json()["detail"]
    
    def test_return_book_success(self):
        """Test successful book return"""
        # First add and borrow a book
        client.post("/books", json=test_book)
        client.patch("/books/1234567890/borrow")  # Borrow first
        
        response = client.patch("/books/1234567890/return")
        assert response.status_code == 200
        data = response.json()
        assert "iade edildi" in data["message"]
    
    def test_return_book_not_borrowed(self):
        """Test returning non-borrowed book"""
        # First add a book (but don't borrow it)
        client.post("/books", json=test_book)
        
        # Try to return non-borrowed book
        response = client.patch("/books/1234567890/return")
        assert response.status_code == 400
        assert "ödünç verilmedi" in response.json()["detail"]
    
    def test_borrow_nonexistent_book(self):
        """Test borrowing non-existent book"""
        response = client.patch("/books/9999999999/borrow")
        assert response.status_code == 404
        assert "Kitap bulunamadı" in response.json()["detail"]
    
    def test_return_nonexistent_book(self):
        """Test returning non-existent book"""
        response = client.patch("/books/9999999999/return")
        assert response.status_code == 404
        assert "Kitap bulunamadı" in response.json()["detail"]
    
    def test_remove_book_success(self):
        """Test successful book removal"""
        # First add the book to remove
        client.post("/books", json=test_book_2)
        
        response = client.delete("/books/0987654321")  # Remove second test book
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Kitap silindi"
    
    def test_remove_nonexistent_book(self):
        """Test removing non-existent book"""
        response = client.delete("/books/9999999999")
        assert response.status_code == 404
        assert "Kitap bulunamadı" in response.json()["detail"]
    
    def test_get_stats(self):
        """Test getting library statistics"""
        response = client.get("/stats")
        assert response.status_code == 200
        stats = response.json()
        
        # Check required fields
        assert "kütüphane" in stats
        assert "toplam_kitap" in stats
        assert "mevcut_kitap" in stats
        assert "ödünç_kitap" in stats
        
        # Check values are reasonable
        assert stats["toplam_kitap"] >= 0
        assert stats["mevcut_kitap"] >= 0
        assert stats["ödünç_kitap"] >= 0
        assert stats["mevcut_kitap"] + stats["ödünç_kitap"] == stats["toplam_kitap"]

# Fixtures for setup and teardown
@pytest.fixture(autouse=True)
def reset_library():
    """Reset library before each test"""
    # Clear all books from library
    from api import library
    library._books.clear()
    yield
    # Cleanup after test (optional)
    library._books.clear()

# Integration test using httpx (alternative to TestClient)
@pytest.mark.asyncio
async def test_api_with_httpx():
    """Test API using httpx async client"""
    from httpx import AsyncClient
    from httpx._transports.asgi import ASGITransport
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Reset library for this test
        from api import library
        library._books.clear()
        
        # Test root endpoint
        response = await ac.get("/")
        assert response.status_code == 200
        
        # Test adding a book
        response = await ac.post("/books", json=test_book)
        assert response.status_code == 200
        
        # Test getting books
        response = await ac.get("/books")
        assert response.status_code == 200
        books = response.json()
        assert len(books) == 1

if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "--tb=short"])
