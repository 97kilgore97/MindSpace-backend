from django.db import models


class ResourceCategory(models.Model):
    name = models.CharField(max_length=100)
    icon = models.CharField(max_length=50, blank=True)
    color = models.CharField(max_length=20, blank=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Resource Categories'
        ordering = ['name']


class Resource(models.Model):
    title = models.CharField(max_length=200)
    summary = models.TextField(blank=True)
    content = models.TextField()
    category = models.ForeignKey(ResourceCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='resources')
    read_time_mins = models.PositiveIntegerField(default=5)
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class CrisisContact(models.Model):
    country = models.CharField(max_length=100)
    hotline = models.CharField(max_length=50)
    availability = models.CharField(max_length=100, default='24/7')

    def __str__(self):
        return f"{self.country} - {self.hotline}"
