from django.db import models
import datetime
from django.utils import timezone
from django.utils.text import slugify


class Note(models.Model):
    class NoteType(models.TextChoices):
        FLEETING = "FLT", "Fleeting Note"
        REFERENCE = "REF", "Reference Note"
        PERMANENT = "PRM", "Permanent Note"

    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    note_type = models.CharField(
        max_length=3, choices=NoteType.choices, default=NoteType.FLEETING
    )
    content_raw = models.TextField()
    content_html = models.TextField(blank=True)
    metadata = models.JSONField(default=dict)

    zettel_id = models.CharField(max_length=20, unique=True, null=True, blank=True)
    tags = models.ManyToManyField("Tag", related_name="notes", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        if not self.zettel_id:
            self.zettel_id = timezone.now().strftime("%Y%m%d%H%M%S")
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class ReferenceNote(Note):
    """Kitap, makale veya video özetleri için"""

    source_url = models.URLField(max_length=500, blank=True)
    author = models.CharField(max_length=255, blank=True)
    reference_type = models.CharField(
        max_length=50, help_text="Book, Article, Video vb."
    )


class PermanentNote(Note):
    """Atomik ve rafine edilmiş kalıcı düşünceler"""

    # Kalıcı notlarda hiyerarşi (Luhmann'ın numbering sistemi gibi)
    parent_note = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="children",
    )
    is_atomic = models.BooleanField(default=True)


class Tag(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=120, unique=True)
    # Hiyerarşik yapı için:
    parent = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True, related_name="children"
    )

    class Meta:
        unique_together = (
            "name",
            "parent",
        )  # Aynı seviyede aynı isimli iki etiket olmasın

    def __str__(self):
        full_path = [self.name]
        p = self.parent
        while p:
            full_path.append(p.name)
            p = p.parent
        return " / ".join(reversed(full_path))


class NoteLink(models.Model):
    class LinkType(models.TextChoices):
        REFERENCE = "REF", "General Reference"  # Genel bağlantı
        SEQUENCE = "SEQ", "Sequence (Folgezettel)"  # Bir düşüncenin devamı
        STRUCTURE = (
            "STR",
            "Structure (MOC)",
        )  # Bir "Map of Content" (İçerik Haritası) bağı

    source = models.ForeignKey(
        Note, on_delete=models.CASCADE, related_name="outgoing_links"
    )
    target = models.ForeignKey(
        Note, on_delete=models.CASCADE, related_name="incoming_links"
    )

    link_type = models.CharField(
        max_length=3, choices=LinkType.choices, default=LinkType.REFERENCE
    )

    # Notun içindeki spesifik bir bölüme mi link veriliyor? (Örn: #Giriş)
    target_block = models.CharField(max_length=255, null=True, blank=True)

    # Linkin içinde geçtiği cümle (Context)
    # Frontend'de "Backlinks" gösterirken bu cümleyi göstermek çok kullanışlı olur.
    context_text = models.TextField(null=True, blank=True)

    class Meta:
        unique_together = ("source", "target", "target_block")
