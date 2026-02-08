#!/bin/sh
set -e

echo "Esperando a la base de datos..."
counter=0
while ! nc -z db 5432; do
  counter=$((counter+1))
  if [ "$counter" -ge 30 ]; then
    echo "Timeout esperando a db" >&2
    exit 1
  fi
  sleep 1
done

echo "Inicializando migraciones si es necesario..."
python /app/scripts/init_db.py || true
flask db upgrade || true

echo "Iniciando servidor"
exec "$@"
