# FOODGRAM-PROJECT-REACT
Дипломный проект. Приложение - "Кулинарная книга".
Адрес сервера: http://abp.myddns.me/.
#
### Шаблон наполнения env-файла
```
SECRET_KEY=# Секретный ключ приложения Django
DB_ENGINE=django.db.backends.postgresql
DB_NAME=# Имя базы данных
POSTGRES_USER=# Пользователь базы данных
POSTGRES_PASSWORD=# Пароль пользователя базы данных
DB_HOST=# Имя контейнера
DB_PORT=5432
```
### Как запустить проект:

Клонировать репозиторий и перейти в его директорию infra:

```
git clone https://github.com/abp-ce/foodgram-project-react.git
cd foodgram-project-react/infra
```

Cоздать и запустить докер-контейнеры:

```
docker-compose up -d --build
```

Выполните миграции, соберите статику, создайте суперпользователя, 
заполните базу Ingredients:

```
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py collectstatic --no-input
docker-compose exec web python manage.py createsuperuser
docker-compose exec web python manage.py populate_db
```
