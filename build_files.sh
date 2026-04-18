#!/bin/bash
# Install exact requirements specified via file
python3.12 -m pip install -r requirements.txt

# Run migrations so the Vercel deployment correctly setups the remote Supabase structure
python3.12 manage.py migrate --noinput
