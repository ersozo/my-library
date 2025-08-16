from dataclasses import dataclass, field
from typing import List
from pydantic import BaseModel, Field, ValidationError
import json
from pathlib import Path

class Book:
    def __init__(self, title: str, author: str, isbn: str):
        self.title = title
        self.author = author
        self.isbn = isbn
        self.is_borrowed = False

    def borrow_book(self):
        if not self.is_borrowed:
            self.is_borrowed = True
            return True
        raise Exception(f"{self.title} zaten ödünç verildi.")

    def return_book(self):
        if self.is_borrowed:
            self.is_borrowed = False
            return True
        raise Exception(f"{self.title} ödünç verilmedi.")

    def display_info(self):
        return f"{self.title} by {self.author} (ISBN: {self.isbn})"
    
    def __str__(self):
        return self.display_info()

class EBook(Book):
    def __init__(self, title: str, author: str, isbn: str, file_format: str, file_size: float):
        super().__init__(title, author, isbn)
        self.file_format = file_format
        self.file_size = file_size

    def display_info(self):
        return f"{super().display_info()} - Format: {self.file_format} - Dosya Boyutu: {self.file_size}MB"

class AudioBook(Book):
    def __init__(self, title: str, author: str, isbn: str, duration_hours: float):
        super().__init__(title, author, isbn)
        self.duration_hours = duration_hours

    def display_info(self):
        return f"{super().display_info()} - Süre: {self.duration_hours} saat"


class Library:
    def __init__(self, name: str, json_file: str = "library.json"):
        self.name = name
        self._books = []
        self.json_file = json_file
        self.load_from_json()

    def _book_to_dict(self, book: Book):
        book_dict = {
            "title": book.title,
            "author": book.author,
            "isbn": book.isbn,
            "is_borrowed": book.is_borrowed,
            "type": "Book"
        }
        
        if isinstance(book, EBook):
            book_dict["type"] = "EBook"
            book_dict["file_format"] = book.file_format
            book_dict["file_size"] = book.file_size
        elif isinstance(book, AudioBook):
            book_dict["type"] = "AudioBook"
            book_dict["duration_hours"] = book.duration_hours
            
        return book_dict

    def _dict_to_book(self, book_dict: dict):
        book_type = book_dict.get("type", "Book")
        
        if book_type == "EBook":
            book = EBook(
                title=book_dict["title"],
                author=book_dict["author"],
                isbn=book_dict["isbn"],
                file_format=book_dict["file_format"],
                file_size=book_dict["file_size"]
            )
        elif book_type == "AudioBook":
            book = AudioBook(
                title=book_dict["title"],
                author=book_dict["author"],
                isbn=book_dict["isbn"],
                duration_hours=book_dict["duration_hours"]
            )
        else:
            book = Book(
                title=book_dict["title"],
                author=book_dict["author"],
                isbn=book_dict["isbn"]
            )
        
        book.is_borrowed = book_dict.get("is_borrowed", False)
        return book

    def save_to_json(self):
        try:
            books_data = [self._book_to_dict(book) for book in self._books]
            library_data = {
                "name": self.name,
                "books": books_data
            }
            
            with open(self.json_file, 'w', encoding='utf-8') as f:
                json.dump(library_data, f, indent=2, ensure_ascii=False)
            
            print(f"Kütüphane verileri {self.json_file} dosyasına kaydedildi.")
            return True
        except Exception as e:
            print(f"JSON dosyasına kaydederken hata oluştu: {e}")
            return False

    def load_from_json(self):
        try:
            if not Path(self.json_file).exists():
                print(f"JSON dosyası {self.json_file} bulunamadı. Boş kütüphane ile başlanıyor.")
                return False
            
            with open(self.json_file, 'r', encoding='utf-8') as f:
                library_data = json.load(f)
            
            self.name = library_data.get("name", self.name)
            books_data = library_data.get("books", [])
            
            self._books = [self._dict_to_book(book_dict) for book_dict in books_data]
            print(f"{self.total_books} kitap {self.json_file} dosyasından yüklendi.")
            return True
        except Exception as e:
            print(f"JSON dosyasından yüklerken hata oluştu: {e}")
            return False

    def add_book(self, book: Book):
        # ISBN ile kontrol
        existing_book = self.find_book_by_isbn(book.isbn)
        if existing_book:
            print(f"Kitap zaten mevcut: {existing_book.display_info()}")
            return False
        
        self._books.append(book)
        print(f"Kitap başarıyla eklendi: {book.display_info()}")
        self.save_to_json()  
        return True

    def remove_book(self, isbn: str):
        book = self.find_book_by_isbn(isbn)
        if book:
            self._books.remove(book)
            print(f"Kitap başarıyla silindi: {book.display_info()}")
            self.save_to_json()  
            return True
        else:
            print(f"ISBN {isbn} ile kitap bulunamadı.")
            return False

    def borrow_book(self, isbn: str):
        book = self.find_book_by_isbn(isbn)
        if book:
            try:
                book.borrow_book()
                print(f"Kitap ödünç verildi: {book.display_info()}")
                self.save_to_json()  
                return True
            except Exception as e:
                print(f"Hata: {e}")
                return False
        else:
            print(f"ISBN {isbn} ile kitap bulunamadı.")
            return False

    def return_book(self, isbn: str):
        """Return a book by ISBN and save changes."""
        book = self.find_book_by_isbn(isbn)
        if book:
            try:
                book.return_book()
                print(f"Kitap iade edildi: {book.display_info()}")
                self.save_to_json() 
                return True
            except Exception as e:
                print(f"Hata: {e}")
                return False
        else:
            print(f"ISBN {isbn} ile kitap bulunamadı.")
            return False

    def display_books(self):
        if not self._books:
            print("Kütüphanede hiç kitap yok.")
            return
        
        print(f"\n{self.name} - Toplam {self.total_books} kitap:")
        print("-" * 50)
        for i, book in enumerate(self._books, 1):
            status = " (Ödünç verildi)" if book.is_borrowed else ""
            print(f"{i}. {book.display_info()}{status}")
    
    def find_book_by_title(self, title: str):
        for book in self._books:
            if book.title.lower() == title.lower():
                return book
        return None
    
    def find_book_by_isbn(self, isbn: str):
        for book in self._books:
            if book.isbn == isbn:
                return book
        return None
    
    def find_book_by_author(self, author: str):
        for book in self._books:
            if book.author.lower() == author.lower():
                return book
        return None
    
    def find_book(self, title: str, author: str, isbn: str):
        if title.strip():
            book = self.find_book_by_title(title)
            if book:
                return book
        
        if author.strip():
            book = self.find_book_by_author(author)
            if book:
                return book
        
        if isbn.strip():
            book = self.find_book_by_isbn(isbn)
            if book:
                return book
        
        return None

    @property
    def total_books(self):
        return len(self._books)


@dataclass
class Member:
    name: str
    member_id: str
    email: str
    borrowed_books: List[Book] = field(default_factory=list)

class PydanticBook(BaseModel):
    title: str
    author: str
    isbn: str = Field(..., min_length=10, max_length=13)
    publication_year: int = Field(..., gt=1400, le=2030)

