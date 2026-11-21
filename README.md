# myblog

Блог на Django 6 и PostgreSQL 16. Посты, теги, комментарии, письмо со ссылкой на пост, поиск по триграммам, RSS и sitemap.

Секреты лежат в `.env`. Образец — `.env.example`.

## Контейнеры

```sh
cp .env.example .env
make up
```

Сайт: http://127.0.0.1:8000/blog/  
Админка: http://127.0.0.1:8000/admin/

`make up` поднимает базу и сайт, применяет миграции и, если постов ещё нет, добавляет несколько примеров. Повторный запуск их не дублирует. Остановка — `make down`, данные базы остаются.

На push и pull request GitHub Actions гоняет flake8 и pytest.

```sh
docker compose exec web python myblog/manage.py createsuperuser
```

Без почтовых настроек в `.env` страницы работают, отправка ссылки на пост — нет.

## Сайт на хосте

База всё равно нужна. Её можно поднять отдельно, порт берётся из `POSTGRES_PORT`.

```sh
docker compose up -d db
make install
cd myblog && ../my_env/bin/python manage.py migrate
make seed
cd myblog && ../my_env/bin/python manage.py runserver
```

`make test` создаёт отдельную базу на этом же сервере. Пользователь из `.env` должен уметь создавать базы. `make lint` запускает flake8.
