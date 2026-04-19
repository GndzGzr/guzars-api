# About Guzars API

**Navigation:** 
*   **[About Guzars API](about-guzars-api.md)**
*   [About Obsidian Integration](about-obsidian.md)
*   [Usage & Administration](about-usage.md)
*   [Setup Guide](about-setup.md)

---

## What is Guzars API?

Guzars API is a custom backend solution designed to synchronize your Obsidian vault with a web-accessible database. It parses local markdown files, extracts internal links, tags, and frontmatter, and serves this interconnected graph data as a clean REST API. This makes it effortless to expose your private knowledge base to a public-facing blog or portfolio built with frameworks like Next.js or Nuxt.

## Core Features
1. **Automated Note Synchronization**: Trigger sync processes to update the database automatically based on your Obsidian vault changes.
2. **Graph Data Structure**: It doesn't just store files; it records exact connections (WikiLinks) so your frontend can render an interactive knowledge graph.
3. **Admin Dashboard**: Manage metadata, manually publish/unpublish specific notes, and supervise tags via the built-in [Django Admin Panel](/admin).
4. **Markdown Parsing**: Natively extracts standard Obsidian frontmatter, tags, heading structures, and tables of contents.

## Next Steps

To get started, follow the **[Setup Guide](about-setup.md)**, or read about how we map your vault in **[About Obsidian Integration](about-obsidian.md)**. If you've already configured your environment, head over to **[Usage & Administration](about-usage.md)**.