#!/usr/bin/env sh
# Apply SQL migrations found in scripts/migrations to the database container using docker-compose
set -e
MIGDIR="/app/scripts/migrations"
echo "Applying SQL migrations from local $MIGDIR"
for f in $(ls scripts/migrations/*.sql | sort); do
  echo "Applying $f..."
  docker-compose exec -T db sh -c "psql -U \"$POSTGRES_USER\" -d \"$POSTGRES_DB\" -f -" < "$f"
done
echo "Migrations applied."
