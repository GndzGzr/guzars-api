# About Obsidian Integration

**Navigation:** 
*   [About Guzars API](about-guzars-api.md)
*   **[About Obsidian Integration](about-obsidian.md)**
*   [Usage & Administration](about-usage.md)
*   [Setup Guide](about-setup.md)

---

## How It Works

This integration acts as the bridge between your private Obsidian vault (local markdown files) and your public-facing API. It allows seamless, version-controlled synchronization of your notes directly into a relational database.

### Vault Structure & Graph Mapping
When the backend processes your vault files, it analyzes:
1.  **Markdown Files (`.md`)**: Extracts content, headings, and generates a Table of Contents.
2.  **Frontmatter (YAML)**: Captures properties like `title`, `published`, `date`, `tags`, or any custom fields you map.
3.  **WikiLinks (`[[Link]]`)**: Analyzes internal links to construct a connection graph. This allows the API to serve 'linked mentions' and outgoing links just like the local Obsidian graph view.

### Publishing Workflow
By default, the API will respect an `published: true` toggle in your Obsidian frontmatter.
If you draft a note inside Obsidian but keep `published: false` (or omit it entirely), the API will keep the document hidden from public endpoints while still syncing its metadata for internal linking.

### Managing Obsidian Metadata via Admin
Once synced, all notes and relationships are manageable in the [Django Admin Panel](/admin). While the primary source of truth is your local Obsidian vault, you can override database fields, view parsed node relationships, and configure tags directly in the browser.

For next steps, view the **[Usage & Administration](about-usage.md)** guide to learn how to operate the sync scripts and use the Admin panel.