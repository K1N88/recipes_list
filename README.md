# FOODGRAM

## Содержание
- [Описание проекта](#Описание-проекта)
- [Технологический стек](#Технологический-стек)
- [Запуск проекта](#Запуск-проекта)
- [Примеры работы с проектом](#Примеры-работы-с-проектом)
- [Над проектом работали](#Над-проектом-работали)

### Описание проекта:

Проект — сайт Foodgram, «Продуктовый помощник».
На этом сервисе пользователи могут публиковать рецепты,
подписываться на публикации других пользователей, 
добавлять понравившиеся рецепты в список «Избранное», 
а перед походом в магазин скачивать сводный список продуктов, 
необходимых для приготовления одного или нескольких выбранных блюд.

### Технологический стек:

- Python
- Django
- DjangoRestFramework
- PostgreSQL
- nginx

### Запуск проекта:

Клонировать репозиторий и перейти в него в командной строке:
```
git clone git@github.com:K1N88/foodgram-project-react.git
```
Сборка /backend в контейнер:
```
sudo docker build -t foodgram .
```
Сборка /frontend в контейнер:
```
sudo docker build -t foodgram_front .
```
Запуск контейнеров:
```
sudo docker-compose up -d --build
```
Выполните миграции:
```
sudo docker exec foodgram_web_1 python manage.py migrate
```
Соберите статику:
```
sudo docker exec foodgram_web_1 python manage.py collectstatic --no-input
```
Загрузите ингридиенты:
```
sudo docker exec foodgram_web_1 python manage.py from_csv_to_base
```
Создайте суперпользователя:
```
sudo docker exec -i -t foodgram_web_1 python manage.py createsuperuser
```

### Примеры работы с проектом:

Удобную веб-страницу со справочным меню, документацией для эндпоинтов и 
разрешённых методов, с примерами запросов, ответов и кода Вы сможете посмотреть 
по адресу:

[http://localhost/api/docs/redoc.html](http://localhost/api/docs/redoc.html)

### Над проектом работал:
- [Константин Назаров](https://github.com/K1N88)
