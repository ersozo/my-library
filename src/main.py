from library import Book, Library, PydanticBook, EBook, AudioBook
from pydantic import ValidationError
from message_display import UnicodeDisplay


display = UnicodeDisplay()


def display_menu():
    print("\n" + "=" * 40)
    print("   KÜTÜPHANE YÖNETİM SİSTEMİ")
    print("=" * 40)
    print("1. Kitap Ekle (Manuel)")
    print("2. Kitap Ekle (ISBN ile)")
    print("3. Kitap Sil")
    print("4. Kitapları Listele")
    print("5. Kitap Ara")
    print("6. Kitap Ödünç Al")
    print("7. Kitap İade Et")
    print("8. Çıkış")
    print("=" * 40)


def get_user_choice():
    while True:
        try:
            choice = input("Seçiminizi yapın (1-8): ").strip()
            if choice in ['1', '2', '3', '4', '5', '6', '7', '8']:
                return choice
            else:
                display.warning("Geçersiz seçim! Lütfen 1-8 arası bir sayı girin.")
        except KeyboardInterrupt:
            print("")
            display.warning("Program sonlandırılıyor...")
            return '8'


def add_book_menu(library):
    print("\n--- KİTAP EKLEME (MANUEL) ---\n")
    
    # Kitap türü seçimi
    display.book("Kitap türünü seçin:\n")
    print("\t1. Normal Kitap")
    print("\t2. E-Kitap")
    print("\t3. Sesli Kitap")
    
    try:
        book_type = input("\nSeçiminizi yapın (1-3): ").strip()
        
        if book_type not in ['1', '2', '3']:
            display.warning("Geçersiz seçim! Lütfen 1-3 arası bir sayı girin.")
            return

        # Ortak bilgiler
        title = input("\tKitap başlığı\t\t\t: ").strip()
        author = input("\tYazar adı\t\t\t: ").strip()
        isbn = input("\tISBN numarası (10-13 karakter)\t: ").strip()
        publication_year_input = input("\tYayın yılı (1401-2030)\t\t: ").strip()

        # yayın yılını Pydantic doğrulaması için int'e çeviriyoruz
        if publication_year_input:
            try:
                publication_year = int(publication_year_input)
            except ValueError:
                publication_year = 0  # Geçersiz değeri Pydantic ile kontrol edeceğiz
        else:
            publication_year = 0  # Boş değeri Pydantic ile kontrol edeceğiz

        # Doğrulama için Pydantic kullanıyoruz
        try:
            validated_book = PydanticBook(
                title=title,
                author=author,
                isbn=isbn,
                publication_year=publication_year
            )
            
            # Kitap türüne göre ek bilgiler al ve kitabı oluştur
            if book_type == '1':
                # Normal Kitap
                book = Book(validated_book.title, validated_book.author, validated_book.isbn)
            elif book_type == '2':
                # E-Kitap
                file_format = input("Dosya formatı (PDF, EPUB, vb.): ").strip()
                file_size_input = input("Dosya boyutu (MB): ").strip()
                try:
                    file_size = float(file_size_input)
                except ValueError:
                    display.error("Geçersiz dosya boyutu! Sayısal değer girin.")
                    return
                book = EBook(validated_book.title, validated_book.author, validated_book.isbn, file_format, file_size)
            elif book_type == '3':
                # Sesli Kitap
                duration_input = input("Süre (dakika): ").strip()
                try:
                    duration_minutes = int(duration_input)
                except ValueError:
                    display.error("Geçersiz süre! Sayısal değer girin.")
                    return
                book = AudioBook(validated_book.title, validated_book.author, validated_book.isbn, duration_minutes)
            
            library.add_book(book)
            
        except ValidationError as e:
            print("")
            display.error("Kitap bilgileri geçersiz:")
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
                            display.warning(f"ISBN en az 10 karakter olmalıdır (girilen: '{input_value}')")
                        elif 'at most' in message:
                            display.warning(f"ISBN en fazla 13 karakter olmalıdır (girilen: '{input_value}')")
                        elif 'required' in message.lower():
                            display.warning(f"ISBN numarası zorunludur")
                        else:
                            display.warning(f"{message} (girilen: '{input_value}')")
                    elif field == 'publication_year':
                        if 'greater than' in message:
                            display.warning(f"Yayın yılı 1400'den büyük olmalıdır (girilen: {input_value})")
                        elif 'less than or equal' in message:
                            display.warning(f"Yayın yılı 2030'dan küçük veya eşit olmalıdır (girilen: {input_value})")
                        elif 'required' in message.lower():
                            display.warning(f"Yayın yılı zorunludur")
                        else:
                            display.warning(f"{message} (girilen: {input_value})")
                    elif 'required' in message.lower() or 'missing' in message.lower():
                        display.warning(f"{field_name} zorunludur")
                    else:
                        display.warning(f"{message} (girilen: '{input_value}')")
            
            print("\n" + "-" * 40)
            display.info("Lütfen bilgileri kontrol edip tekrar deneyin.")
            return

    except KeyboardInterrupt:
        print("")
        display.warning("Kitap ekleme işlemi iptal edildi.")
    except Exception as e:
        display.error(f"Beklenmeyen hata: {e}")


def add_book_by_isbn_menu(library):
    print("\n--- KİTAP EKLEME (ISBN İLE) ---")
    
    try:
        display.info("Open Library API kullanarak kitap bilgileri otomatik olarak çekilecektir.")
        display.warning("İnternet bağlantısı gereklidir.")
        
        isbn = input("\n\tKitap ISBN numarasını girin: ").strip()
        if not isbn:
            display.warning("ISBN numarası boş olamaz!")
            return

        display.info(f"ISBN {isbn} ile kitap aranıyor...")
        display.info("Open Library API'den bilgiler çekiliyor...")
        
        success = library.add_book_by_isbn(isbn)
        
        if success:
            display.success("Kitap başarıyla eklendi!")
        else:
            display.error("Kitap eklenemedi. Lütfen ISBN'i ve internet bağlantınızı kontrol edin!")

    except KeyboardInterrupt:
        print("")
        display.warning("Kitap ekleme işlemi iptal edildi.")
    except Exception as e:
        display.error(f"Kitap eklenirken hata oluştu: {e}")


def remove_book_menu(library):
    print("\n--- KİTAP SİLME ---")
    try:
        if library.total_books == 0:
            display.info("Kütüphanede silinecek kitap yok.")
            return
            
        isbn = input("Silinecek kitabın ISBN numarası: ").strip()
        if not isbn:
            display.warning("ISBN numarası boş olamaz!")
            return

        library.remove_book(isbn)

    except KeyboardInterrupt:
        print("")
        display.warning("Kitap silme işlemi iptal edildi.")
    except Exception as e:
        display.error(f"Kitap silinirken hata oluştu: {e}")


def list_books_menu(library):
    print("\n--- KİTAP LİSTESİ ---")
    library.display_books()


def find_book_menu(library, display):
    print("\n--- KİTAP ARAMA ---\n")
    
    if library.total_books == 0:
        display.info("Kütüphanede aranacak kitap yok.")
        return
    try:
        library.find_book()
    except KeyboardInterrupt:
        print("")
        display.warning("Arama işlemi iptal edildi.")
    except Exception as e:
        display.error(f"Arama sırasında hata oluştu: {e}")


def borrow_book_menu(library):
    print("\n--- KİTAP ÖDÜNÇ ALMA ---")
    
    if library.total_books == 0:
        display.warning("Kütüphanede ödünç alınacak kitap yok.")
        return
    
    try:
        # Önce mevcut kitapları gösteriyoruz
        display.info("Mevcut kitaplar:")
        library.display_books()
        
        isbn = input("\nÖdünç almak istediğiniz kitabın ISBN numarası: ").strip()
        if not isbn:
            display.warning("ISBN numarası boş olamaz!")
            return

        library.borrow_book(isbn)

    except KeyboardInterrupt:
        print("")
        display.warning("Kitap ödünç alma işlemi iptal edildi.")
    except Exception as e:
        display.error(f"Kitap ödünç alınırken hata oluştu: {e}")


def return_book_menu(library):
    print("\n--- KİTAP İADE ETME ---")
    
    if library.total_books == 0:
        display.info("Kütüphanede iade edilecek kitap yok.")
        return

    try:
        # Önce mevcut kitapları gösteriyoruz
        display.info("Mevcut kitaplar:")
        library.display_books()
        
        isbn = input("\nİade etmek istediğiniz kitabın ISBN numarası: ").strip()
        if not isbn:
            display.warning("ISBN numarası boş olamaz!")
            return

        library.return_book(isbn)

    except KeyboardInterrupt:
        print("")
        display.warning("Kitap iade işlemi iptal edildi.")
    except Exception as e:
        display.error(f"Kitap iade edilirken hata oluştu: {e}")


def main():

    display = UnicodeDisplay()
    display.info("Kütüphane Yönetim Sistemi başlatılıyor...")
    library = Library(name="Kütüphanem")

    while True:
        try:
            display_menu()
            choice = get_user_choice()

            if choice == '1':
                add_book_menu(library)
            elif choice == '2':
                add_book_by_isbn_menu(library)
            elif choice == '3':
                remove_book_menu(library)
            elif choice == '4':
                list_books_menu(library)
            elif choice == '5':
                find_book_menu(library, display)
            elif choice == '6':
                borrow_book_menu(library)
            elif choice == '7':
                return_book_menu(library)
            elif choice == '8':
                print("")
                display.info("Kütüphane sistemi kapatılıyor...")
                book_count = library.total_books
                if book_count > 0:
                    display.info(f"Toplam {book_count} kitap kayıtlı.")
                else:
                    display.info("Kütüphanede kayıtlı kitap yok.")
                display.info("İyi günler!\n")
                break

        except KeyboardInterrupt:
            print("")
            display.warning("Program sonlandırılıyor...")
            display.info("İyi günler!\n")
            break
        except Exception as e:
            display.error(f"Beklenmeyen bir hata oluştu: {e}")
            display.info("Program devam ediyor...")


if __name__ == "__main__":
    main()
