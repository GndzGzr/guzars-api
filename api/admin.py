from django.contrib import admin
from .models import VaultConfiguration

@admin.register(VaultConfiguration)
class VaultConfigurationAdmin(admin.ModelAdmin):
    list_display = ("__str__", )
    
    def has_add_permission(self, request):
        """Only allow one configuration instance."""
        if VaultConfiguration.objects.exists():
            return False
        return super().has_add_permission(request)
    
    def has_delete_permission(self, request, obj=None):
        """Prevent deletion to maintain the singleton."""
        return False

