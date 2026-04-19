import logging
import frontmatter
from django.utils.text import slugify
from notes.models import Note, Tag, ReferenceNote, PermanentNote, NoteLink
from notes.parsers import render_markdown_to_html, extract_links_from_content, extract_toc_from_content

logger = logging.getLogger(__name__)

class NoteIngestor:
    """
    Handles parsing Obsidian Markdown files, extracting frontmatter,
    and upserting them into the database appropriately based on type.
    """
    def __init__(self):
        pass

    def _clean_metadata_for_json(self, meta):
        import datetime
        if isinstance(meta, dict):
            return {k: self._clean_metadata_for_json(v) for k, v in meta.items()}
        elif isinstance(meta, list):
            return [self._clean_metadata_for_json(i) for i in meta]
        elif isinstance(meta, (datetime.date, datetime.datetime)):
            return meta.isoformat()
        return meta

    def parse_markdown(self, raw_content: str):
        """
        Parses raw text (including frontmatter).
        Returns metadata (dict) and content (str).
        """
        post = frontmatter.loads(raw_content)
        return post.metadata, post.content

    def _get_or_create_tag_path(self, tag_path: str):
        """
        Converts 'dev/python/django' into proper Tag objects with parent hierarchy.
        Returns the leaf Tag object.
        """
        parts = [p.strip() for p in tag_path.split("/") if p.strip()]
        if not parts:
            return None

        parent = None
        current_tag = None
        for p in parts:
            tag_slug = slugify(p)
            current_tag, created = Tag.objects.get_or_create(
                name=p,
                parent=parent,
                defaults={'slug': tag_slug}
            )
            parent = current_tag
        
        return current_tag
        
    def _sync_tags(self, note_instance, tags_data):
        """
        Links Tags extracted from frontmatter to the Note instance.
        """
        if not tags_data or not isinstance(tags_data, list):
            return

        leaf_tags = []
        for tag_path in tags_data:
            leaf_tag = self._get_or_create_tag_path(tag_path)
            if leaf_tag:
                leaf_tags.append(leaf_tag)
        
        note_instance.tags.set(leaf_tags)

    def ingest_note(self, filepath: str, raw_content: str, created_at=None, updated_at=None):
        filename = filepath.split('/')[-1]
        file_path_clean = filepath
        """
        Primary ingestion function for a single Markdown file context.
        """
        try:
            metadata, content = self.parse_markdown(raw_content)
        except Exception as e:
            logger.error(f"Failed to parse frontmatter in {filename}: {e}")
            metadata = {}
            content = raw_content
        
        metadata = self._clean_metadata_for_json(metadata)
        # Derive title and slug
        title = metadata.get('title') or filename.replace('.md', '')
        slug = metadata.get('slug', slugify(title))
        
        # Determine main type from parent or type
        parent_val = str(metadata.get('parent', '')).lower().strip()
        type_val = str(metadata.get('type', '')).lower().strip()
        
        if parent_val in ['reference', 'permanent', 'fleeting']:
            main_type = parent_val
        elif type_val.startswith('reference'):
            main_type = 'reference'
        elif type_val.startswith('permanent'):
            main_type = 'permanent'
        else:
            main_type = 'fleeting'
            
        note_type_str = main_type
        
        # Base note defaults
        defaults = {
            'title': title,
            'file_path': file_path_clean,
            'content_raw': content,
            'content_html': render_markdown_to_html(content),
            'metadata': metadata,
            'toc': extract_toc_from_content(content),
            'published': str(metadata.get('published', True)).lower() == 'true' if isinstance(metadata.get('published', True), str) else metadata.get('published', True)
        }
        
        if created_at:
            defaults['created_at'] = created_at
        if updated_at:
            defaults['updated_at'] = updated_at
        
        if 'zettel_id' in metadata:
            defaults['zettel_id'] = metadata['zettel_id']
        else:
            import uuid
            from django.utils import timezone
            defaults['zettel_id'] = timezone.now().strftime("%Y%m%d%H%M%S") + "-" + uuid.uuid4().hex[:4]

        # The parent field is exclusively for categorizing Fleeting/Reference/Permanent
        # So we do not link it to another Note record as parent_note.
            
        # Determine specific Note class based on type
        if main_type == 'reference':
            defaults['note_type'] = Note.NoteType.REFERENCE
            
            # YAML frontmatter returns `None` for empty keys. 
            # We must coalesce them to `""` to satisfy Django's NOT NULL constraint.
            s_url = metadata.get('source_url', '')
            defaults['source_url'] = str(s_url) if s_url is not None else ''
            
            r_url = metadata.get('reference_url', '')
            defaults['reference_url'] = str(r_url) if r_url is not None else ''
            
            # YAML sometimes parses lists: author: ["Name 1", "Name 2"]
            author_val = metadata.get('author', '')
            if isinstance(author_val, list):
                defaults['author'] = ", ".join(str(a) for a in author_val)
            else:
                defaults['author'] = str(author_val) if author_val is not None else ''
                
            # Try to infer reference_type from sub-type e.g. "type: reference-book" -> "book"
            if "-" in type_val:
                ref_type = type_val.split("-", 1)[1]
                defaults['reference_type'] = str(ref_type) if ref_type is not None else ''
            else:
                ref_type = metadata.get('reference_type', '')
                defaults['reference_type'] = str(ref_type) if ref_type is not None else ''
                
            model_class = ReferenceNote
        elif main_type == 'permanent':
            defaults['note_type'] = Note.NoteType.PERMANENT
            defaults['is_atomic'] = str(metadata.get('is_atomic', True)).lower() == 'true' if isinstance(metadata.get('is_atomic', True), str) else metadata.get('is_atomic', True)
            model_class = PermanentNote
        else:
            defaults['note_type'] = Note.NoteType.FLEETING
            model_class = Note


        # Pre-promote base Note to Child explicitly if it exists to avoid update_fields error
        existing = Note.objects.filter(slug=slug).first()
        if existing:
            if model_class == ReferenceNote and not hasattr(existing, 'referencenote'):
                rn = ReferenceNote(note_ptr_id=existing.id)
                rn.__dict__.update(existing.__dict__)
                rn.save()
            elif model_class == PermanentNote and not hasattr(existing, 'permanentnote'):
                pn = PermanentNote(note_ptr_id=existing.id)
                pn.__dict__.update(existing.__dict__)
                pn.save()

        note_instance, created = model_class.objects.update_or_create(
            slug=slug,
            defaults=defaults
        )
        
        # Sync Tags
        self._sync_tags(note_instance, metadata.get('tags', []))
        
        # Link Logic (extract links from content and save to NoteLink)
        self._sync_links(note_instance, content)

        return note_instance, created

    def _sync_links(self, note_instance: Note, content: str):
        """
        Parses the raw content for out-bound links, creating them in NoteLink.
        """
        # Delete old outgoing links to rebuild them
        NoteLink.objects.filter(source=note_instance).delete()
        
        links_data = extract_links_from_content(content)
        
        seen_links = set()
        for ld in links_data:
            link_key = (ld['target_slug'], ld['target_block'])
            if link_key in seen_links: continue
            seen_links.add(link_key)
            target_slug = ld['target_slug']
            
            # Find the target note (if it exists)
            target_note = Note.objects.filter(slug=target_slug).first()
            
            if not target_note:
                # If the linked note doesn't exist, we skip it
                # to prevent polluting the DB with empty stub notes.
                continue
            
            # create the NoteLink
            NoteLink.objects.create(
                source=note_instance,
                target=target_note,
                target_block=ld['target_block'],
                context_text=ld['context_text'],
                link_type=NoteLink.LinkType.REFERENCE
            )
