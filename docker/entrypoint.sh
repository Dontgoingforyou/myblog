#!/bin/sh
set -e

python myblog/manage.py migrate --noinput
python myblog/manage.py seed
exec python myblog/manage.py runserver 0.0.0.0:8000
