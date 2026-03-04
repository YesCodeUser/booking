# 🏨 Hotel Booking API

Реализация RESTful API для системы бронирования гостиничных номеров. Проект выполнен в рамках тестового задания на позицию Junior Backend Developer.

---

## 🛠 Технологический стек

- Язык: Python 3.12+
- Фреймворк: Django 6.0 + Django REST Framework (DRF)
- База данных: PostgreSQL
- Авторизация: JWT (библиотеки Djoser + SimpleJWT)
- Документация: Swagger / OpenAPI 3.0 (drf-spectacular)
- Тестирование: Pytest + pytest-django
- Качество кода: Ruff (линтер) + Black (форматтер)

---

## 🚀 Быстрый запуск

### 1. Подготовка окружения

Склонируйте репозиторий и создайте виртуальное окружение:

- python -m venv venv
- Для Windows: venv\Scripts\activate
- Для Linux/macOS: source venv/bin/activate
- pip install -r requirements.txt

---

### 2. Настройка базы данных (.env)

В корневом каталоге проекта создайте файл .env и добавьте настройки вашей СУБД PostgreSQL:

- POSTGRES_DB=your_db
- POSTGRES_USER=your_user
- POSTGRES_PASSWORD=your_password
- POSTGRES_HOST=localhost
- POSTGRES_PORT=5432
- SECRET_KEY=your_secret_key

---

### 3. Миграции и создание Администратора

- python manage.py migrate
- python manage.py createsuperuser

---

### 4. Запуск сервера

- python manage.py runserver

---

## 🧪 Тестирование и Линтинг

Запуск автоматизированных тестов (покрытие сценариев: бронирование, овербукинг, права доступа):

- pytest

Проверка кода линтером:

- ruff check .

---

## 📖 Документация API

После запуска сервера полная интерактивная документация доступна по адресу:

👉 Swagger UI: http://127.0.0.1:8000/api/schema/swagger-ui/

---

## 📑 Основные эндпоинты

### 🔐 Авторизация и пользователи (Djoser)

- POST /auth/users/ — Регистрация нового аккаунта.
- POST /auth/jwt/create/ — Вход (получение Access и Refresh токенов).
- GET /auth/users/me/ — Просмотр данных своего профиля.

---

### 🛌 Номера (Rooms)

- GET /api/rooms/ — Список всех комнат. Доступны фильтрация и сортировка по цене и местам.
- GET /api/rooms/available/ — Поиск свободных комнат. Параметры: ?arrival=YYYY-MM-DD&departure=YYYY-MM-DD.

---

### 📅 Бронирования (Bookings)

Доступно только авторизованным пользователям (Bearer Token).

- GET /api/bookings/ — Список бронирований текущего пользователя.
- POST /api/bookings/ — Создание новой брони (с проверкой доступности дат).
- DELETE /api/bookings/{id}/ — Отмена бронирования (статус записи меняется на Cancelled).
