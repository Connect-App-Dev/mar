#! /bin/sh
rm -rf db.sqlite3
service postgresql stop
rm -rf /var/lib/postgresql/data/*
/usr/local/share/pq-init.sh
#python ../manage.py migrate