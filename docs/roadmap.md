# Obsidian Headless CMS API - Roadmap

## Phase 1: Core Data Models (✅ Mostly Complete)
- [x] Base Note Model (Multi-table Inheritance setup)
- [x] Specialized Models (ReferenceNote, PermanentNote)
- [x] Tag Hierarchy
- [x] Note Relationships (NoteLink) with context text

## Phase 2: Markdown & Markdown Ingestion (Next Up)
- [ ] **Vault Parsing Services (in `notes` app)** 
  - `python-frontmatter` setup for YAML metadata parsing
  - Sub-class note classification logic based on frontmatter.
- [ ] **Markdown to HTML Conversion**
  - Implement Mistune parser.
  - Implement custom Obsidian Syntax extensions for Wikilinks (`[[link]]`) and block embeds (`![[link#header]]`).
- [ ] **Data Sync / Ingestor Logic**
  - Implement `NoteIngestor` class (`notes/services.py`).
  - Read from local file system or receive GitHub webhooks for automated ingestion.
  - Handle Tag parsing, NoteLink graph creation, and upsert logic.

## Phase 3: REST API & Serialization (Django REST Framework)
- [ ] Create serializers (Notes, ReferenceNotes, PermanentNotes, Tags).
- [ ] API Endpoints for standard CRUD/Read operations.
- [ ] Specialized Graph Queries:
  - Backlinks and Forward Links endpoints.
  - Traverse nested tags.

## Phase 4: Authentication & Sync Mechanism
- [x] Setup authentication (if required for the API).
- [x] Configure GitHub Webhooks to sync notes automatically on commit.

## Phase 5: Testing & Deployment
- [ ] Write unit tests for the Markdown parsing logic.
- [ ] Write tests for the Knowledge graph generation.
- [ ] Prepare & Deploy Serverless API on Vercel.
## Phase 6: CMS Architecture & Advanced Features (Requested)
- [x] **Type-Specific Endpoints**: Create `/api/notes/fleeting/`, `/api/notes/reference/`, and `/api/notes/permanent/` endpoints.
- [x] **Sub-Type Classification**: Allow `type` in frontmatter to define sub-types (e.g., `reference-book`, `reference-video`) while backend mapping uses the `parent` field/logic to categorize it properly under the main types (Fleeting, Reference, Permanent).
- [x] **Reference URLs**: Add `reference_url` field to Reference notes to point to external URLs or internal vault notes (`[[Book Note]]`).
- [x] **Local Asset & Image Handling**: Parse `![[image.png]]` and standard markdown images. Map them to github raw content URLs via `/api/assets/` endpoint.
- [x] **PDF Support**: Detect and handle embedded PDF files natively using `<iframe>` rendering.
- [x] **Table of Contents (TOC)**: Automatically generate and store a structured TOC JSON from `####` headers.
- [x] **Dynamic "How-To" Markdown Indices**: Serve specific markdown files when hitting root API index pages (like `/api/`) to explain how to use the endpoints natively.
- [x] **Metadata Enhancements**:
  - [x] Add `published` boolean field to all notes (default: `True`).
  - [x] Extract and save `created_at` and `updated_at` directly from GitHub commit metadata instead of generating local timestamps.
  - [x] Generate random `zettel_id` automatically on the fly if not provided.
  - [x] Provide bulletproof fallback mechanisms in the parser so broken frontmatter never crashes ingestion.
  - [x] Automatically pack unrecognized frontmatter fields into the JSON `metadata` bag.
- [x] **Remote CMS Configuration**: Move `obsidian_config.json` (folder include/exclude rules) into the database so the frontend admin panel can configure which folders sync dynamically.
- [x] **CMS Permissions**: Ensure the API is optimized for a Read-Only frontend CMS, with an admin/owner executing all backend creation/CRUD operations.

