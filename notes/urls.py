from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import NoteViewSet, TagViewSet, FleetingNoteViewSet, ReferenceNoteViewSet, PermanentNoteViewSet

router = DefaultRouter()
router.register(r'notes/fleeting', FleetingNoteViewSet, basename='fleeting-note')
router.register(r'notes/reference', ReferenceNoteViewSet, basename='reference-note')
router.register(r'notes/permanent', PermanentNoteViewSet, basename='permanent-note')
router.register(r'notes', NoteViewSet, basename='note')
router.register(r'tags', TagViewSet, basename='tag')

urlpatterns = [
    path('', include(router.urls)),
]