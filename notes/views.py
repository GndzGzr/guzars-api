from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Note, Tag
from .serializers import NoteSerializer, TagSerializer


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

    def get_queryset(self):
        qs = super().get_queryset()
        
        # Support optional filtering by tag
        tag_slug = self.request.query_params.get('tag')
        if tag_slug:
            qs = qs.filter(tags__slug=tag_slug)
            
        return qs