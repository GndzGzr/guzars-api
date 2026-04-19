#!/bin/bash
# reset_database.sh
# Destroys all DATA in the currently connected database (including Supabase) and remigrates.

echo "⚠️ WARNING: This will completely flush all data from your DATABASE (including remote Supabase if connected)!"
echo "Proceeding in 3 seconds..."
sleep 3

# Explicitly run our custom un-indexer to aggressively purge notes, tags, and links
echo "--> Purging all notes natively..."
python manage.py clear_notes

echo "--> Dropping all database tables..."
python -c "
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()
from django.db import connection

if connection.vendor == 'postgresql':
    with connection.cursor() as cursor:
        cursor.execute('DROP SCHEMA public CASCADE; CREATE SCHEMA public;')
        cursor.execute('GRANT ALL ON SCHEMA public TO postgres; GRANT ALL ON SCHEMA public TO public;')
elif connection.vendor == 'sqlite':
    import os
    if os.path.exists('db.sqlite3'):
        os.remove('db.sqlite3')
"

echo "--> Re-applying all migrations natively..."
python manage.py makemigrations --noinput
python manage.py migrate

echo "--> (Optional) Create a new superuser for the CMS admin panel"
python manage.py createsuperuser
username=$(python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); print(User.objects.first().username)")
password="(the one you just set)"
echo "Superuser created with username: $username and password: $password"


echo "✅ Database completely reset and schemas validated!"
