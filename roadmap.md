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