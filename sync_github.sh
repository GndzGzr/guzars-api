#!/bin/bash
# sync_github.sh
# Synchronizes all Markdown files from the Guzars Obsidian repository into the database.

echo "🔄 Starting GitHub sync for GndzGzr/guzars-obsidian..."

# Ensure we're in the virtual environment if it exists
if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Run the Django management command to pull down from the main branch
python manage.py sync_github GndzGzr/guzars-obsidian --branch main

echo "✅ Sync complete!"
