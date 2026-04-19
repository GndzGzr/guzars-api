from django.core.management.base import BaseCommand
from notes.models import Note, Tag, NoteLink

class Command(BaseCommand):
    help = 'Deletes all Notes, Tags, and NoteLinks from the database.'

    def handle(self, *args, **kwargs):
        self.stdout.write("Deleting all NoteLinks...")
        NoteLink.objects.all().delete()
        
        self.stdout.write("Deleting all Notes...")
        Note.objects.all().delete()
        
        self.stdout.write("Deleting all Tags...")
        Tag.objects.all().delete()
        
        self.stdout.write(self.style.SUCCESS("Successfully cleared the knowledge graph database (Notes, Tags, Links, and any accidentally indexed Assets)!"))