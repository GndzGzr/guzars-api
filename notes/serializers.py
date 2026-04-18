from rest_framework import serializers
from .models import Note, Tag, NoteLink, ReferenceNote, PermanentNote


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'slug', 'parent']


class NoteLinkSerializer(serializers.ModelSerializer):
    target_slug = serializers.CharField(source='target.slug', read_only=True)
    target_title = serializers.CharField(source='target.title', read_only=True)
    
    class Meta:
        model = NoteLink
        fields = ['id', 'target', 'target_slug', 'target_title', 'link_type', 'target_block', 'context_text']


class NoteBacklinkSerializer(serializers.ModelSerializer):
    source_slug = serializers.CharField(source='source.slug', read_only=True)
    source_title = serializers.CharField(source='source.title', read_only=True)
    
    class Meta:
        model = NoteLink
        fields = ['id', 'source', 'source_slug', 'source_title', 'link_type', 'context_text']


class NoteSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    outgoing_links = NoteLinkSerializer(many=True, read_only=True)
    incoming_links = NoteBacklinkSerializer(many=True, read_only=True)
    parent_note_slug = serializers.CharField(source='parent_note.slug', read_only=True)
    parent_note_title = serializers.CharField(source='parent_note.title', read_only=True)
    
    class Meta:
        model = Note
        fields = [
            'id', 'title', 'slug', 'note_type', 'zettel_id', 'published',
            'content_html', 'metadata', 'toc', 'tags', 
            'parent_note', 'parent_note_slug', 'parent_note_title',
            'outgoing_links', 'incoming_links',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['content_html']

class ReferenceNoteSerializer(NoteSerializer):
    class Meta(NoteSerializer.Meta):
        model = ReferenceNote
        fields = NoteSerializer.Meta.fields + ['source_url', 'reference_url', 'author', 'reference_type']


class PermanentNoteSerializer(NoteSerializer):
    class Meta(NoteSerializer.Meta):
        model = PermanentNote
        fields = NoteSerializer.Meta.fields + ['is_atomic']
