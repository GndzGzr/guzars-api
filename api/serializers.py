from rest_framework import serializers
from .models import VaultConfiguration

class VaultConfigurationSerializer(serializers.ModelSerializer):
    class Meta:
        model = VaultConfiguration
        fields = ['include_paths', 'exclude_paths', 'last_updated']

from django.contrib.auth.models import User

class UserSignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'password', 'email']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password']
        )
        return user
