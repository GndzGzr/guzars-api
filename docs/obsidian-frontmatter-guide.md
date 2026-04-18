# Obsidian Frontmatter Guide for API Ingestion

This guide outlines the exact YAML frontmatter structure you should use in your Obsidian vault for each of the three note types supported by the backend: Fleeting, Reference, and Permanent notes.

**Important Tip for Obsidian Wikilinks in Frontmatter:**
If you use wikilinks in your frontmatter (like `[[Parent Note]]`), **always wrap them in quotation marks** so Obsidian and the Python YAML parser don't throw syntax errors.
✅ `parent: "[[My Parent Note]]"`
❌ `parent: [[My Parent Note]]`

---

## 1. Fleeting Notes (`type: fleeting`)
These are your quick, raw thoughts or temporary notes. If a note does not have a `type` defined, it defaults to a Fleeting Note.

```yaml
---
title: My random thought on React
type: fleeting
tags:
  - web/frontend/react
  - thoughts
parent: "[[Web Development MOC]]"
---
```

**Fields:**
*   **title:** (Optional) If omitted, the file name will be used as the title.
*   **type:** Must be `fleeting` (or omitted).
*   **tags:** A list of tags. You can use slashes (`/`) to create hierarchical tags in the database automatically.
*   **parent:** (Optional) The parent note. You can use Obsidian's wikilink syntax like `"[[Note Name]]"` (wrapped in quotes for valid YAML) or just the plain name `"Note Name"`.

---

## 2. Reference Notes (`type: reference`)
These are for highlights, summaries, or notes taken from external sources like books, articles, or videos.

```yaml
---
title: Summary of Clean Code
type: reference
author: Robert C. Martin
reference_type: Book
source_url: https://example.com/clean-code
tags:
  - programming/best-practices
  - books
parent: "[[Software Engineering]]"
---
```

**Fields:**
*   **type:** Must be `reference`.
*   **author:** (Optional) The creator of the source material.
*   **reference_type:** (Optional) The medium of the reference (e.g., `Book`, `Article`, `Video`, `Podcast`).
*   **source_url:** (Optional) A link to the original content URL.
*   *(Also supports all base note fields like `parent`, `tags`, and `title`)*

---

## 3. Permanent Notes (`type: permanent`)
These are your refined, atomic thoughts that form the core of your knowledge base (Zettelkasten).

```yaml
---
title: Functions should do one thing
type: permanent
is_atomic: true
zettel_id: 202604181200
tags:
  - programming/concept
parent: "[[Clean Code Summary]]"
---
```

**Fields:**
*   **type:** Must be `permanent`.
*   **is_atomic:** (Optional) Boolean (`true`/`false`). Defaults to `true` in the database. Represents if this note contains a single, focused idea.
*   **zettel_id:** (Optional) A custom Zettelkasten ID. If you don't provide one, the backend will automatically generate a timestamp-based ID (e.g., `20260418203512-a1b2`).
*   *(Also supports all base note fields like `parent`, `tags`, and `title`)*
