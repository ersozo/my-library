from dataclasses import dataclass, field
from typing import List
from pydantic import BaseModel, Field, ValidationError
import json
from pathlib import Path
import httpx
from message_display import UnicodeDisplay


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
    def __init__(self, title: str, author: str, isbn: str, duration_minutes: int):
        super().__init__(title, author, isbn)
        self.duration_minutes = duration_minutes

    def display_info(self):
        return f"{super().display_info()} - Süre: {self.duration_minutes} dakika"


class Library:
    def __init__(self, name: str, json_file: str = "library.json"):
        self.name = name
        self._books = []
        self.json_file = json_file       # verileri kaydetmek için JSON dosyası
        self.display = UnicodeDisplay()  # mesaj gösterme için
        self.load_from_json()

    # Kitap nesnesini dict formatına dönüştürür
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
            book_dict["duration_minutes"] = book.duration_minutes

        return book_dict

    # dict formatından kitap nesnesine dönüştürür
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
                duration_minutes=book_dict["duration_minutes"]
            )
        else:
            book = Book(
                title=book_dict["title"],
                author=book_dict["author"],
                isbn=book_dict["isbn"]
            )

        book.is_borrowed = book_dict.get("is_borrowed", False)
        return book

    # Kütüphane verilerini JSON dosyasına kaydeder
    def save_to_json(self):
        try:
            books_data = [self._book_to_dict(book) for book in self._books]
            library_data = {
                "name": self.name,
                "books": books_data
            }

            with open(self.json_file, 'w', encoding='utf-8') as f:
                json.dump(library_data, f, indent=2, ensure_ascii=False)

            self.display.success(f"Kütüphane verileri {self.json_file} dosyasına kaydedildi.")
            return True
        except Exception as e:
            self.display.error(f"JSON dosyasına kaydederken hata oluştu: {e}")
            return False

    # Kütüphane verilerini JSON dosyasından yükler
    def load_from_json(self):
        try:
            if not Path(self.json_file).exists():
                self.display.warning(f" JSON dosyası {self.json_file} bulunamadı. Boş kütüphane ile başlanıyor.")
                return False

            with open(self.json_file, 'r', encoding='utf-8') as f:
                library_data = json.load(f)

            self.name = library_data.get("name", self.name)
            books_data = library_data.get("books", [])

            self._books = [self._dict_to_book(book_dict) for book_dict in books_data]
            self.display.success(f"{self.total_books} kitap {self.json_file} dosyasından yüklendi.")
            return True
        except Exception as e:
            self.display.error(f"JSON dosyasından yüklerken hata oluştu: {e}")
            return False

    def add_book(self, book: Book):
        # ISBN ile kontrol
        existing_book = self.find_book_by_isbn(book.isbn)
        if existing_book:
            self.display.warning(f" Kitap zaten mevcut: {existing_book.display_info()}")
            return False

        self._books.append(book)
        self.display.success(f"Kitap başarıyla eklendi: {book.display_info()}")
        self.save_to_json()
        return True

    def remove_book(self, isbn: str):
        book = self.find_book_by_isbn(isbn)
        if book:
            self._books.remove(book)
            self.display.success(f"Kitap başarıyla silindi: {book.display_info()}")
            self.save_to_json()
            return True
        else:
            self.display.error(f"ISBN {isbn} ile kitap bulunamadı.")
            return False

    def borrow_book(self, isbn: str):
        book = self.find_book_by_isbn(isbn)
        if book:
            try:
                book.borrow_book()
                self.display.success(f"Kitap ödünç verildi: {book.display_info()}")
                self.save_to_json()
                return True
            except Exception as e:
                self.display.error(f"Hata: {e}")
                return False
        else:
            self.display.error(f"ISBN {isbn} ile kitap bulunamadı.")
            return False

    def return_book(self, isbn: str):
        book = self.find_book_by_isbn(isbn)
        if book:
            try:
                book.return_book()
                self.display.success(f"Kitap iade edildi: {book.display_info()}")
                self.save_to_json()
                return True
            except Exception as e:
                self.display.error(f"Hata: {e}")
                return False
        else:
            self.display.error(f"ISBN {isbn} ile kitap bulunamadı.")
            return False

    def display_books(self):
        if not self._books:
            self.display.info("Kütüphanede hiç kitap yok.")
            return

        self.display.success(f"{self.name} - Toplam {self.total_books} kitap:")
        print("-" * 50)
        for i, book in enumerate(self._books, 1):
            status = " (Ödünç verildi)" if book.is_borrowed else ""
            print(f"\t{i}. {book.display_info()}{status}")

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

    def find_book(self):
        print("\t1. Başlığa göre ara")
        print("\t2. Yazara göre ara")
        print("\t3. ISBN'e göre ara")

        choice = input("\nArama türünü seçin (1-3): ").strip()

        if choice == "1":
            title = input("\n\tKitap başlığını girin: ").strip()
            book = self.find_book_by_title(title)
        elif choice == "2":
            author = input("\n\tYazar adını girin: ").strip()
            book = self.find_book_by_author(author)
        elif choice == "3":
            isbn = input("\n\tISBN numarasını girin: ").strip()
            book = self.find_book_by_isbn(isbn)
        else:
            print("")
            self.display.error("Geçersiz seçim!")
            return
        print("")
        if book:
            self.display.success(f"Kitap bulundu:\n")
            print(f"\tBaşlık\t: {book.title}")
            print(f"\tYazar\t: {book.author}")
            print(f"\tISBN\t: {book.isbn}")
            print(f"\tDurum\t: {'Ödünç verildi' if book.is_borrowed else 'Mevcut'}")
        else:
            self.display.error("Kitap bulunamadı.")



    @property
    def total_books(self):
        return len(self._books)


    def fetch_book_from_api(self, isbn: str):
        try:
            url = f"https://openlibrary.org/isbn/{isbn}.json"

            with httpx.Client(timeout=10.0, follow_redirects=True) as client:
                response = client.get(url)

                if response.status_code == 404:
                    self.display.error(f"Kitap bulunamadı: ISBN {isbn} ile kitap bulunamadı.")
                    return None
                elif response.status_code != 200:
                    self.display.error(f"API hatası: HTTP {response.status_code}")
                    return None

                data = response.json()

                # Kitap bilgilerini al
                title = data.get("title", "Bilinmeyen Başlık")
                authors_data = data.get("authors", [])

                # Yazar adlarını al
                author_names = []
                for author_ref in authors_data:
                    try:
                        author_url = f"https://openlibrary.org{author_ref['key']}.json"
                        author_response = client.get(author_url, follow_redirects=True)
                        if author_response.status_code == 200:
                            author_data = author_response.json()
                            author_name = author_data.get("name", "Bilinmeyen Yazar")
                            author_names.append(author_name)
                    except Exception:
                        author_names.append("Bilinmeyen Yazar")

                # Eğer yazar bulunamazsa varsayılan değer kullan
                if not author_names:
                    author_names = ["Bilinmeyen Yazar"]

                # Birden fazla yazarı " & " ile birleştir
                author = " & ".join(author_names)

                return {
                    "title": title,
                    "author": author,
                    "isbn": isbn
                }

        except httpx.TimeoutException:
            self.display.error("API isteği zaman aşımına uğradı. İnternet bağlantınızı kontrol edin.")
            return None
        except httpx.RequestError as e:
            self.display.error(f"API isteği başarısız: {e}")
            return None
        except Exception as e:
            self.display.error(f"Beklenmeyen hata: {e}")
            return None


    def add_book_by_isbn(self, isbn: str):
        # Kitap zaten mevcut mu kontrolü
        existing_book = self.find_book_by_isbn(isbn)
        if existing_book:
            self.display.error(f"Kitap zaten mevcut: {existing_book.display_info()}")
            return False

        # API'den kitap bilgilerini al
        book_info = self.fetch_book_from_api(isbn)
        if not book_info:
            return False

        # Kitap nesnesi oluştur
        book = Book(book_info["title"], book_info["author"], isbn)

        # Kütüphaneye ekle
        self._books.append(book)
        self.display.success(f"Kitap başarıyla eklendi: {book.display_info()}")
        self.save_to_json()
        return True



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

