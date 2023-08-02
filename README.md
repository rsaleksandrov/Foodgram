# Проект FOOD GRAMM

## Описание
На этом сервисе пользователи смогут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.


## Разверытвание проекта на сервере

### Подготовка программного окружения

- Для Linux устанавливаем docker и docker-compose
```bash
sudo apt install docker.io docker-compose
```
- Для windows устанавливаем [Docker-desktop](https://www.docker.com/products/docker-desktop/)

### Установка исходных кодов и настройка окружения docker-compose
1. Клонируем (или скачиваем и распаковываем) код из [репозитория](https://github.com/rsaleksandrov/Foodgram/)
2. Переходим в папку `infra`
3. Создаем файл `.env` и прописываем в него:
```python
DB_ENGINE=django.db.backends.postgresql # указываем, что работаем с postgresql
DB_NAME=foodgram # имя базы данных
POSTGRES_USER=<логин для подключения к базе данных>
POSTGRES_PASSWORD=<пароль для подключения к БД>
DB_HOST=db # название сервиса БД Postgres в файле docker-compose.yaml
DB_PORT=5432 # порт для подключения к БД
SECRET_KEY=<секретный ключ для работы Django>
```

### Запуск проекта
Для запуска проекта, находясь в каталоге `infra` выполнить команду:
```bash
sudo docker-compose up --build
```
Ключ `--build` можно указывать только при первом запуске проекта и при обновлении backend-а

## Стек технологий и программые пакеты

### Стек техноллогий
- Python
- Django
- Docker
- Docker-compose
- Nginx
- PostgreSQL

### Программные пакеты

Для backend:
- python 3.10
- django 4.2.1
- djangorestframework 3.14.0
- djoser 2.2.0
- gunicorn 20.1.0
- django-filter 23.2
- Pillow 9.5.0
- psycopg2_binary 2.9.6

Контейнеры:
- Nginx - nginx:1.19.3
- PostgreSQL - postgres:13.0-alpine


