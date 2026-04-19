# Setup Guide

**Navigation:** 
*   [About Guzars API](about-guzars-api.md)
*   [About Obsidian Integration](about-obsidian.md)
*   [Usage & Administration](about-usage.md)
*   **[Setup Guide](about-setup.md)**

---

## Getting Started

Follow these steps to initialize and configure Guzars API for rendering your Obsidian notes. This ensures the Django application can connect, migrate its databases, and serve content accurately.

## 1. Environment Setup

*   Clone the `/backend` directory and enter `guzars-api`.
*   Ensure **Python 3.10+** and `pip` are installed on your machine.
*   Create a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate
```
*   Install dependencies via `requirements.txt`:
```bash
pip install -r requirements.txt
```

## 2. Configuration & Linking your Vault

You must configure `vault-config.json` or environmental equivalents linking your Obsidian vault source (GitHub / local path). Set up your environment file:
*   Make a copy of `.env.example` as `.env` and configure Django keys.
*   Register API tokens for GitHub if syncing raw files directly from your private tracker repo.

## 3. Database Initialization

Guzars API uses SQLite as a default but supports scalable databases like PostgreSQL.
*   Once database variables are set, run migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```
*   Create an admin account to configure tags and notes:
```bash
python manage.py createsuperuser
```

## 4. Run Server

You are now ready to launch the backend server:
```bash
python manage.py runserver
```

To configure data ingestion and manually operate endpoints, refer to the **[Usage & Administration](about-usage.md)**. Use the [Django Admin Panel](http://127.0.0.1:8000/admin) to explore synced references.