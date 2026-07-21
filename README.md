# URL Shortener API

A production-ready URL shortener API built with **FastAPI** and **PostgreSQL**.  
It supports user authentication, URL shortening, QR code generation, public redirects, click tracking, analytics, Redis caching, database migrations, automated tests, and Docker Compose deployment.

## Live Demo

- **API Base URL:** http://go.weetis.com:8000
- **Swagger Docs:** http://go.weetis.com:8000/docs
- **Alternative:** http://www.go.weetis.com:8000

---

## Features

- **User Authentication**
  - Register and login
  - JWT access tokens
  - Refresh token rotation
  - Logout with refresh token revocation
  - Password hashing with bcrypt

- **Link Management**
  - Create short links
  - List user-owned links
  - Get link details
  - Update original URLs
  - Delete links

- **Security & Ownership**
  - Users can only manage their own links
  - Protected endpoints require a Bearer token
  - Analytics data is only visible to the link owner

- **Public Redirection**
  - Public redirect endpoint for short URLs
  - Click count is increased on each redirect
  - Click metadata is stored for analytics

- **Analytics**
  - Overview dashboard data
  - Total links
  - Total clicks
  - Top-performing links
  - Recent clicks for a specific link
  - User agent, referrer, language and IP hash tracking

- **QR Code Generation**
  - Generate a PNG QR code for a shortened URL

- **Redis Caching**
  - In-memory caching for frequently accessed links
  - Redis-backed authentication token blacklisting
  - Separate Redis instance for tests

- **Database & Deployment**
  - PostgreSQL database
  - SQLAlchemy ORM
  - Alembic migrations
  - Docker & Docker Compose (development and production)
  - Nginx reverse proxy
  - GitHub Actions CI/CD pipeline

- **Testing**
  - Pytest test suite
  - Authentication tests
  - Link CRUD tests
  - Redirect tests
  - QR code tests
  - Analytics tests
  - Cache tests
  - Security header tests

---

## Tech Stack

| Area             | Technology                        |
| ---------------- | --------------------------------- |
| Backend          | FastAPI                           |
| Database         | PostgreSQL                        |
| ORM              | SQLAlchemy                        |
| Migrations       | Alembic                           |
| Validation       | Pydantic                          |
| Authentication   | JWT, python-jose, passlib, bcrypt |
| Caching          | Redis                             |
| QR Code          | qrcode, Pillow                    |
| Testing          | Pytest, FastAPI TestClient        |
| CI/CD            | GitHub Actions                    |
| Containerization | Docker, Docker Compose            |
| Reverse Proxy    | Nginx                             |

---

## API Endpoints

All protected endpoints require this header:

```http
Authorization: Bearer <access_token>
```

### Users & Authentication

| Method | Endpoint         | Description                                 | Auth Required |
| ------ | ---------------- | ------------------------------------------- | ------------- |
| `POST` | `/users/`        | Register a new user                         | No            |
| `POST` | `/users/login`   | Login and receive access/refresh tokens     | No            |
| `POST` | `/users/refresh` | Rotate refresh token and receive new tokens | No            |
| `POST` | `/users/logout`  | Revoke refresh token                        | Yes           |

### Links

| Method   | Endpoint          | Description                 | Auth Required |
| -------- | ----------------- | --------------------------- | ------------- |
| `POST`   | `/links/`         | Create a short link         | Yes           |
| `GET`    | `/links/`         | List current user's links   | Yes           |
| `GET`    | `/links/{code}`    | Get a specific link         | Yes           |
| `PUT`    | `/links/{code}`    | Update a link               | Yes           |
| `DELETE` | `/links/{code}`    | Delete a link               | Yes           |
| `GET`    | `/links/{code}/qr` | Generate QR code for a link | Yes           |

### Redirection

| Method | Endpoint   | Description                            | Auth Required |
| ------ | ---------- | -------------------------------------- | ------------- |
| `GET`  | `/r/{code}` | Redirect to original URL and log click | No            |

### Analytics

| Method | Endpoint                        | Description                         | Auth Required |
| ------ | ------------------------------- | ----------------------------------- | ------------- |
| `GET`  | `/analytics/overview`           | Get user's analytics overview       | Yes           |
| `GET`  | `/analytics/links/{code}`        | Get analytics for a specific link   | Yes           |
| `GET`  | `/analytics/links/{code}/clicks` | Get paginated click logs for a link | Yes           |

---

## Example Requests

### Register

```http
POST /users/
Content-Type: application/json
```

```json
{
  "email": "test@example.com",
  "password": "StrongPass123*"
}
```

### Login

```http
POST /users/login
Content-Type: application/json
```

```json
{
  "email": "test@example.com",
  "password": "StrongPass123*"
}
```

Example response:

```json
{
  "access_token": "<access_token>",
  "refresh_token": "<refresh_token>",
  "token_type": "bearer"
}
```

### Create Short Link

```http
POST /links/
Authorization: Bearer <access_token>
Content-Type: application/json
```

```json
{
  "original_url": "https://github.com/"
}
```

Example response:

```json
{
  "code": "abc123",
  "original_url": "https://github.com/",
  "click": 0,
  "short_url": "http://go.weetis.com:8000/r/abc123"
}
```

### Redirect

```http
GET /r/abc123
```

This redirects the user to the original URL and creates a click log.

### Link Analytics

```http
GET /analytics/links/abc123
Authorization: Bearer <access_token>
```

Example response:

```json
{
  "code": "abc123",
  "original_url": "https://github.com/",
  "total_clicks": 5,
  "recent_clicks": [
    {
      "clicked_at": "2026-07-03T12:00:00",
      "ip_hash": "hashed-ip-value",
      "user_agent": "Mozilla/5.0 ...",
      "referer": null,
      "accept_language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7"
    }
  ],
  "short_url": "http://go.weetis.com:8000/r/abc123"
}
```

### Analytics Overview

```http
GET /analytics/overview
Authorization: Bearer <access_token>
```

Example response:

```json
{
  "links": [
    {
      "code": "abc123",
      "original_url": "https://github.com/",
      "click": 5,
      "short_url": "http://go.weetis.com:8000/r/abc123"
    }
  ],
  "total_links": 1,
  "top_links": [
    {
      "code": "abc123",
      "original_url": "https://github.com/",
      "click": 5,
      "short_url": "http://go.weetis.com:8000/r/abc123"
    }
  ],
  "total_clicks": 5
}
```

---

## Local Development Setup

### 1. Prerequisites

- Python 3.12+
- PostgreSQL
- Redis
- Git

### 2. Clone the Repository

```bash
git clone https://github.com/yusuf-levent/url_shortener.git
cd url_shortener
```

### 3. Create and Activate Virtual Environment

```bash
python -m venv venv
```

Windows:

```bash
venv\Scripts\activate
```

macOS / Linux:

```bash
source venv/bin/activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure Environment Variables

Create a `.env` file in the project root:

```env
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/url_shortener
TEST_DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/url_shortener_test

SECRET_KEY=a-very-long-and-secure-random-string
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

BASE_URL=http://localhost:8000

REDIS_HOST=localhost
REDIS_PORT=6379

TZ=UTC
```

### 6. Create PostgreSQL Databases

```sql
CREATE DATABASE url_shortener;
CREATE DATABASE url_shortener_test;
```

### 7. Run Migrations

```bash
alembic upgrade head
```

### 8. Start the Application

```bash
uvicorn main:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

Swagger documentation:

```text
http://127.0.0.1:8000/docs
```

---

## Testing

Run the test suite:

```bash
pytest
```

The tests use `TEST_DATABASE_URL`. Make sure the test database exists before running tests.

---

## Docker Compose Usage

The project includes two Docker Compose configurations:

### Development (`compose.yaml`)

Starts PostgreSQL, Redis, the application, and a test Redis instance.

```bash
docker compose up -d
```

The API will be available at:

```text
http://localhost:8082
```

To run tests inside the container:

```bash
docker compose run --rm test
```

### Production (`compose.prod.yml`)

Starts PostgreSQL, Redis, and the application without exposed development ports or test services.

```bash
docker compose -f compose.prod.yml up -d
```

> **Note:** The production setup uses a `.env.prod` file for environment variables. Make sure to create it with the appropriate values before running.

---

## Nginx Reverse Proxy

The project includes an `nginx.conf` for use as a reverse proxy in front of the application. Configure your Nginx server to proxy requests to the running container (default port `8000`).

---

## Project Structure

```text
url_shortener/
├── alembic/                 # Database migrations
├── migrations/              # Alembic migration files
│   ├── env.py
│   ├── script.py.mako
│   └── versions/            # Migration version files
├── routers/                 # API routers
│   ├── admin.py             # Admin endpoints
│   ├── analytics.py         # Analytics endpoints
│   ├── links.py             # Link CRUD and QR endpoints
│   ├── redirect.py          # Public redirect endpoint
│   └── users.py             # User authentication endpoints
├── services/                # Business logic layer
│   ├── admin_service.py     # Admin operations
│   ├── analytics_service.py # Analytics logic
│   ├── auth_redis_service.py# Redis-backed auth token management
│   ├── auth_service.py      # Authentication logic
│   ├── cache_service.py     # Redis caching logic
│   ├── link_query_service.py# Link query operations
│   ├── link_service.py      # Link CRUD logic
│   ├── logging_service.py   # Logging utilities
│   ├── redis_service.py     # Redis connection management
│   └── redirect_service.py  # Redirect logic
├── tests/                   # Pytest test suite
│   ├── conftest.py          # Test fixtures and configuration
│   ├── test_admin.py
│   ├── test_analytics.py
│   ├── test_auth_login.py
│   ├── test_auth_logout.py
│   ├── test_auth_refresh.py
│   ├── test_auth_register.py
│   ├── test_cache.py
│   ├── test_links.py
│   ├── test_redirect.py
│   ├── test_security.py
│   └── test_units.py
├── auth.py                  # JWT and authentication helpers
├── config.py                # App settings (includes Redis, TZ)
├── constants.py             # Application constants
├── database.py              # Database connection and session
├── Dockerfile               # Docker image definition
├── main.py                  # FastAPI app entrypoint
├── models.py                # SQLAlchemy models
├── schemas.py               # Pydantic schemas
├── requirements.txt         # Python dependencies
├── compose.yaml             # Docker Compose (development)
├── compose.prod.yml         # Docker Compose (production)
├── nginx.conf               # Nginx reverse proxy configuration
├── .dockerignore            # Docker ignore file
├── pytest.ini               # Pytest configuration
└── alembic.ini              # Alembic configuration
```

---

## Possible Future Improvements

- Add custom aliases for short links
- Add link expiration dates
- Add date-range filtering for analytics
- Add browser/device parsing for user agents
- Add rate limiting
- Add background cleanup for expired refresh tokens
- Add a simple frontend dashboard

---

## Türkçe Açıklama

# URL Shortener API

Bu proje **FastAPI** ve **PostgreSQL** ile geliştirilmiş, üretime yakın seviyede bir URL kısaltma API projesidir.  
Kullanıcı kimlik doğrulama, link kısaltma, QR code oluşturma, public redirect, tıklama takibi, analytics, Redis önbellekleme, database migration, testler ve Docker Compose dağıtımını içerir.

## Canlı Demo

- **API Base URL:** http://go.weetis.com:8000
- **Swagger Docs:** http://go.weetis.com:8000/docs
- **Alternatif:** http://www.go.weetis.com:8000

---

## Özellikler

- **Kullanıcı Sistemi**
  - Register ve login
  - JWT access token
  - Refresh token rotation
  - Logout ile refresh token iptali
  - bcrypt ile şifre hashleme

- **Link Yönetimi**
  - Kısa link oluşturma
  - Kullanıcının kendi linklerini listeleme
  - Tek link detayını görüntüleme
  - Link güncelleme
  - Link silme

- **Güvenlik ve Sahiplik Kontrolü**
  - Kullanıcı sadece kendi linklerini yönetebilir
  - Korumalı endpointler Bearer token ister
  - Analytics verileri sadece link sahibine gösterilir

- **Public Redirect**
  - Kısa linkler public olarak çalışır
  - Her redirect işleminde tıklama sayısı artar
  - Analytics için tıklama bilgileri kaydedilir

- **Analytics**
  - Genel dashboard verisi
  - Toplam link sayısı
  - Toplam tıklama sayısı
  - En çok tıklanan linkler
  - Tek link için son tıklamalar
  - User agent, referer, dil bilgisi ve IP hash takibi

- **QR Code**
  - Kısa link için PNG formatında QR code üretme

- **Redis Önbellekleme**
  - Sık erişilen linkler için bellek içi önbellekleme
  - Redis tabanlı kimlik doğrulama token karaliste desteği
  - Testler için ayrı Redis örneği

- **Database ve Deployment**
  - PostgreSQL
  - SQLAlchemy ORM
  - Alembic migration
  - Docker & Docker Compose (geliştirme ve üretim)
  - Nginx reverse proxy
  - GitHub Actions CI/CD

- **Testler**
  - Pytest test yapısı
  - Auth testleri
  - Link CRUD testleri
  - Redirect testleri
  - QR code testleri
  - Analytics testleri
  - Cache testleri
  - Güvenlik başlık testleri

---

## Kullanılan Teknolojiler

| Alan           | Teknoloji                         |
| -------------- | --------------------------------- |
| Backend        | FastAPI                           |
| Database       | PostgreSQL                        |
| ORM            | SQLAlchemy                        |
| Migration      | Alembic                           |
| Validation     | Pydantic                          |
| Authentication | JWT, python-jose, passlib, bcrypt |
| Önbellekleme   | Redis                             |
| QR Code        | qrcode, Pillow                    |
| Test           | Pytest, FastAPI TestClient        |
| CI/CD          | GitHub Actions                    |
| Konteyner      | Docker, Docker Compose            |
| Reverse Proxy  | Nginx                             |

---

## API Endpointleri

Korumalı endpointler şu header ile istek bekler:

```http
Authorization: Bearer <access_token>
```

### Kullanıcı ve Kimlik Doğrulama

| Method | Endpoint         | Açıklama                                | Auth Gerekli mi? |
| ------ | ---------------- | --------------------------------------- | ---------------- |
| `POST` | `/users/`        | Yeni kullanıcı oluşturur                | Hayır            |
| `POST` | `/users/login`   | Login yapar, access/refresh token döner | Hayır            |
| `POST` | `/users/refresh` | Refresh token rotation yapar            | Hayır            |
| `POST` | `/users/logout`  | Refresh token iptal eder                | Evet             |

### Linkler

| Method   | Endpoint          | Açıklama                         | Auth Gerekli mi? |
| -------- | ----------------- | -------------------------------- | ---------------- |
| `POST`   | `/links/`         | Yeni kısa link oluşturur         | Evet             |
| `GET`    | `/links/`         | Kullanıcının linklerini listeler | Evet             |
| `GET`    | `/links/{code}`    | Tek link detayını getirir        | Evet             |
| `PUT`    | `/links/{code}`    | Linki günceller                  | Evet             |
| `DELETE` | `/links/{code}`    | Linki siler                      | Evet             |
| `GET`    | `/links/{code}/qr` | Link için QR code üretir          | Evet             |

### Redirect

| Method | Endpoint   | Açıklama                                          | Auth Gerekli mi? |
| ------ | ---------- | ------------------------------------------------- | ---------------- |
| `GET`  | `/r/{code}` | Orijinal URL'ye yönlendirir ve tıklamayı kaydeder | Hayır            |

### Analytics

| Method | Endpoint                        | Açıklama                                     | Auth Gerekli mi? |
| ------ | ------------------------------- | -------------------------------------------- | ---------------- |
| `GET`  | `/analytics/overview`           | Kullanıcının genel analytics özetini getirir | Evet             |
| `GET`  | `/analytics/links/{code}`        | Tek link için analytics bilgisi getirir      | Evet             |
| `GET`  | `/analytics/links/{code}/clicks` | Tek link için tıklama kayıtlarını getirir    | Evet             |

---

## Örnek İstekler

### Register

```http
POST /users/
Content-Type: application/json
```

```json
{
  "email": "test@example.com",
  "password": "StrongPass123*"
}
```

### Login

```http
POST /users/login
Content-Type: application/json
```

```json
{
  "email": "test@example.com",
  "password": "StrongPass123*"
}
```

Örnek response:

```json
{
  "access_token": "<access_token>",
  "refresh_token": "<refresh_token>",
  "token_type": "bearer"
}
```

### Kısa Link Oluşturma

```http
POST /links/
Authorization: Bearer <access_token>
Content-Type: application/json
```

```json
{
  "original_url": "https://github.com/"
}
```

Örnek response:

```json
{
  "code": "abc123",
  "original_url": "https://github.com/",
  "click": 0,
  "short_url": "http://go.weetis.com:8000/r/abc123"
}
```

### Redirect

```http
GET /r/abc123
```

Bu istek kullanıcıyı orijinal URL'ye yönlendirir ve tıklama kaydı oluşturur.

### Link Analytics

```http
GET /analytics/links/abc123
Authorization: Bearer <access_token>
```

Örnek response:

```json
{
  "code": "abc123",
  "original_url": "https://github.com/",
  "total_clicks": 5,
  "recent_clicks": [
    {
      "clicked_at": "2026-07-03T12:00:00",
      "ip_hash": "hashed-ip-value",
      "user_agent": "Mozilla/5.0 ...",
      "referer": null,
      "accept_language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7"
    }
  ],
  "short_url": "http://go.weetis.com:8000/r/abc123"
}
```

---

## Lokal Kurulum

### 1. Gereksinimler

- Python 3.12+
- PostgreSQL
- Redis
- Git

### 2. Repoyu Klonla

```bash
git clone https://github.com/yusuf-levent/url_shortener.git
cd url_shortener
```

### 3. Virtual Environment Oluştur ve Aktifleştir

```bash
python -m venv venv
```

Windows:

```bash
venv\Scripts\activate
```

macOS / Linux:

```bash
source venv/bin/activate
```

### 4. Paketleri Kur

```bash
pip install -r requirements.txt
```

### 5. Environment Variables Ayarla

Proje ana dizininde `.env` dosyası oluştur:

```env
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/url_shortener
TEST_DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/url_shortener_test

SECRET_KEY=a-very-long-and-secure-random-string
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

BASE_URL=http://localhost:8000

REDIS_HOST=localhost
REDIS_PORT=6379

TZ=UTC
```

### 6. PostgreSQL Database Oluştur

```sql
CREATE DATABASE url_shortener;
CREATE DATABASE url_shortener_test;
```

### 7. Migration Çalıştır

```bash
alembic upgrade head
```

### 8. Uygulamayı Başlat

```bash
uvicorn main:app --reload
```

API adresi:

```text
http://127.0.0.1:8000
```

Swagger docs:

```text
http://127.0.0.1:8000/docs
```

---

## Testler

```bash
pytest
```

Testler `TEST_DATABASE_URL` değerini kullanır. Testleri çalıştırmadan önce test database'in oluşturulmuş olması gerekir.

---

## Docker Compose Kullanımı

Proje iki Docker Compose yapılandırması içerir:

### Geliştirme (`compose.yaml`)

PostgreSQL, Redis, uygulama ve test Redis örneğini başlatır.

```bash
docker compose up -d
```

API adresi:

```text
http://localhost:8082
```

Testleri container içinde çalıştırmak için:

```bash
docker compose run --rm test
```

### Üretim (`compose.prod.yml`)

PostgreSQL, Redis ve uygulamayı geliştirme portları ve test servisleri olmadan başlatır.

```bash
docker compose -f compose.prod.yml up -d
```

> **Not:** Üretim yapılandırması `.env.prod` dosyasını kullanır. Çalıştırmadan önce uygun değerlerle oluşturulmalıdır.

---

## Nginx Reverse Proxy

Proje, uygulamanın önünde reverse proxy olarak kullanılmak üzere bir `nginx.conf` dosyası içerir. Nginx sunucunuzu, çalışan container'a (varsayılan port `8000`) istekleri yönlendirecek şekilde yapılandırın.

---

## Proje Yapısı

```text
url_shortener/
├── alembic/                 # Database migrations
├── migrations/              # Alembic migration dosyaları
│   ├── env.py
│   ├── script.py.mako
│   └── versions/            # Migration versiyon dosyaları
├── routers/                 # API router dosyaları
│   ├── admin.py             # Admin endpointleri
│   ├── analytics.py         # Analytics endpointleri
│   ├── links.py             # Link CRUD ve QR endpointleri
│   ├── redirect.py          # Public redirect endpointi
│   └── users.py             # Kullanıcı ve auth endpointleri
├── services/                # İş mantığı katmanı
│   ├── admin_service.py     # Admin işlemleri
│   ├── analytics_service.py # Analytics mantığı
│   ├── auth_redis_service.py# Redis tabanlı token yönetimi
│   ├── auth_service.py      # Kimlik doğrulama mantığı
│   ├── cache_service.py     # Redis önbellekleme mantığı
│   ├── link_query_service.py# Link sorgu işlemleri
│   ├── link_service.py      # Link CRUD mantığı
│   ├── logging_service.py   # Loglama araçları
│   ├── redis_service.py     # Redis bağlantı yönetimi
│   └── redirect_service.py  # Redirect mantığı
├── tests/                   # Pytest testleri
│   ├── conftest.py          # Test fixture ve konfigürasyon
│   ├── test_admin.py
│   ├── test_analytics.py
│   ├── test_auth_login.py
│   ├── test_auth_logout.py
│   ├── test_auth_refresh.py
│   ├── test_auth_register.py
│   ├── test_cache.py
│   ├── test_links.py
│   ├── test_redirect.py
│   ├── test_security.py
│   └── test_units.py
├── auth.py                  # JWT ve authentication yardımcıları
├── config.py                # Uygulama ayarları (Redis, TZ dahil)
├── constants.py             # Uygulama sabitleri
├── database.py              # Database bağlantısı ve session
├── Dockerfile               # Docker image tanımı
├── main.py                  # FastAPI app başlangıcı
├── models.py                # SQLAlchemy modelleri
├── schemas.py               # Pydantic şemaları
├── requirements.txt         # Python paketleri
├── compose.yaml             # Docker Compose (geliştirme)
├── compose.prod.yml         # Docker Compose (üretim)
├── nginx.conf               # Nginx reverse proxy konfigürasyonu
├── .dockerignore            # Docker ignore dosyası
├── pytest.ini               # Pytest konfigürasyonu
└── alembic.ini              # Alembic konfigürasyonu
```

---

## Gelecekte Eklenebilecekler

- Custom alias desteği
- Link expiration date
- Analytics için tarih aralığı filtresi
- User agent üzerinden browser/device analizi
- Rate limiting
- Expired refresh token cleanup
- Basit bir frontend dashboard

---

## License

This project is currently for portfolio and educational purposes.