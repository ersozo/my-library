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


ebook = EBook("1984", "George Orwell", "1234567890", "PDF", 1.5)
audio_book = AudioBook("Hamlet", "William Shakespeare", "0987654321", 10.5)

my_library = Library(name="My Library 01")
my_library.add_book(ebook)
my_library.add_book(audio_book)

print(my_library.display_books())
print(my_library.find_book(title="1984").display_info())

print(my_library.total_books)
