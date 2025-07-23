#!/bin/ash

# Wait for database to be ready
echo "Waiting for database connection..."
while ! nc -z db 5432; do
  sleep 1
done
echo "Database is ready!"

# Create upload directory
mkdir -p media/uploads

# Initialize database migrations if not already initialized
if [ ! -d "migrations" ]; then
    echo "Initializing database migrations..."
    flask db init
fi

# Apply migrations
echo "Applying database migrations..."
flask db migrate -m "Auto migration"
flask db upgrade

echo "Starting application..."
exec "$@"
