from typing import Optional, List, Dict, Any
from pydantic import ValidationError
from library import Library, Book, EBook, AudioBook, PydanticBook
from dataclasses import dataclass


# DB'de saklanacak alanları içeren genişletilmiş kitap verisi
@dataclass
class BookData:
    title: str
    author: str
    isbn: str
    publication_year: Optional[int] = None
    is_borrowed: bool = False


class WebManager:
    """
    Manager layer, CLI'deki main.py gibi çalışıyor. Pydantic ile doğrulama, iş mantığı, veritabanı işlemleri, 
    veri dönüşümü gibi işlemleri yapıyor.
    - Pydantic doğrulama 
    - İş mantığı
    - DB işlemleri
    - API ve domain arasında veri dönüşümü
    """
    
    def __init__(self, library_name: str, db_file: str = "web_library.db"):
        self.library = Library(library_name, db_file)
    
    # Pydantic ile doğrulama
    def validate_book_data(self, data: Dict[str, Any]) -> PydanticBook:
        try:
            return PydanticBook(**data)
        except ValidationError as e:
            raise ValidationError(f"Validation failed: {e}")
    
    # Kitap ekleme
    def add_manual_book(self, book_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            validated_book = self.validate_book_data(book_data)
            book = Book(validated_book.title, validated_book.author, validated_book.isbn)
            success = self.library.add_book(book)
            
            if success:
                return {
                    "success": True,
                    "message": "Kitap başarıyla eklendi",
                    "book": self._book_to_dict(book, validated_book.publication_year)
                }
            else:
                return {
                    "success": False,
                    "message": "Kitap eklenemedi - ISBN zaten mevcut"
                }
                
        except ValidationError as e:
            return {
                "success": False,
                "message": f"Validation failed: {e}",
                "validation_errors": self._format_validation_errors(e)
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Unexpected error: {e}"
            }
    # ISBN ile kitap ekleme
    def add_book_by_isbn(self, isbn: str) -> Dict[str, Any]:
        try:
            # Check if book already exists first (like the library does)
            existing_book = self.library.find_book_by_isbn(isbn)
            if existing_book:
                return {
                    "success": False,
                    "message": "Kitap eklenemedi - ISBN zaten mevcut"
                }
            
            success = self.library.add_book_by_isbn(isbn)
            
            if success:
                book = self.library.find_book_by_isbn(isbn)
                return {
                    "success": True,
                    "message": "Kitap ISBN ile başarıyla eklendi",
                    "book": self._book_to_dict(book)
                }
            else:
                return {
                    "success": False,
                    "message": "Kitap eklenemedi - ISBN OpenLibrary'de bulunamadı, lütfen manuel ekleme yapın"
                }
                
        except Exception as e:
            return {
                "success": False,
                "message": f"Error: {e}"
            }
    
    def get_all_books(self) -> List[Dict[str, Any]]:
        return [self._book_to_dict(book) for book in self.library._books]
    
    # Kitap arama
    def search_books(self, title: str = "", author: str = "", isbn: str = "") -> Optional[Dict[str, Any]]:
        if title:
            book = self.library.find_book_by_title(title)
            if book:
                return self._book_to_dict(book)
        
        if author:
            book = self.library.find_book_by_author(author)
            if book:
                return self._book_to_dict(book)
        
        # Try ISBN search
        if isbn:
            book = self.library.find_book_by_isbn(isbn)
            if book:
                return self._book_to_dict(book)
        
        return None
    
    # Kitap ödünç alma
    def borrow_book(self, isbn: str) -> Dict[str, Any]:
        try:
            success = self.library.borrow_book(isbn)
            if success:
                book = self.library.find_book_by_isbn(isbn)
                return {
                    "success": True,
                    "message": f"'{book.title}' ödünç alındı"
                }
            else:
                return {
                    "success": False,
                    "message": "Kitap ödünç alınamadı - kitap bulunamadı veya zaten ödünç verildi"
                }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error: {e}"
            }
    
    # Kitap iade etme
    def return_book(self, isbn: str) -> Dict[str, Any]:
        try:
            success = self.library.return_book(isbn)
            if success:
                book = self.library.find_book_by_isbn(isbn)
                return {
                    "success": True,
                    "message": f"'{book.title}' iade edildi"
                }
            else:
                return {
                    "success": False,
                    "message": "Kitap iade edilemedi - kitap bulunamadı veya zaten iade edildi"
                }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error: {e}"
            }
    # Kitap silme
    def remove_book(self, isbn: str) -> Dict[str, Any]:
        try:
            success = self.library.remove_book(isbn)
            if success:
                return {
                    "success": True,
                    "message": "Kitap silindi"
                }
            else:
                return {
                    "success": False,
                    "message": "Kitap bulunamadı"
                }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error: {e}"
            }
        
    # Kütüphane istatistikleri
    def get_stats(self) -> Dict[str, Any]:
        total = self.library.total_books
        borrowed = sum(1 for book in self.library._books if book.is_borrowed)
        return {
            "kütüphane": self.library.name,
            "toplam_kitap": total,
            "mevcut_kitap": total - borrowed,
            "ödünç_kitap": borrowed
        }
    
    # Yardımcı metotlar
    def _book_to_dict(self, book: Book, publication_year: Optional[int] = None) -> Dict[str, Any]:
        return {
            "title": book.title,
            "author": book.author,
            "isbn": book.isbn,
            "publication_year": publication_year,  
            "borrowed": book.is_borrowed
        }
    
    def _format_validation_errors(self, error: ValidationError) -> List[Dict[str, Any]]:
        formatted_errors = []
        for err in error.errors():
            formatted_errors.append({
                "field": err["loc"][0] if err["loc"] else "unknown",
                "message": err["msg"],
                "type": err["type"]
            })
        return formatted_errors
