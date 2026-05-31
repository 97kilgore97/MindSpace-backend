from rest_framework import serializers
from .models import Counselor, Session, TimeSlot


class CounselorSerializer(serializers.ModelSerializer):
    status_display = serializers.SerializerMethodField()
    available_slots_count = serializers.SerializerMethodField()

    class Meta:
        model = Counselor
        fields = [
            'id', 'full_name', 'specialization', 'bio', 'status',
            'status_display', 'sessions_count', 'rating', 'is_verified',
            'available_slots_count', 'created_at'
        ]
        read_only_fields = ['id', 'sessions_count', 'rating', 'created_at']

    def get_status_display(self, obj):
        return {'online': 'Online', 'busy': 'In session', 'offline': 'Offline'}.get(obj.status, obj.status)

    def get_available_slots_count(self, obj):
        return TimeSlot.objects.filter(counselor=obj, is_booked=False).count()


class TimeSlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimeSlot
        fields = ['id', 'counselor', 'start_time', 'end_time', 'is_booked']
        read_only_fields = ['id', 'is_booked']


class SessionSerializer(serializers.ModelSerializer):
    counselor_name = serializers.CharField(source='counselor.full_name', read_only=True)
    user_name = serializers.CharField(source='user.display_name', read_only=True)

    class Meta:
        model = Session
        fields = [
            'id', 'user', 'user_name', 'counselor', 'counselor_name',
            'scheduled_at', 'duration_mins', 'status', 'notes', 'created_at'
        ]
        read_only_fields = ['id', 'user', 'status', 'created_at']


class BookSessionSerializer(serializers.Serializer):
    """Validates a booking request — counselor + time slot."""
    counselor_id = serializers.UUIDField()
    slot_id = serializers.UUIDField()
    notes = serializers.CharField(required=False, allow_blank=True, max_length=500)

    def validate(self, attrs):
        try:
            counselor = Counselor.objects.get(id=attrs['counselor_id'], is_verified=True)
        except Counselor.DoesNotExist:
            raise serializers.ValidationError({'counselor_id': 'Counselor not found or not verified.'})

        try:
            slot = TimeSlot.objects.get(id=attrs['slot_id'], counselor=counselor, is_booked=False)
        except TimeSlot.DoesNotExist:
            raise serializers.ValidationError({'slot_id': 'Time slot not available.'})

        attrs['counselor'] = counselor
        attrs['slot'] = slot
        return attrs

    def create(self, validated_data):
        user = self.context['request'].user
        counselor = validated_data['counselor']
        slot = validated_data['slot']

        session = Session.objects.create(
            user=user,
            counselor=counselor,
            scheduled_at=slot.start_time,
            notes=validated_data.get('notes', ''),
            status='confirmed',
        )
        slot.is_booked = True
        slot.save(update_fields=['is_booked'])

        counselor.sessions_count += 1
        counselor.save(update_fields=['sessions_count'])

        return session


class SessionUpdateSerializer(serializers.ModelSerializer):
    """Counselor/admin update a session status or add notes."""
    class Meta:
        model = Session
        fields = ['status', 'notes']
