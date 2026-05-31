from django.contrib import admin
from .models import Resource, ResourceCategory, CrisisContact

@admin.register(ResourceCategory)
class ResourceCategoryAdmin(admin.ModelAdmin):
    list_display = ['name']

@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'is_published', 'created_at']
    list_filter = ['is_published', 'category']

@admin.register(CrisisContact)
class CrisisContactAdmin(admin.ModelAdmin):
    list_display = ['country', 'hotline', 'availability']
