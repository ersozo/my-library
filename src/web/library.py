from dataclasses import dataclass, field
from typing import List
from pydantic import BaseModel, Field, ValidationError
import sqlite3
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
    def __init__(self, name: str, db_file: str = "library.db"):
        self.name = name
        self._books = []
        self.db_file = db_file           # verileri kaydetmek için SQLite dosyası
        self.display = UnicodeDisplay()  # mesaj gösterme için
        self.init_database()
        self.load_from_database()

    # SQLite veritabanını oluşturur
    def init_database(self):
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()

            # Kitaplar tablosunu oluştur
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS books (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    author TEXT NOT NULL,
                    isbn TEXT UNIQUE NOT NULL,
                    is_borrowed INTEGER DEFAULT 0,
                    book_type TEXT DEFAULT 'Book',
                    file_format TEXT,
                    file_size REAL,
                    duration_minutes INTEGER
                )
            ''')

            # Kütüphane bilgileri tablosunu oluştur
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS library_info (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL
                )
            ''')

            # Kütüphane adını kontrol et ve ekle
            cursor.execute('SELECT COUNT(*) FROM library_info')
            if cursor.fetchone()[0] == 0:
                cursor.execute('INSERT INTO library_info (name) VALUES (?)', (self.name,))

            conn.commit()
            conn.close()
            self.display.success(f"SQLite veritabanı başarıyla başlatıldı: {self.db_file}")
        except Exception as e:
            self.display.error(f"Veritabanı başlatılırken hata oluştu: {e}")

    # Veritabanından kitap nesnesine dönüştürür
    def _row_to_book(self, row):
        book_type = row[5]  # book_type column

        if book_type == "EBook":
            book = EBook(
                title=row[1],
                author=row[2],
                isbn=row[3],
                file_format=row[6] or "",
                file_size=row[7] or 0.0
            )
        elif book_type == "AudioBook":
            book = AudioBook(
                title=row[1],
                author=row[2],
                isbn=row[3],
                duration_minutes=row[8] or 0
            )
        else:
            book = Book(
                title=row[1],
                author=row[2],
                isbn=row[3]
            )

        book.is_borrowed = bool(row[4]) 
        return book

    # Kitabı veritabanına kaydeder
    def save_book_to_db(self, book: Book):
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()

            # Kitap türünü belirle
            book_type = "Book"
            file_format = None
            file_size = None
            duration_minutes = None

            if isinstance(book, EBook):
                book_type = "EBook"
                file_format = book.file_format
                file_size = book.file_size
            elif isinstance(book, AudioBook):
                book_type = "AudioBook"
                duration_minutes = book.duration_minutes

            cursor.execute('''
                INSERT INTO books (title, author, isbn, is_borrowed, book_type, file_format, file_size, duration_minutes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (book.title, book.author, book.isbn, int(book.is_borrowed), book_type, file_format, file_size, duration_minutes))

            conn.commit()
            conn.close()
            return True
        except Exception as e:
            self.display.error(f"Kitap veritabanına kaydedilirken hata oluştu: {e}")
            return False

    # Kitap durumunu veritabanında günceller
    def update_book_in_db(self, book: Book):
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()

            cursor.execute('''
                UPDATE books SET is_borrowed = ? WHERE isbn = ?
            ''', (int(book.is_borrowed), book.isbn))

            conn.commit()
            conn.close()
            return True
        except Exception as e:
            self.display.error(f"Kitap veritabanında güncellenirken hata oluştu: {e}")
            return False

    # Kitabı veritabanından siler
    def remove_book_from_db(self, isbn: str):
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()

            cursor.execute('DELETE FROM books WHERE isbn = ?', (isbn,))

            conn.commit()
            conn.close()
            return True
        except Exception as e:
            self.display.error(f"Kitap veritabanından silinirken hata oluştu: {e}")
            return False

    # Kütüphane verilerini veritabanından yükler
    def load_from_database(self):
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()

            # Kütüphane adını yükle
            cursor.execute('SELECT name FROM library_info LIMIT 1')
            result = cursor.fetchone()
            if result:
                self.name = result[0]

            # Kitapları yükle
            cursor.execute('SELECT * FROM books')
            rows = cursor.fetchall()

            self._books = [self._row_to_book(row) for row in rows]
            conn.close()

            self.display.success(f"{self.total_books} kitap veritabanından yüklendi.")
            return True
        except Exception as e:
            self.display.error(f"Veritabanından yüklerken hata oluştu: {e}")
            return False

    def add_book(self, book: Book):
        # ISBN ile kontrol
        existing_book = self.find_book_by_isbn(book.isbn)
        if existing_book:
            self.display.warning(f" Kitap zaten mevcut: {existing_book.display_info()}")
            return False

        # Veritabanına kaydet
        if self.save_book_to_db(book):
            self._books.append(book)
            self.display.success(f"Kitap başarıyla eklendi: {book.display_info()}")
            return True
        return False

    def remove_book(self, isbn: str):
        book = self.find_book_by_isbn(isbn)
        if book:
            # Veritabanından sil
            if self.remove_book_from_db(isbn):
                self._books.remove(book)
                self.display.success(f"Kitap başarıyla silindi: {book.display_info()}")
                return True
        else:
            self.display.error(f"ISBN {isbn} ile kitap bulunamadı.")
            return False

    def borrow_book(self, isbn: str):
        book = self.find_book_by_isbn(isbn)
        if book:
            try:
                book.borrow_book()
                # Veritabanında güncelle
                if self.update_book_in_db(book):
                    self.display.success(f"Kitap ödünç verildi: {book.display_info()}")
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
                # Veritabanında güncelle
                if self.update_book_in_db(book):
                    self.display.success(f"Kitap iade edildi: {book.display_info()}")
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
            with httpx.Client(timeout=15.0, follow_redirects=True) as client:
                response = client.get(url)
                # 404 hatasını kontrol et
                if response.status_code == 404:
                    self.display.warning(f" ISBN {isbn} OpenLibrary'de bulunamadı.")
                    return None
                # 200 hatasını kontrol et
                elif response.status_code != 200:
                    self.display.warning(f" API hatası: HTTP {response.status_code}")
                    return None
                # ISBN ile bulunan kitap bilgilerini al
                data = response.json()
                
                title = data.get("title")
                if not title:
                    self.display.warning(f" API hatası: Kitap başlığı bulunamadı")
                    return None

                authors_data = data.get("authors", [])
                if not authors_data:
                    self.display.warning(f" API hatası: Yazar bilgisi bulunamadı")
                    return None

                try:
                    author_ref = authors_data[0]
                    author_url = f"https://openlibrary.org{author_ref['key']}.json"
                    author_response = client.get(author_url, timeout=10.0)
                    
                    if author_response.status_code != 200:
                        self.display.warning(f" API hatası: Yazar bilgisi çekilemedi (HTTP {author_response.status_code})")
                        return None
                    
                    author_data = author_response.json()
                    author_name = author_data.get("name")
                    if not author_name:
                        self.display.warning(f" API hatası: Yazar adı bulunamadı")
                        return None
                    
                    author = author_name
                    
                except Exception as e:
                    self.display.warning(f" API hatası: Yazar bilgisi çekilirken hata: {e}")
                    return None

                self.display.success(f"Kitap bilgileri bulundu: {title} - {author}")
                return {
                    "title": title,
                    "author": author,
                    "isbn": isbn
                }

        except httpx.TimeoutException:
            self.display.warning(f" API zaman aşımı (15 saniye). İnternet bağlantısı yavaş olabilir.")
            return None
        except (httpx.RequestError, httpx.ConnectError) as e:
            self.display.warning(f" İnternet bağlantı sorunu: {e}")
            return None
        except Exception as e:
            self.display.warning(f" API hatası: {e}")
            return None

    def add_book_by_isbn(self, isbn: str):
        # Kitap zaten mevcut mu kontrolü
        existing_book = self.find_book_by_isbn(isbn)
        if existing_book:
            self.display.warning(f" Kitap zaten mevcut: {existing_book.display_info()}")
            return False

        # API'den kitap bilgilerini al
        book_info = self.fetch_book_from_api(isbn)
        if not book_info:
            self.display.warning(f" ISBN {isbn} OpenLibrary'de bulunamadı. Manual olarak ekleme yapın.")
            return False

        # Kitap nesnesi oluştur
        book = Book(book_info["title"], book_info["author"], isbn)

        # Veritabanına kaydet
        if self.save_book_to_db(book):
            self._books.append(book)
            self.display.success(f"Kitap başarıyla eklendi: {book.display_info()}")
            return True
        return False



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
