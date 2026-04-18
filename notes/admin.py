from django.contrib import admin
from .models import Note, ReferenceNote, PermanentNote, Tag, NoteLink

class NoteLinkInline(admin.TabularInline):
    model = NoteLink
    fk_name = "source"
    extra = 0

@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ("title", "note_type", "zettel_id", "published", "created_at")
    list_filter = ("note_type", "published", "created_at", "tags")
    search_fields = ("title", "slug", "zettel_id", "content_raw")
    prepopulated_fields = {"slug": ("title",)}
    inlines = [NoteLinkInline]

@admin.register(ReferenceNote)
class ReferenceNoteAdmin(NoteAdmin):
    list_display = ("title", "reference_type", "author", "published", "created_at")
    list_filter = ("reference_type", "published", "created_at")

@admin.register(PermanentNote)
class PermanentNoteAdmin(NoteAdmin):
    list_display = ("title", "is_atomic", "published", "created_at")
    list_filter = ("is_atomic", "published", "created_at")

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "parent")
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}

@admin.register(NoteLink)
class NoteLinkAdmin(admin.ModelAdmin):
    list_display = ("source", "target", "link_type")
    list_filter = ("link_type",)
    search_fields = ("source__title", "target__title")

