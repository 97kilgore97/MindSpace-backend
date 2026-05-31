from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from .models import User, UserProfile


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['avatar', 'bio', 'phone', 'date_of_birth', 'crisis_flag', 'streak_days']
        read_only_fields = ['crisis_flag', 'streak_days']


class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'email', 'display_name', 'is_anonymous',
            'role', 'status', 'date_joined', 'last_active', 'profile'
        ]
        read_only_fields = ['id', 'date_joined', 'last_active', 'role', 'status']


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, label='Confirm password')

    class Meta:
        model = User
        fields = ['email', 'display_name', 'password', 'password2']

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({'password': 'Passwords do not match.'})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(
            email=validated_data['email'],
            display_name=validated_data.get('display_name', ''),
            password=validated_data['password'],
        )
        UserProfile.objects.create(user=user)
        return user


class AnonymousRegisterSerializer(serializers.Serializer):
    """Creates a temporary anonymous account — no email or password required."""
    display_name = serializers.CharField(max_length=50, default='Anonymous')

    def create(self, validated_data):
        import uuid
        fake_email = f"anon_{uuid.uuid4().hex[:10]}@mindspace.internal"
        user = User.objects.create_user(
            email=fake_email,
            display_name=validated_data.get('display_name', 'Anonymous'),
            password=None,
            is_anonymous=True,
        )
        UserProfile.objects.create(user=user)
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        user = authenticate(username=attrs['email'], password=attrs['password'])
        if not user:
            raise serializers.ValidationError('Invalid credentials.')
        if user.status == 'suspended':
            raise serializers.ValidationError('Your account has been suspended.')
        attrs['user'] = user
        return attrs


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, validators=[validate_password])

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('Old password is incorrect.')
        return value

    def save(self):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user


class PublicUserSerializer(serializers.ModelSerializer):
    """Minimal safe serializer for public-facing user display (peer chat etc.)."""
    class Meta:
        model = User
        fields = ['id', 'display_name', 'is_anonymous']
