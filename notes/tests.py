from django.test import TestCase
from notes.parsers import parse_wikilink, render_html_wikilink, render_markdown_to_html, extract_links_from_content
from notes.services import NoteIngestor
from notes.models import Note, Tag, NoteLink

class ParserTests(TestCase):
    def test_extract_links_from_content(self):
        text = "This is a note with a [[Link to Page]] and another [[Target#Heading|Alias Name]]."
        links = extract_links_from_content(text)
        
        self.assertEqual(len(links), 2)
        
        link1 = links[0]
        self.assertEqual(link1['target_slug'], 'link-to-page')
        self.assertEqual(link1['target_original'], 'Link to Page')
        self.assertEqual(link1['target_block'], '')
        
        link2 = links[1]
        self.assertEqual(link2['target_slug'], 'target')
        self.assertEqual(link2['target_original'], 'Target')
        self.assertEqual(link2['target_block'], 'heading') # Slugified explicitly or implicitly in function
    
    def test_render_markdown_to_html_wikilinks(self):
        text = "Here is a [[Test Note]]."
        html = render_markdown_to_html(text)
        # mistune rendering wraps in <p> usually, but let's check the anchor tag
        self.assertIn('<a href="/api/notes/test-note" class="internal-link">Test Note</a>', html)

        text_alias = "Here is a [[Target#My Heading|Click Here]]."
        html_alias = render_markdown_to_html(text_alias)
        self.assertIn('<a href="/api/notes/target#my-heading" class="internal-link">Click Here</a>', html_alias)


class NoteIngestorTests(TestCase):
    def setUp(self):
        self.ingestor = NoteIngestor()
        self.markdown_content = """---
title: My Atomic Concept
type: permanent
tags:
  - knowledge/engineering
  - test/unit
---
This is a test permanent note that links to a [[Fleeting Thought]].
"""

    def test_ingest_note_creates_note_and_tags(self):
        note, created = self.ingestor.ingest_note("test-file", self.markdown_content)
        
        self.assertTrue(created)
        self.assertEqual(note.title, "My Atomic Concept")
        self.assertEqual(note.note_type, Note.NoteType.PERMANENT)
        
        # Tags should be created matching the hierarchy
        tags = note.tags.all()
        self.assertEqual(tags.count(), 2)
        
        # Check specific tag logic (leaf tags)
        tag_names = [t.name for t in tags]
        self.assertIn("engineering", tag_names)
        self.assertIn("unit", tag_names)
        
        # Check the parent-child relationships
        engineering_tag = tags.get(name="engineering")
        self.assertIsNotNone(engineering_tag.parent)
        self.assertEqual(engineering_tag.parent.name, "knowledge")

    def test_ingest_note_creates_links(self):
        note, created = self.ingestor.ingest_note("test-file", self.markdown_content)
        
        # Check that the outgoing link was saved
        links = NoteLink.objects.filter(source=note)
        self.assertEqual(links.count(), 1)
        
        link = links.first()
        self.assertEqual(link.target.slug, "fleeting-thought")
        # Target note should have been created as a stub
        self.assertEqual(link.target.title, "Fleeting Thought")
        self.assertEqual(link.target.note_type, Note.NoteType.FLEETING)
