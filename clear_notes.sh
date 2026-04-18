#!/bin/bash
# clear_notes.sh
# Safely deletes all ingested Obsidian markdown data from the active database 
# (Local SQLite or Remote Supabase, depending on your .env) without destroying users/schema.

echo "⚠️ WARNING: This will delete ALL Notes, Tags, and NoteLinks!"
echo "It applies to whichever database your Django environment is currently connected to."
echo "Proceeding in 3 seconds..."
sleep 3

# Run the custom Django management command to truncate the notes data
python manage.py clear_notes

echo "✅ Knowledge graph data successfully cleared!"