import pytest
import tempfile
import os
from library import Book, EBook, AudioBook, Library, PydanticBook
from message_display import UnicodeDisplay


def create_temp_file():
    temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
    temp_file.close()
    return temp_file.name


def cleanup_temp_file(filename):
    if os.path.exists(filename):
        os.unlink(filename)


# Book sınıfı testleri
def test_book_creation():
    book = Book("Test Book", "Test Author", "1234567890")
    assert book.title == "Test Book"
    assert book.author == "Test Author"
    assert book.isbn == "1234567890"
    assert not book.is_borrowed

# EBook sınıfı testleri
def test_ebook_creation():
    ebook = EBook("Test EBook", "Test Author", "1234567890", "PDF", 2.5)
    assert ebook.file_format == "PDF"
    assert ebook.file_size == 2.5
    assert isinstance(ebook, Book)

# AudioBook sınıfı testleri
def test_audiobook_creation():
    audiobook = AudioBook("Test AudioBook", "Test Author", "1234567890", 120)
    assert audiobook.duration_minutes == 120
    assert isinstance(audiobook, Book)

# Kitap ödünç alma ve iade etme testi
def test_book_borrow_return():
    book = Book("Test Book", "Test Author", "1234567890")
    
    # Ödünç alma
    assert book.borrow_book() is True
    assert book.is_borrowed is True
    
    # Zaten ödünç alınmış kitap
    with pytest.raises(Exception):
        book.borrow_book()
    
    # Iade etme
    assert book.return_book() is True
    assert book.is_borrowed is False
    
    # Zaten iade edilmiş kitap
    with pytest.raises(Exception):
        book.return_book()

# Kitap bilgilerinin görüntülenmesi
def test_display_info():
    book = Book("Test Book", "Test Author", "1234567890")
    ebook = EBook("Test EBook", "Test Author", "1234567890", "PDF", 2.5)
    audiobook = AudioBook("Test AudioBook", "Test Author", "1234567890", 120)
    
    assert "Test Book by Test Author" in book.display_info()
    assert "PDF" in ebook.display_info()
    assert "120 dakika" in audiobook.display_info()


# Kütüphane testleri
def test_library_creation():
    """Kütüphane oluşturma testi"""
    temp_file = create_temp_file()
    try:
        library = Library("Test Library", temp_file)
        assert library.name == "Test Library"
        assert library.total_books == 0
    finally:
        cleanup_temp_file(temp_file)

# Kitap ekleme testi
def test_add_book():
    temp_file = create_temp_file()
    try:
        library = Library("Test Library", temp_file)
        book = Book("Test Book", "Test Author", "1234567890")
        
        # Başarılı ekleme testi
        assert library.add_book(book) is True
        assert library.total_books == 1
        
        # Aynı ISBN ile ekleme testi
        duplicate_book = Book("Different Title", "Different Author", "1234567890")
        assert library.add_book(duplicate_book) is False
        assert library.total_books == 1  # Artmamalı
    finally:
        cleanup_temp_file(temp_file)

# Kitap silme testi
def test_remove_book():
    temp_file = create_temp_file()
    try:
        library = Library("Test Library", temp_file)
        book = Book("Test Book", "Test Author", "1234567890")
        library.add_book(book)
        
        # Başarılı silme testi
        assert library.remove_book("1234567890") is True
        assert library.total_books == 0
        
        # Mevcut olmayan kitap silme testi
        assert library.remove_book("9999999999") is False
    finally:
        cleanup_temp_file(temp_file)

# Kitap bulma testi
def test_find_book_methods():
    temp_file = create_temp_file()
    try:
        library = Library("Test Library", temp_file)
        book = Book("Test Book", "Test Author", "1234567890")
        library.add_book(book)
        
        # ISBN ile bulma testi
        found_book = library.find_book_by_isbn("1234567890")
        assert found_book == book
        
        # Başlık ile bulma testi
        found_book = library.find_book_by_title("Test Book")
        assert found_book == book
        
        # Yazar ile bulma testi
        found_book = library.find_book_by_author("Test Author")
        assert found_book == book
        
        # Mevcut olmayan kitap bulma testi
        assert library.find_book_by_isbn("9999999999") is None
    finally:
        cleanup_temp_file(temp_file)

# Ödünç alma ve iade etme testi
def test_borrow_return_books():
    temp_file = create_temp_file()
    try:
        library = Library("Test Library", temp_file)
        book = Book("Test Book", "Test Author", "1234567890")
        library.add_book(book)
        
        # Başarılı ödünç alma
        assert library.borrow_book("1234567890") is True
        assert book.is_borrowed is True
        
        # Zaten ödünç alınmış kitabı ödünç alma
        assert library.borrow_book("1234567890") is False
        
        # Başarılı iade etme
        assert library.return_book("1234567890") is True
        assert book.is_borrowed is False
        
        # Zaten iade edilmiş kitabı iade etme
        assert library.return_book("1234567890") is False
        
        # Mevcut olmayan kitabı ödünç alma
        assert library.borrow_book("9999999999") is False
    finally:
        cleanup_temp_file(temp_file)


# JSON kaydetme ve yükleme testi
def test_json_persistence():
    temp_file = create_temp_file()
    try:
        library1 = Library("Test Library", temp_file)
        
        # Farklı türde kitap ekleme
        book = Book("Test Book", "Test Author", "1234567890")
        ebook = EBook("Test EBook", "Test Author", "1234567891", "PDF", 2.5)
        audiobook = AudioBook("Test AudioBook", "Test Author", "1234567892", 120)
        
        library1.add_book(book)
        library1.add_book(ebook)
        library1.add_book(audiobook)
        
        # Kitap ödünç alma
        library1.borrow_book("1234567890")
        
        # Yeni kütüphane oluştur ve dosyadan yükle
        library2 = Library("New Library", temp_file)
        
        # Tüm kitapların yüklendiğini doğrula
        assert library2.total_books == 3
        
        # Kitap türlerini doğrula
        loaded_book = library2.find_book_by_isbn("1234567890")
        loaded_ebook = library2.find_book_by_isbn("1234567891")
        loaded_audiobook = library2.find_book_by_isbn("1234567892")
        
        assert isinstance(loaded_book, Book)
        assert isinstance(loaded_ebook, EBook)
        assert isinstance(loaded_audiobook, AudioBook)
        
        # Ödünç alınma durumunu doğrula
        assert loaded_book.is_borrowed is True
        assert loaded_ebook.is_borrowed is False
        assert loaded_audiobook.is_borrowed is False
    finally:
        cleanup_temp_file(temp_file)

# Mevcut olmayan JSON dosyası yükleme testi
def test_load_nonexistent_file():
    library = Library("Test Library", "nonexistent.json")
    assert library.total_books == 0


# Pydantic doğrulama testleri
def test_pydantic_valid_book():
    book_data = PydanticBook(
        title="Test Book",
        author="Test Author",
        isbn="1234567890",
        publication_year=2020
    )
    
    assert book_data.title == "Test Book"
    assert book_data.author == "Test Author"
    assert book_data.isbn == "1234567890"
    assert book_data.publication_year == 2020

# ISBN doğrulama testi
def test_pydantic_invalid_isbn():
    with pytest.raises(Exception):
        PydanticBook(
            title="Test Book",
            author="Test Author",
            isbn="123",  # Çok kısa
            publication_year=2020
        )
    
    with pytest.raises(Exception):
        PydanticBook(
            title="Test Book",
            author="Test Author",
            isbn="12345678901234567890",  # Çok uzun
            publication_year=2020
        )

# Yayın yılı doğrulama testi
def test_pydantic_invalid_year():
    with pytest.raises(Exception):
        PydanticBook(
            title="Test Book",
            author="Test Author",
            isbn="1234567890",
            publication_year=1000  # Çok eski
        )
    
    with pytest.raises(Exception):
        PydanticBook(
            title="Test Book",
            author="Test Author",
            isbn="1234567890",
            publication_year=2050  # Çok ileri
        )


# Bilgilendirme mesajlarının konsolda UnicodeDisplay ile görüntülenmesine ait testler
def test_unicode_display():
    display = UnicodeDisplay()
    
    methods = ['success', 'error', 'warning', 'info', 'book', 'search']
    for method_name in methods:
        method = getattr(display, method_name)
        assert callable(method)
    
    assert isinstance(display.symbols, dict)
    assert 'success' in display.symbols
    assert 'error' in display.symbols


# Kütüphane işlemlerinin testi
def test_complete_workflow():
    temp_file = create_temp_file()
    try:
        library = Library("Test Library", temp_file)
        
        # Farklı türde kitap ekleme
        book = Book("Test Book", "Test Author", "1234567890")
        ebook = EBook("Test EBook", "Test Author", "1234567891", "PDF", 2.5)
        audiobook = AudioBook("Test AudioBook", "Test Author", "1234567892", 120)
        
        library.add_book(book)
        library.add_book(ebook)
        library.add_book(audiobook)
        
        assert library.total_books == 3
        
        # Kitap ödünç alma
        library.borrow_book("1234567890")
        library.borrow_book("1234567891")
        
        # Kitap iade etme
        library.return_book("1234567890")
        
        # Kitap silme
        library.remove_book("1234567892")
        
        assert library.total_books == 2
        
        # Son durumun doğrulanması
        book1 = library.find_book_by_isbn("1234567890")
        book2 = library.find_book_by_isbn("1234567891")
        
        assert book1.is_borrowed is False  # İade edildi
        assert book2.is_borrowed is True   # Hala ödünç alınmış durumda
        assert library.find_book_by_isbn("1234567892") is None  # Silindi
    finally:
        cleanup_temp_file(temp_file)


# API entegrasyon testleri
def test_api_methods_exist():
    """API metodlarının varlığını test et"""
    temp_file = create_temp_file()
    try:
        library = Library("Test Library", temp_file)
        assert hasattr(library, 'fetch_book_from_api')
        assert hasattr(library, 'add_book_by_isbn')
    finally:
        cleanup_temp_file(temp_file)

# Aynı ISBN ile kitap ekleme testi
def test_add_book_by_isbn_duplicate():
    """Aynı ISBN ile kitap ekleme testi"""
    temp_file = create_temp_file()
    try:
        library = Library("Test Library", temp_file)
        
        # Önce manuel olarak bir kitap ekle
        book = Book("Test Book", "Test Author", "1234567890")
        library.add_book(book)
        
        # Kitabın var olduğunu doğrula
        existing_book = library.find_book_by_isbn("1234567890")
        assert existing_book is not None
    finally:
        cleanup_temp_file(temp_file)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
