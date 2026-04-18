from django.db import models

class VaultConfiguration(models.Model):
    """
    Singleton database table storing CMS-level configurations
    such as what GitHub folders to sync.
    """
    include_paths = models.JSONField(default=list, blank=True, help_text='List of folder paths to exclusively sync')
    exclude_paths = models.JSONField(default=list, blank=True, help_text='List of folder paths to explicitly ignore')
    last_updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj

    def __str__(self):
        return "Vault Sync Configuration"
