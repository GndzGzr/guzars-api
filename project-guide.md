Project Context: Obsidian Headless CMS API
🎯 Overview
A modular, high-performance API designed to function as a Headless CMS for Obsidian vaults. It transforms a collection of Markdown files into a queryable Knowledge Graph using Zettelkasten methodology.

🛠 Tech Stack
Backend: Django 6.0+ (Python 3.12+)

API Framework: Django REST Framework (DRF)

Package Manager: uv

Database: SQLite (Portable/Relational)

Parsing: python-frontmatter (Metadata) & mistune (Markdown to HTML)

Source Provider: GitHub (via Webhooks/REST API) predominantly, Local File System as fallback.

Authentication & Security:
- Private API: Endpoints are secured (e.g., via Token Auth).
- Read first: The API starts strictly as a Read-Only interface to visualize the Vault graph, with edit/create capabilities coming later for the owner.

🏗 Database Architecture (Zettelkasten & Relationships)
1. Note Inheritance Model

We use Multi-table Inheritance to allow notes to evolve:

Note (Base): Common fields (title, slug, content, metadata JSON, zettel_id).

FleetingNote: Transient thoughts (stored in base Note with type discriminator).

ReferenceNote (Child): Adds source_url, author, reference_type.

PermanentNote (Child): Atomic thoughts, adds parent_note (self-referential) and is_atomic.

2. Relationships

Tag: Supports Nested Tags (e.g., #dev/python/django) via a parent ForeignKey.

NoteLink: Manages the Knowledge Graph.

Tracks source and target notes.

Stores link_type (Sequence vs. Reference).

Stores context_text (the sentence surrounding the link) for rich backlinks.

🧩 Key Logic & Services
Ingestion Pipeline (notes/services.py)

The NoteIngestor class handles the conversion from Markdown to DB:

Extract: Uses frontmatter to separate YAML from body.

Classify: Determines model class based on type field in YAML.

Upsert: Uses update_or_create on the slug to prevent duplicates.

Tagging: Handles hierarchical tag creation.

Obsidian-Specific Syntax

Wikilinks: [[Note Name]] or [[Note Name|Alias]]

Embeds: ![[Image.png]] or ![[Note Name#Heading]]

Parser Goal: These must be resolved into valid API URLs or Relative Links during the content_html generation phase.

🚦 Coding Standards
Modularity: Keep "Source Providers" (how we get the file) separate from "Parsers" (how we read the file).

Performance: Favor select_related and prefetch_related for graph queries (Backlinks).

Naming: Use Zettelkasten terminology (Atomic, Backlink, Folgezettel, MOC).

REST: Follow standard RESTful patterns for endpoints.
