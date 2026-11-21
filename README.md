# myblog

Блог на Django 6 и PostgreSQL 16. Посты, теги, комментарии, письмо со ссылкой на пост, поиск по триграммам, RSS и sitemap.

Секреты в `.env`. Образец — `.env.example`.

## Контейнеры

```sh
cp .env.example .env
make up
```

Сайт: http://127.0.0.1:8000/blog/
Админка: http://127.0.0.1:8000/admin/

`make up` поднимает базу и сайт, применяет миграции и добавляет недостающие примеры. Уже написанные посты не меняет. `make down` останавливает контейнеры, база и картинки остаются.

```sh
docker compose exec web python myblog/manage.py createsuperuser
```

Без почтовых настроек в `.env` страницы открываются, письмо со ссылкой не уходит.

## Без контейнера сайта

```sh
docker compose up -d db
make install
cd myblog && ../my_env/bin/python manage.py migrate
make seed
cd myblog && ../my_env/bin/python manage.py runserver
```

Порт базы берётся из `POSTGRES_PORT`. `make test` создаёт отдельную базу на этом же сервере, пользователю нужно право создавать базы. `make lint` запускает flake8.

На push и pull request Actions отдельно запускает flake8 и pytest.

## За прокси

`make up` оставляет `DEBUG=True`. Для машины за прокси, который завершает HTTPS и передаёт `X-Forwarded-Proto`:

```sh
docker compose -f docker-compose.prod.yml up --build -d
```

В этом файле `DEBUG=False`: куки только по HTTPS, редирект на HTTPS, HSTS на час, порт базы наружу не открывается. В `.env` нужны свой `SECRET_KEY` и `ALLOWED_HOSTS`. Статику, медиа и TLS отдаёт прокси. `runserver` в контейнере остаётся сервером разработки.
