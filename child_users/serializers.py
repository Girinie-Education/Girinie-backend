from rest_framework import serializers
from .models import ChildUser

class ChildUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChildUser
        fields = [
            'id', 'name', 'age', 'color', 'avatarUrl', 'parent',
            'order_level', 'manners_level', 'selfcare_level', 'clean_level',
            'calm_level', 'kindness_level', 'saving_level', 'eating_level', 'average_level',
            'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'parent', 'average_level', 'created_at', 'updated_at',
            'order_level', 'manners_level', 'selfcare_level', 'clean_level',
            'calm_level', 'kindness_level', 'saving_level', 'eating_level',
        ]

