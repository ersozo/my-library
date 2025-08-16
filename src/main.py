#!/usr/bin/env python3
from library import Book, Library, PydanticBook
from pydantic import ValidationError


def display_menu():
    print("\n" + "=" * 40)
    print("   KÜTÜPHANE YÖNETİM SİSTEMİ")
    print("=" * 40)
    print("1. Kitap Ekle")
    print("2. Kitap Sil")
    print("3. Kitapları Listele")
    print("4. Kitap Ara")
    print("5. Çıkış")
    print("=" * 40)


def get_user_choice():
    while True:
        try:
            choice = input("Seçiminizi yapın (1-5): ").strip()
            if choice in ['1', '2', '3', '4', '5']:
                return choice
            else:
                print("Geçersiz seçim! Lütfen 1-5 arası bir sayı girin.")
        except KeyboardInterrupt:
            print("\nProgram sonlandırılıyor...")
            return '5'


def add_book_menu(library):
    print("\n--- KİTAP EKLEME ---")
    
    try:
        title = input("Kitap başlığı: ").strip()
        author = input("Yazar adı: ").strip()
        isbn = input("ISBN numarası (10-13 karakter): ").strip()
        publication_year_input = input("Yayın yılı (1401-2030): ").strip()

        # yayın yılını Pydantic doğrulaması için int'e çeviriyoruz
        if publication_year_input:
            try:
                publication_year = int(publication_year_input)
            except ValueError:
                publication_year = 0  # Geçersiz değer - Pydantic kontrol edecek
        else:
            publication_year = 0  # Boş değer - Pydantic kontrol edecek

        # Doğrulama için Pydantic kullanıyoruz
        try:
            validated_book = PydanticBook(
                title=title,
                author=author,
                isbn=isbn,
                publication_year=publication_year
            )
            
            # Doğrulama başarılıysa kitabı ekle
            book = Book(validated_book.title, validated_book.author, validated_book.isbn)
            library.add_book(book)
            
            
        except ValidationError as e:
            print("\nKitap bilgileri geçersiz:")
            print("-" * 40)
            
            # Hata mesajlarını daha iyi görünüm için gruplandırıyoruz
            errors_by_field = {}
            for error in e.errors():
                field = error['loc'][0]
                message = error['msg']
                input_value = error.get('input', 'N/A')
                
                if field not in errors_by_field:
                    errors_by_field[field] = []
                errors_by_field[field].append((message, input_value))
            
            for field, field_errors in errors_by_field.items():
                field_name = {
                    'title': 'Kitap Başlığı',
                    'author': 'Yazar Adı', 
                    'isbn': 'ISBN Numarası',
                    'publication_year': 'Yayın Yılı'
                }.get(field, field)
                
                print(f"\n{field_name}:")
                for message, input_value in field_errors:
                    if field == 'isbn':
                        if 'at least' in message:
                            print(f"   • ISBN en az 10 karakter olmalıdır (girilen: '{input_value}')")
                        elif 'at most' in message:
                            print(f"   • ISBN en fazla 13 karakter olmalıdır (girilen: '{input_value}')")
                        elif 'required' in message.lower():
                            print(f"   • ISBN numarası zorunludur")
                        else:
                            print(f"   • {message} (girilen: '{input_value}')")
                    elif field == 'publication_year':
                        if 'greater than' in message:
                            print(f"   • Yayın yılı 1400'den büyük olmalıdır (girilen: {input_value})")
                        elif 'less than or equal' in message:
                            print(f"   • Yayın yılı 2030'dan küçük veya eşit olmalıdır (girilen: {input_value})")
                        elif 'required' in message.lower():
                            print(f"   • Yayın yılı zorunludur")
                        else:
                            print(f"   • {message} (girilen: {input_value})")
                    elif 'required' in message.lower() or 'missing' in message.lower():
                        print(f"   • {field_name} zorunludur")
                    else:
                        print(f"   • {message} (girilen: '{input_value}')")
            
            print("\nLütfen bilgileri kontrol edip tekrar deneyin.")
            return

    except KeyboardInterrupt:
        print("\nKitap ekleme işlemi iptal edildi.")
    except Exception as e:
        print(f"Beklenmeyen hata: {e}")


def remove_book_menu(library):
    print("\n--- KİTAP SİLME ---")
    try:
        if library.total_books == 0:
            print("Kütüphanede silinecek kitap yok.")
            return
            
        isbn = input("Silinecek kitabın ISBN numarası: ").strip()
        if not isbn:
            print("ISBN numarası boş olamaz!")
            return

        library.remove_book(isbn)

    except KeyboardInterrupt:
        print("\nKitap silme işlemi iptal edildi.")
    except Exception as e:
        print(f"Kitap silinirken hata oluştu: {e}")


def list_books_menu(library):
    print("\n--- KİTAP LİSTESİ ---")
    library.display_books()


def find_book_menu(library):
    print("\n--- KİTAP ARAMA ---")
    
    if library.total_books == 0:
        print("Kütüphanede aranacak kitap yok.")
        return

    print("Arama yapmak için en az bir alan doldurun:")
    
    try:
        title = input("Kitap başlığı (boş bırakabilirsiniz): ").strip()
        author = input("Yazar adı (boş bırakabilirsiniz): ").strip()
        isbn = input("ISBN numarası (boş bırakabilirsiniz): ").strip()
        
        if not title and not author and not isbn:
            print("En az bir arama kriteri girmelisiniz!")
            return

        search_title = title if title else ""
        search_author = author if author else ""
        search_isbn = isbn if isbn else ""

        book = library.find_book(search_title, search_author, search_isbn)
        if book:
            status = " (Ödünç verildi)" if book.is_borrowed else " (Mevcut)"
            print(f"\nKitap bulundu: {book.display_info()}{status}")
        else:
            print("Verilen kriterlere uygun kitap bulunamadı.")
            if title:
                print(f"  - Başlık: '{title}'")
            if author:
                print(f"  - Yazar: '{author}'")
            if isbn:
                print(f"  - ISBN: '{isbn}'")

    except KeyboardInterrupt:
        print("\nArama işlemi iptal edildi.")
    except Exception as e:
        print(f"Arama sırasında hata oluştu: {e}")


def main():
    print("Kütüphane Yönetim Sistemi başlatılıyor...")

    library = Library(name="Kütüphanem")

    while True:
        try:
            display_menu()
            choice = get_user_choice()

            if choice == '1':
                add_book_menu(library)
            elif choice == '2':
                remove_book_menu(library)
            elif choice == '3':
                list_books_menu(library)
            elif choice == '4':
                find_book_menu(library)
            elif choice == '5':
                print("\nKütüphane sistemi kapatılıyor...")
                book_count = library.total_books
                if book_count > 0:
                    print(f"Toplam {book_count} kitap kayıtlı.")
                else:
                    print("Kütüphanede kayıtlı kitap yok.")
                print("İyi günler!")
                break

        except KeyboardInterrupt:
            print("\n\nProgram sonlandırılıyor...")
            print("İyi günler!")
            break
        except Exception as e:
            print(f"Beklenmeyen bir hata oluştu: {e}")
            print("Program devam ediyor...")


if __name__ == "__main__":
    main()
