# ── serializers.py ────────────────────────────────────────
from rest_framework import serializers
from .models import Resource, ResourceCategory


class ResourceCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ResourceCategory
        fields = ['id', 'name', 'icon', 'color']


class ResourceSerializer(serializers.ModelSerializer):
    category = ResourceCategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=ResourceCategory.objects.all(),
        source='category',
        write_only=True,
        required=False
    )

    class Meta:
        model = Resource
        fields = [
            'id', 'title', 'summary', 'content', 'category', 'category_id',
            'read_time_mins', 'is_published', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
