# Usage & Administration

**Navigation:** 
*   [About Guzars API](about-guzars-api.md)
*   [About Obsidian Integration](about-obsidian.md)
*   **[Usage & Administration](about-usage.md)**
*   [Setup Guide](about-setup.md)

---

## Daily Usage

After integrating Guzars API with your Obsidian vault mapping, daily operation involves writing notes locally and triggering the synchronization module. This allows the backend to consume and process new markdown structures, extract tags, parse links, and make the content live via the endpoints.

### Syncing the Graph
You can manually run the sync task (e.g., pulling from a linked GitHub repo) or configure Webhooks for your Obsidian vault.

```bash
python manage.py sync_github
```

If you ever need to clear all data and resync from scratch, run the `clear_notes` command first:

```bash
python manage.py clear_notes
```

## Administration Panel

Guzars API uses the powerful Django Administration interface as its CMS (Content Management System).

### Accessing the Django Admin Panel
To access the management dashboard, ensure the server is running and navigate to the built-in route:
*   [http://127.0.0.1:8000/admin](http://127.0.0.1:8000/admin) (Local Development)
*   `https://<your-production-url>/admin`

### Key Admin Features

1.  **Manage Notes & Drafts**: Filter notes by `Published` status. Toggle visibility for posts you might only want in draft form, without needing to delete them locally.
2.  **Inspect Connections**: The admin gives you visibility into parsed relationships (`ReferenceNote` and `NoteLink` models). You can identify broken links or orphan notes rapidly.
3.  **Tags & Taxonomies**: Rename or merge global tags independently of individual file frontmatter values.

## Interacting with the API index
The REST Framework router surfaces endpoints for fetching:
*   `/api/notes/` - List/Search public notes.
*   `/api/tags/` - Aggregation of active tags.
*   `/api/graph/` - Network data payload representing your Obsidian nodes and edges.

If you haven't set up the system yet, please follow the **[Setup Guide](about-setup.md)** to configure your environment variables and database credentials.