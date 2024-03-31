#!/bin/ash

echo "Apply Database Migrations"
flask db migrate
flask db upgrade
exec "$@"