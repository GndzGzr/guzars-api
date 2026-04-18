import logging
import frontmatter
from django.utils.text import slugify
from notes.models import Note, Tag, ReferenceNote, PermanentNote, NoteLink
from notes.parsers import render_markdown_to_html, extract_links_from_content

logger = logging.getLogger(__name__)

class NoteIngestor:
    """
    Handles parsing Obsidian Markdown files, extracting frontmatter,
    and upserting them into the database appropriately based on type.
    """
    def __init__(self):
        pass

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

    def ingest_note(self, filename: str, raw_content: str):
        """
        Primary ingestion function for a single Markdown file context.
        """
        metadata, content = self.parse_markdown(raw_content)
        
        # Derive title and slug
        # Filename acts as title if title is missing from metadata. Usually we strip '.md'
        title = metadata.get('title', filename.replace('.md', ''))
        slug = metadata.get('slug', slugify(title))
        note_type_str = str(metadata.get('type', 'fleeting')).lower()
        
        # Base note defaults
        defaults = {
            'title': title,
            'content_raw': content,
            'content_html': render_markdown_to_html(content),
            'metadata': metadata,
        }
        
        if 'zettel_id' in metadata:
            defaults['zettel_id'] = metadata['zettel_id']

        # Handle explicit parent-child logic from frontmatter (e.g. parent: "Biology Course")
        parent_name = metadata.get('parent')
        if parent_name:
            if str(parent_name).startswith("[[") and str(parent_name).endswith("]]"):
                parent_name = str(parent_name)[2:-2].split("|")[0]
            
            parent_slug = slugify(parent_name)
            # Create a placeholder parent note if it doesn't exist yet so we can attach immediately
            parent_obj, p_created = Note.objects.get_or_create(
                slug=parent_slug,
                defaults={
                    'title': parent_name,
                    'content_raw': '',
                    'note_type': Note.NoteType.FLEETING
                }
            )
            defaults['parent_note'] = parent_obj
            
        # Determine specific Note class based on type
        if note_type_str == 'reference':
            defaults['note_type'] = Note.NoteType.REFERENCE
            defaults['source_url'] = metadata.get('source_url', '')
            defaults['author'] = metadata.get('author', '')
            defaults['reference_type'] = metadata.get('reference_type', '')
            model_class = ReferenceNote
        elif note_type_str == 'permanent':
            defaults['note_type'] = Note.NoteType.PERMANENT
            defaults['is_atomic'] = metadata.get('is_atomic', True)
            model_class = PermanentNote
        else:
            defaults['note_type'] = Note.NoteType.FLEETING
            model_class = Note

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
        
        for ld in links_data:
            target_slug = ld['target_slug']
            # We must get or create the target note, or at least try to link it.
            # If it's an unresolved link, we might create a minimal 'Fleeting' stub note
            target_note, t_created = Note.objects.get_or_create(
                slug=target_slug,
                defaults={
                    'title': ld['target_original'],
                    'content_raw': '',  # Empty placeholder
                    'note_type': Note.NoteType.FLEETING
                }
            )
            
            # create the NoteLink
            NoteLink.objects.create(
                source=note_instance,
                target=target_note,
                target_block=ld['target_block'],
                context_text=ld['context_text'],
                link_type=NoteLink.LinkType.REFERENCE
            )
