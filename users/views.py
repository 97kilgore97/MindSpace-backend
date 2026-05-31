from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone

from .models import User, UserProfile
from .serializers import (
    UserSerializer, RegisterSerializer, LoginSerializer,
    AnonymousRegisterSerializer, ChangePasswordSerializer, UserProfileSerializer
)


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


class RegisterView(generics.CreateAPIView):
    """POST /api/users/register/ — create a full account."""
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        tokens = get_tokens_for_user(user)
        return Response({
            'user': UserSerializer(user).data,
            'tokens': tokens,
        }, status=status.HTTP_201_CREATED)


class AnonymousLoginView(APIView):
    """POST /api/users/anonymous/ — enter without an account."""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = AnonymousRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        tokens = get_tokens_for_user(user)
        return Response({
            'user': UserSerializer(user).data,
            'tokens': tokens,
            'message': 'Anonymous session created. Your data is private.',
        }, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    """POST /api/users/login/ — authenticate and receive JWT tokens."""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        user.last_active = timezone.now()
        user.save(update_fields=['last_active'])
        tokens = get_tokens_for_user(user)
        return Response({
            'user': UserSerializer(user).data,
            'tokens': tokens,
        })


class MeView(generics.RetrieveUpdateAPIView):
    """GET/PATCH /api/users/me/ — view or update own profile."""
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

    def patch(self, request, *args, **kwargs):
        # Allow updating display_name only; profile fields go via /me/profile/
        serializer = self.get_serializer(
            self.get_object(), data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class ProfileView(generics.RetrieveUpdateAPIView):
    """GET/PATCH /api/users/me/profile/ — extended profile fields."""
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        profile, _ = UserProfile.objects.get_or_create(user=self.request.user)
        return profile


class ChangePasswordView(APIView):
    """POST /api/users/change-password/"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'message': 'Password updated successfully.'})


class LogoutView(APIView):
    """POST /api/users/logout/ — blacklist the refresh token."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data['refresh']
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({'message': 'Logged out successfully.'})
        except Exception:
            return Response(
                {'error': 'Invalid or missing refresh token.'},
                status=status.HTTP_400_BAD_REQUEST
            )


# ─── Admin-only views ─────────────────────────────────────

class UserListView(generics.ListAPIView):
    """GET /api/users/ — admin: list all users."""
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = User.objects.all().select_related('profile').order_by('-date_joined')


class UserDetailView(generics.RetrieveUpdateAPIView):
    """GET/PATCH /api/users/<id>/ — admin: view/update any user."""
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = User.objects.all().select_related('profile')


@api_view(['POST'])
@permission_classes([permissions.IsAdminUser])
def flag_user(request, pk):
    """POST /api/users/<id>/flag/ — admin: mark a user as crisis."""
    try:
        user = User.objects.get(pk=pk)
        user.status = 'flagged'
        user.profile.crisis_flag = True
        user.profile.save(update_fields=['crisis_flag'])
        user.save(update_fields=['status'])
        return Response({'message': f'User {user.display_name} flagged for crisis review.'})
    except User.DoesNotExist:
        return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
