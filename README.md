[![codecov](https://codecov.io/gh/ivangol739/shop_api/branch/main/graph/badge.svg)](https://codecov.io/gh/ivangol739/shop_api)


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
HOST=
PORT=

# Auth Settings Google
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = 
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = 
SOCIAL_AUTH_GOOGLE_OAUTH2_REDIRECT_URI = 
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


## Дополнительно
### 🌐 Авторизация через google

```
https://accounts.google.com/o/oauth2/v2/auth?
client_id=SOCIAL_AUTH_GOOGLE_OAUTH2_KEY
&redirect_uri=SOCIAL_AUTH_GOOGLE_OAUTH2_REDIRECT_URI
&response_type=code
&scope=openid%20email%20profile
&access_type=offline
&prompt=consent
```
Вставить в код `SOCIAL_AUTH_GOOGLE_OAUTH2_KEY` и `SOCIAL_AUTH_GOOGLE_OAUTH2_REDIRECT_URI`, далее вставить ссылку в браузер для авторизации.

### Запустить тесты

```
docker-compose run --rm test
```