from rest_framework import generics, permissions, filters
from core.permissions import IsAdminOrModerator
from .models import Resource, ResourceCategory
from .serializers import ResourceSerializer, ResourceCategorySerializer


class ResourceCategoryListView(generics.ListAPIView):
    """GET /api/resources/categories/ — all categories."""
    serializer_class = ResourceCategorySerializer
    permission_classes = [permissions.AllowAny]
    queryset = ResourceCategory.objects.all()


class ResourceListView(generics.ListAPIView):
    """GET /api/resources/ — published articles & guides."""
    serializer_class = ResourceSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'summary', 'content']

    def get_queryset(self):
        qs = Resource.objects.filter(is_published=True).select_related('category')
        cat = self.request.query_params.get('category')
        if cat:
            qs = qs.filter(category_id=cat)
        return qs.order_by('-created_at')


class ResourceDetailView(generics.RetrieveAPIView):
    """GET /api/resources/<id>/ — single resource."""
    serializer_class = ResourceSerializer
    permission_classes = [permissions.AllowAny]
    queryset = Resource.objects.filter(is_published=True)


class AdminResourceView(generics.ListCreateAPIView):
    """GET/POST /api/resources/admin/ — admin: manage resources."""
    serializer_class = ResourceSerializer
    permission_classes = [IsAdminOrModerator]
    queryset = Resource.objects.all().select_related('category').order_by('-created_at')


class AdminResourceDetailView(generics.RetrieveUpdateDestroyAPIView):
    """GET/PATCH/DELETE /api/resources/admin/<id>/"""
    serializer_class = ResourceSerializer
    permission_classes = [IsAdminOrModerator]
    queryset = Resource.objects.all()
