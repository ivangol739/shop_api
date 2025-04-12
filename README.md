# Shop API

**Shop API** — это REST API для интернет-магазина на базе Django с использованием PostgreSQL, Celery и Docker. 

---

## 📦 Основные технологии

- **Django REST Framework**
- **PostgreSQL**
- **Celery** + **Redis**
- **Docker** + **Docker Compose**
- **Grappelli** (админка)
- **drf-spectacular** (OpenAPI/Swagger)

---

## 🚀 Запуск проекта

### 🔧 Шаг 1: Клонирование репозитория

```
git clone https://github.com/your-username/shop_api.git
cd shop_api
```

---

### 🛠 Шаг 2: Создание `.env` файла

Создайте файл `.env` в корневой директории проекта и добавьте туда следующие переменные окружения:

```env
# Django Settings
SECRET_KEY=

# Email Settings
EMAIL_BACKEND=
EMAIL_HOST=
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
EMAIL_PORT=
EMAIL_USE_TLS=
DEFAULT_FROM_EMAIL=

# Postgres Settings
NAME=
USER=
PASSWORD=
```

---

### 🐳 Шаг 3: Запуск проекта через Docker Compose

```
docker-compose up --build -d
```

---

### 🗄 Шаг 4: Применение миграций

```
docker-compose exec web python manage.py migrate
```

---

### 👤 Шаг 5: Создание суперпользователя

```
docker-compose exec web python manage.py createsuperuser
```

---

### 📥 Шаг 6: Загрузка тестовых данных

```
docker-compose exec web python manage.py import_shop_data /shop_api/data/shop1.yaml
```

