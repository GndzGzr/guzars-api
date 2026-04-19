from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Note, Tag, ReferenceNote, PermanentNote
from .serializers import NoteSerializer, TagSerializer, ReferenceNoteSerializer, PermanentNoteSerializer, NoteTreeSerializer


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'slug'


class NoteViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Note.objects.prefetch_related('tags', 'outgoing_links__target', 'incoming_links__source').all()
    serializer_class = NoteSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'slug'

    @action(detail=False, methods=['get'])
    def tree(self, request):
        """
        Returns a lightweight payload of all notes including only metadata, parent paths, and titles.
        Used primarily by the frontend to render the initial sidebar or file explorer.
        """
        queryset = self.filter_queryset(self.get_queryset())
        serializer = NoteTreeSerializer(queryset, many=True)
        return Response(serializer.data)
        
    def get_queryset(self):
        qs = super().get_queryset().filter(published=True)
        
        # Support optional filtering by tag
        tag_slug = self.request.query_params.get('tag')
        if tag_slug:
            qs = qs.filter(tags__slug=tag_slug)
            
        return qs
class FleetingNoteViewSet(NoteViewSet):
    """
    Endpoints for Fleeting notes
    """
    @action(detail=False, methods=['get'])
    def tree(self, request):
        """
        Returns a lightweight payload of all notes including only metadata, parent paths, and titles.
        Used primarily by the frontend to render the initial sidebar or file explorer.
        """
        queryset = self.filter_queryset(self.get_queryset())
        serializer = NoteTreeSerializer(queryset, many=True)
        return Response(serializer.data)
        
    def get_queryset(self):
        return super().get_queryset().filter(note_type=Note.NoteType.FLEETING)

class ReferenceNoteViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Endpoints specific to Reference notes
    """
    queryset = ReferenceNote.objects.prefetch_related('tags', 'outgoing_links__target', 'incoming_links__source').filter(published=True)
    serializer_class = ReferenceNoteSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'slug'

class PermanentNoteViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Endpoints specific to Permanent notes
    """
    queryset = PermanentNote.objects.prefetch_related('tags', 'outgoing_links__target', 'incoming_links__source').filter(published=True)
    serializer_class = PermanentNoteSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'slug'
