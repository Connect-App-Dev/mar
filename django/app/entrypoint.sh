#!/bin/sh

echo "Waiting for PostgreSQL to start..."

while ! nc -z $DB_HOST "${DB_PORT:=5432}"
do
    sleep 0.1
done

echo "PostgreSQL has started... Performing migrations and starting server"

python manage.py migrate --noinput

python manage.py runserver 0.0.0.0:8000