#!/bin/bash
# Install exact requirements specified via file (breaking system packages to bypass PEP 668 on Vercel)
python3.12 -m pip install -r requirements.txt --break-system-packages

# Run makemigrations so Vercel notices schema changes
python3.12 manage.py makemigrations --noinput

# Run migrations so the Vercel deployment correctly setups the remote Supabase structure
python3.12 manage.py migrate --noinput
python3.12 manage.py collectstatic --noinput
