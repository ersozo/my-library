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
        self._books.append(book)

    def remove_book(self, book: Book):
        self._books.remove(book)

    def display_books(self):
        return [book.display_info() for book in self._books]

    def find_book(self, title: str):
        for book in self._books:
            if book.title == title:
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
    title: str = Field(..., max_length=100)
    author: str = Field(..., max_length=100)
    isbn: str = Field(..., min_length=10, max_length=13)
    publication_year: int = Field(..., ge=1450, le=2025)

# deneme 1 (geçerli örnek)

try:
    book = PydanticBook(
        title="1984",
        author="George Orwell",
        isbn="1234567890",
        publication_year=1949
    )
    print(f"Valid book created:")
    print(book.model_dump_json(indent=4))
except ValidationError as e:
    print(e)


# deneme 2 (geçersiz örnek)

try:
    book = PydanticBook(
        title="SomeTitle",
        author="SomeAuthor",
        isbn="123",
        publication_year=2030
    )
    print(book)
except ValidationError as e:
    print(e)
