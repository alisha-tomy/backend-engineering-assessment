#!/usr/bin/env bash
# python manage.py makemigrations
python manage.py migrate
python manage.py test quiz
python manage.py collectstatic --noinput
python manage.py createsuperuser --noinput
python manage.py runserver 0.0.0.0:8000
