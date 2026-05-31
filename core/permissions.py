from rest_framework.permissions import BasePermission


class IsAdminOrModerator(BasePermission):
    """Allow access to admin and moderator roles only."""
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role in ['admin', 'moderator']
        )


class IsCounselorOrAdmin(BasePermission):
    """Allow counselors and admins."""
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role in ['admin', 'counselor']
        )


class IsOwnerOrAdmin(BasePermission):
    """Object-level: only the owner or an admin can access."""
    def has_object_permission(self, request, view, obj):
        if request.user.role in ['admin', 'moderator']:
            return True
        owner = getattr(obj, 'user', getattr(obj, 'sender', None))
        return owner == request.user
