#!/bin/sh
set -e

python myblog/manage.py migrate --noinput
exec python myblog/manage.py runserver 0.0.0.0:8000
