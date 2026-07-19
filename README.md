# URL Shortener API

A production-ready URL shortener API built with **FastAPI** and **PostgreSQL**.  
It supports user authentication, URL shortening, QR code generation, public redirects, click tracking, analytics, database migrations, automated tests, and CI/CD deployment.

## Live Demo

- **API Base URL:** https://url-shortener-q10i.onrender.com
- **Swagger Docs:** https://url-shortener-q10i.onrender.com/docs

> Note: Some hosted services may take a few seconds to respond after being inactive.

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

- **Database & Deployment**
  - PostgreSQL database
  - SQLAlchemy ORM
  - Alembic migrations
  - Dockerfile included
  - GitHub Actions CI/CD pipeline
  - Deployed on Render

- **Testing**
  - Pytest test suite
  - Authentication tests
  - Link CRUD tests
  - Redirect tests
  - QR code tests
  - Analytics tests

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
| QR Code          | qrcode, Pillow                    |
| Testing          | Pytest, FastAPI TestClient        |
| CI/CD            | GitHub Actions                    |
| Deployment       | Render                            |
| Containerization | Docker                            |

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
  "short_url": "https://url-shortener-q10i.onrender.com/r/abc123"
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
  "short_url": "https://url-shortener-q10i.onrender.com/r/abc123"
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
      "short_url": "https://url-shortener-q10i.onrender.com/r/abc123"
    }
  ],
  "total_links": 1,
  "top_links": [
    {
      "code": "abc123",
      "original_url": "https://github.com/",
      "click": 5,
      "short_url": "https://url-shortener-q10i.onrender.com/r/abc123"
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

## Docker Usage

A `Dockerfile` is included for containerizing the FastAPI application.

Build the image:

```bash
docker build -t url-shortener .
```

Run the container:

```bash
docker run -p 8000:8000 --env-file .env url-shortener
```

> Docker note: The current Docker setup runs the application container. PostgreSQL still needs to be available separately and `DATABASE_URL` must point to the correct database host. If PostgreSQL is running on the host machine, configure the database host accordingly.

---

## Project Structure

```text
url_shortener/
├── alembic/                 # Database migrations
├── routers/                 # API routers
│   ├── users.py             # User authentication endpoints
│   ├── links.py             # Link CRUD and QR endpoints
│   ├── redirect.py          # Public redirect endpoint
│   └── analytics.py         # Analytics endpoints
├── tests/                   # Pytest test suite
├── auth.py                  # JWT and authentication helpers
├── config.py                # App settings
├── database.py              # Database connection and session
├── models.py                # SQLAlchemy models
├── schemas.py               # Pydantic schemas
├── main.py                  # FastAPI app entrypoint
├── requirements.txt         # Python dependencies
└── Dockerfile               # Docker image definition
```

---

## Possible Future Improvements

- Add custom aliases for short links
- Add link expiration dates
- Add date-range filtering for analytics
- Add browser/device parsing for user agents
- Add rate limiting
- Add background cleanup for expired refresh tokens
- Add Docker Compose for PostgreSQL + API
- Add a simple frontend dashboard

---

## Türkçe Açıklama

# URL Shortener API

Bu proje **FastAPI** ve **PostgreSQL** ile geliştirilmiş, üretime yakın seviyede bir URL kısaltma API projesidir.  
Kullanıcı kimlik doğrulama, link kısaltma, QR code oluşturma, public redirect, tıklama takibi, analytics, database migration, testler ve CI/CD süreçlerini içerir.

## Canlı Demo

- **API Base URL:** https://url-shortener-q10i.onrender.com
- **Swagger Docs:** https://url-shortener-q10i.onrender.com/docs

> Not: Ücretsiz/uygun maliyetli hosting servislerinde API bir süre kullanılmadığında ilk istek birkaç saniye yavaş gelebilir.

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
  - Kullanıcının kendi linksini listeleme
  - Tek link detayını görüntüleme
  - Link güncelleme
  - Link silme

- **Güvenlik ve Sahiplik Kontrolü**
  - Kullanıcı sadece kendi linksini yönetebilir
  - Korumalı endpointler Bearer token ister
  - Analytics verileri sadece link sahibine gösterilir

- **Public Redirect**
  - Kısa links public olarak çalışır
  - Her redirect işleminde tıklama sayısı artar
  - Analytics için tıklama bilgileri kaydedilir

- **Analytics**
  - Genel dashboard verisi
  - Toplam link sayısı
  - Toplam tıklama sayısı
  - En çok tıklanan links
  - Tek link için son tıklamalar
  - User agent, referer, dil bilgisi ve IP hash takibi

- **QR code**
  - Kısa link için PNG formatında QR code üretme

- **Database ve Deployment**
  - PostgreSQL
  - SQLAlchemy ORM
  - Alembic migration
  - Dockerfile
  - GitHub Actions CI/CD
  - Render deployment

- **Testler**
  - Pytest test yapısı
  - Auth testleri
  - Link CRUD testleri
  - Redirect testleri
  - QR code testleri
  - Analytics testleri

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
| QR Code        | qrcode, Pillow                    |
| Test           | Pytest, FastAPI TestClient        |
| CI/CD          | GitHub Actions                    |
| Deployment     | Render                            |
| Container      | Docker                            |

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

### links

| Method   | Endpoint          | Açıklama                         | Auth Gerekli mi? |
| -------- | ----------------- | -------------------------------- | ---------------- |
| `POST`   | `/links/`         | Yeni kısa link oluşturur         | Evet             |
| `GET`    | `/links/`         | Kullanıcının linksini listeler | Evet             |
| `GET`    | `/links/{code}`    | Tek link detayını getirir        | Evet             |
| `PUT`    | `/links/{code}`    | Linki günceller                  | Evet             |
| `DELETE` | `/links/{code}`    | Linki siler                      | Evet             |
| `GET`    | `/links/{code}/qr` | Link için QR code üretir          | Evet             |

### Redirect

| Method | Endpoint   | Açıklama                                          | Auth Gerekli mi? |
| ------ | ---------- | ------------------------------------------------- | ---------------- |
| `GET`  | `/r/{code}` | Orijinal URL’ye yönlendirir ve tıklamayı kaydeder | Hayır            |

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
  "short_url": "https://url-shortener-q10i.onrender.com/r/abc123"
}
```

### Redirect

```http
GET /r/abc123
```

Bu istek kullanıcıyı orijinal URL’ye yönlendirir ve tıklama kaydı oluşturur.

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
  "short_url": "https://url-shortener-q10i.onrender.com/r/abc123"
}
```

---

## Lokal Kurulum

### 1. Gereksinimler

- Python 3.12+
- PostgreSQL
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

Testler `TEST_DATABASE_URL` değerini kullanır. Testleri çalıştırmadan önce test database’in oluşturulmuş olması gerekir.

---

## Docker Kullanımı

Projede FastAPI uygulamasını container haline getirmek için `Dockerfile` bulunmaktadır.

Image build et:

```bash
docker build -t url-shortener .
```

Container çalıştır:

```bash
docker run -p 8000:8000 --env-file .env url-shortener
```

> Docker notu: Mevcut Docker yapısı uygulama container’ını çalıştırır. PostgreSQL ayrıca erişilebilir olmalıdır ve `DATABASE_URL` doğru database host’una bakmalıdır. PostgreSQL host makinede çalışıyorsa database host ayarını buna göre düzenlemek gerekir.

---

## Proje Yapısı

```text
url_shortener/
├── alembic/                 # Database migrations
├── routers/                 # API router dosyaları
│   ├── users.py             # Kullanıcı ve auth endpointleri
│   ├── links.py             # Link CRUD ve QR endpointleri
│   ├── redirect.py          # Public redirect endpointi
│   └── analytics.py         # Analytics endpointleri
├── tests/                   # Pytest testleri
├── auth.py                  # JWT ve authentication yardımcıları
├── config.py                # Uygulama ayarları
├── database.py              # Database bağlantısı ve session
├── models.py                # SQLAlchemy modelleri
├── schemas.py               # Pydantic şemaları
├── main.py                  # FastAPI app başlangıcı
├── requirements.txt         # Python paketleri
└── Dockerfile               # Docker image tanımı
```

---

## Gelecekte Eklenebilecekler

- Custom alias desteği
- Link expiration date
- Analytics için tarih aralığı filtresi
- User agent üzerinden browser/device analizi
- Rate limiting
- Expired refresh token cleanup
- PostgreSQL + API için Docker Compose
- Basit bir frontend dashboard

---

## License

This project is currently for portfolio and educational purposes.
