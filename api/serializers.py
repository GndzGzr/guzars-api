from rest_framework import serializers
from .models import VaultConfiguration

class VaultConfigurationSerializer(serializers.ModelSerializer):
    class Meta:
        model = VaultConfiguration
        fields = ['include_paths', 'exclude_paths', 'last_updated']
