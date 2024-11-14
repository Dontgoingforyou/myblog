# Сервис для ведения блога

Сервис написан в рамках самообучения. Будет дополняться.

## Функциональные возможности

- Реализован CRUD для постов
- Отправка электронных писем с рекомендуемыми постами
- Возможность комментировать посты
- Тегирование постов и извлечение постов по схожести
- Вывод свежих постов и самых комментируемых постов 
- Реализована RSS лента новостей
- Реализована карта сайта
- Механизм полнотекстового поиска 

## Стэк технологии

- Django
- PostgreSQL
- HTML/CSS
- Django-taggit
- Markdown

## Установка

1. Склонируйте репозиторий
   ```bash
   https://github.com/Dontgoingforyou/myblog.git
   
2. Установите зависимости
   ```bash
   pip install -r requirements.txt

3. Заполните .env.sample файл своими данными   

4. Сделайте миграции для создания БД
   ```bash
   python manage.py migrate
   
5. Создайте суперпользователя для доступа к админке
   ```bash
   python manage.py createsuperuser
   
6. Загрузите данные из фикстуры(если нужно)
   ```bash
   python manage.py loaddata mysite_data.json
   
7. Запустите сервер
   ```bash
   python manage.py runserver