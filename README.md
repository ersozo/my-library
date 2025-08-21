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

## Kurulum

### 1. Projeyi Klonlayın

```bash
git clone https://github.com/ersozo/my-library.git
cd my-library
```

### 2. Bağımlılıkları Yükleyin ve Sanal Ortamı Aktive Edin

uv kullanarak (ÖNERİLEN)

```bash
uv sync

source .venv/bin/activate   # Linux / macOS
.venv\Scripts\activate      # Windows
```

veya pip kullanarak:

```bash
python -m venv .venv

source .venv/bin/activate   # Linux / macOS
.venv\Scripts\activate      # Windows

pip install -r requirements.txt
```

## Dosya Yapısı

```bash
my-library/
├── src/
│   ├── library.py              # Kütüphane sınıfları
│   ├── main.py                 # CLI uygulaması
│   ├── message_display.py      # Konsol sembolleri için
│   ├── api.py                  # FastAPI uygulaması
│   ├── test_api.py             # API için test dosyası
│   ├── test_library.py         # CLI uygulaması için test dosyası
│   └── web/                    # Web demo dosyaları
│       ├── api.py              # Web API sunucusu (FastAPI)
│       ├── library.py          # Web için kütüphane modülü (sqlite entegrasyonu)
│       ├── message_display.py  # Konsol sembolleri için
│       ├── web_manager.py      # Web uygulaması
│       └── frontend/           # Frontend dosyaları
│           ├── index.html      # Uygulama ana sayfası
│           └── app.js          # JavaScript uygulaması
├── requirements.txt            # Python bağımlılıkları
├── pyproject.toml              # Proje yapılandırması
├── uv.lock
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

1. Kitap Ekle (Manuel)
2. Kitap Ekle (ISBN ile)
3. Kitap Sil
4. Kitapları Listele
5. Kitap Ara
6. Kitap Ödünç Al
7. Kitap İade Et
8. Çıkış


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
    "title": "Building LLM Apps",
    "author": "Valentina Alto",
    "isbn": "9781835462317",
    ""publication_year": 2024
  }'
```
#### ISBN ile Otomatik Kitap Ekleme
```bash
curl -X POST "http://localhost:8000/books/isbn" \
  -H "Content-Type: application/json" \
  -d '{"isbn": "9781492034865"}'
```
> **Not:** Bu endpoint kitap bilgilerini OpenLibrary API'den otomatik olarak alır.

### Kitap Arama
```bash
# Başlığa göre ara
curl "http://localhost:8000/books/search?title=Building%20LLM%20Apps"

# Yazara göre ara
curl "http://localhost:8000/books/search?author=Valentina%20Alto"

# ISBN'e göre ara
curl "http://localhost:8000/books/search?isbn=9781835462317"
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

### 3. Web Demo Uygulaması

Demo uygulaması lokalde çalışır. Konsol uygulamasından farklı olarak sadece tek bir kitap cinsi ekler.<br>
Veriler SQLite ile tutulur. Uygulamayı çalıştırmak için iki komut satırı penceresi (terminal) gereklidir:

#### Terminal 1: FastAPI Sunucusu
```bash
cd src/web
uv run python -m uvicorn api:app --reload
```

#### Terminal 2: HTTP Sunucusu (Frontend)
```bash
cd src/web/frontend
python -m http.server 3000
```

Web uygulamasına erişim: `http://localhost:3000`

> **Not:** Web demo uygulaması, FastAPI backend'i ile iletişim kurar. Backend sunucusunun çalışır durumda olması gereklidir.

#### Geliştirmeye açık noktalar
- Diğer kitap çeşitlerini ekleme.
- Arama bölümü için filtre.
- Farklı listeleme seçenekleri.
- İşlemlerin izlenebilirliği için çözümler (timestamp vb.)
