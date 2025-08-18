# Kütüphane Yönetim Sistemi

Basit bir kütüphane yönetim sistemidir. Kitap ekleme, listeleme, arama, ödünç alma ve iade etme işlemlerini destekler.<br> Komut satırı uygulaması
ve API şeklinde yararlanılabilir. Ayrıca demo olarak basit bir web uygulaması eklenmiştir.

## Özellikler

- Kitap ekleme, silme ve listeleme
- Kitap arama (başlık, yazar, ISBN ile)
- Kitap ödünç alma ve iade etme
- CLI (Komut satırı) arayüzü
- REST API arayüzü
- Pydantic ile veri doğrulama

## Gereksinimler

- Python 3.8+
- FastAPI
- Uvicorn
- Pydantic

## Kurulum

### 1. Projeyi Klonlayın

```bash
git clone <repository-url>
cd my-library
```

### 2. Bağımlılıkları Yükleyin

uv kullanarak:

```bash
uv sync
```

veya pip kullanarak:

```bash
pip install -r requirements.txt
```

## Dosya Yapısı

```
my-library/
├── src/
│   ├── library.py          # Ana kütüphane sınıfları
│   ├── main.py             # CLI uygulaması
│   ├── api.py              # FastAPI uygulaması
│   ├── test_api.py         # API için test dosyası
|   ├── test_library.py     # CLI uygulaması için test dosyası
├── requirements.txt        # Python bağımlılıkları
└── README.md
```

## Kullanım

### 1. CLI Uygulaması (library.py + main.py)

Komut satırından çalıştırın:

```bash
# uv ile
uv run python src/main.py

# veya doğrudan python ile
python src/main.py
```

Menü seçenekleri:
- 1: Kitap ekle
- 2: Kitapları listele
- 3: Kitap ara
- 4: Kitap sil
- 5: Kitap ödünç al
- 6: Kitap iade et
- 7: İstatistikleri göster
- 0: Çıkış


### 2. REST API (api.py)

API sunucusunu başlatın:

```bash
# uv ile
cd src
uv run python -m uvicorn api:app --reload

# veya doğrudan python ile
cd src
python -m uvicorn api:app --reload
```

API'ye erişim: `http://localhost:8000`
Dokümantasyon: `http://localhost:8000/docs`

## API Endpoints

- **GET /** - API durumunu kontrol et
- **POST /books** - Body: `{"title": "...", "author": "...", "isbn": "...", "publication_year": 2024}`
- **POST /books/isbn** - Body: `{"isbn": "9781234567890"}` (ISBN ile otomatik kitap ekleme)
- **GET /books** - Tüm kitapları listele
- **GET /books/search** - Query: `?title=...` veya `?author=...` veya `?isbn=...`
- **DELETE /books/{isbn}** - Kitap sil
- **PATCH /books/{isbn}/borrow** - Kitap ödünç al
- **PATCH /books/{isbn}/return** - Kitap iade et
- **GET /stats** - Kütüphane istatistikleri

## API Kullanım Örnekleri

### Kitap Ekleme

#### Manuel Kitap Ekleme
```bash
curl -X POST "http://localhost:8000/books" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Suç ve Ceza",
    "author": "Dostoyevski",
    "isbn": "1234567890",
    "publication_year": 1866
  }'
```

#### ISBN ile Otomatik Kitap Ekleme
```bash
curl -X POST "http://localhost:8000/books/isbn" \
  -H "Content-Type: application/json" \
  -d '{"isbn": "9781492034865"}'
```
> **Not:** Bu endpoint kitap bilgilerini OpenLibrary API'den otomatik olarak alır. API erişim sorunu olduğunda placeholder bilgiler kullanır.

### Kitap Arama
```bash
# Başlığa göre ara
curl "http://localhost:8000/books/search?title=Suç"

# Yazara göre ara
curl "http://localhost:8000/books/search?author=Dostoyevski"

# ISBN'e göre ara
curl "http://localhost:8000/books/search?isbn=1234567890"
```

### Kitap Ödünç Alma
```bash
curl -X PATCH "http://localhost:8000/books/1234567890/borrow"
```

### İstatistikler
```bash
curl "http://localhost:8000/stats"
```

## Test

#### CLI Testi

CLI uygulamasını test etmek için:

```bash
# uv ile
uv run python src/test_library.py

# veya doğrudan python ile
python src/test_library.py
```

#### API Testi

```bash
# uv ile
uv run python -m pytest src/test_api.py -v

# veya doğrudan python ile
python -m pytest src/test_api.py -v
```

