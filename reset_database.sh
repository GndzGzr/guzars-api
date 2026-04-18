#!/bin/bash
# reset_database.sh
# This script completely destroys the local SQLite database and rebuilds it from scratch.

echo "⚠️ WARNING: This will completely destroy the local database!"
echo "Proceeding in 3 seconds..."
sleep 3

echo "--> Deleting db.sqlite3..."
rm -f db.sqlite3

echo "--> Re-applying all migrations..."
# Assuming you are running this within the virtual environment
python manage.py migrate

echo "--> (Optional) Create a new superuser for the CMS admin panel"
# Uncomment the line below if you want it to ask for a superuser immediately
# python manage.py createsuperuser

echo "✅ Database completely reset!"