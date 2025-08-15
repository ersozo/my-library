from dataclasses import dataclass, field
from typing import List
from pydantic import BaseModel, Field, ValidationError

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
        raise Exception(f"{self.title} is already borrowed.")

    def return_book(self):
        if self.is_borrowed:
            self.is_borrowed = False
            return True
        raise Exception(f"{self.title} was not borrowed.")

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
        return f"{super().display_info()} - Format: {self.file_format} - Size: {self.file_size}MB"

class AudioBook(Book):
    def __init__(self, title: str, author: str, isbn: str, duration_hours: float):
        super().__init__(title, author, isbn)
        self.duration_hours = duration_hours

    def display_info(self):
        return f"{super().display_info()} - Duration: {self.duration_hours} hours"


class Library:
    def __init__(self, name: str):
        self.name = name
        self._books = []

    def add_book(self, book: Book):
        # ISBN ile kontrol
        existing_book = self.find_book_by_isbn(book.isbn)
        if existing_book:
            print(f"Kitap zaten mevcut: {existing_book.display_info()}")
            return False
        
        self._books.append(book)
        print(f"Kitap başarıyla eklendi: {book.display_info()}")
        return True

    def remove_book(self, isbn: str):
        book = self.find_book_by_isbn(isbn)
        if book:
            self._books.remove(book)
            print(f"Kitap başarıyla silindi: {book.display_info()}")
            return True
        else:
            print(f"ISBN {isbn} ile kitap bulunamadı.")
            return False

    def display_books(self):
        if not self._books:
            print("Kütüphanede hiç kitap yok.")
            return
        
        print(f"\n{self.name} - Toplam {len(self._books)} kitap:")
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
        # Try to find by title first (if provided)
        if title.strip():
            book = self.find_book_by_title(title)
            if book:
                return book
        
        # Try to find by author (if provided)
        if author.strip():
            book = self.find_book_by_author(author)
            if book:
                return book
        
        # Try to find by ISBN (if provided)
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

