# ── serializers.py ────────────────────────────────────────
from rest_framework import serializers
from .models import ChatRoom, ChatMessage
from users.serializers import PublicUserSerializer


class ChatMessageSerializer(serializers.ModelSerializer):
    sender = PublicUserSerializer(read_only=True)

    class Meta:
        model = ChatMessage
        fields = ['id', 'room', 'sender', 'content', 'is_flagged', 'sent_at']
        read_only_fields = ['id', 'sender', 'is_flagged', 'sent_at']

    def create(self, validated_data):
        validated_data['sender'] = self.context['request'].user
        message = super().create(validated_data)
        # Run safety check after save
        from core.safety import check_message_safety
        check_message_safety(message)
        return message


class ChatRoomSerializer(serializers.ModelSerializer):
    member_count = serializers.SerializerMethodField()
    latest_message = serializers.SerializerMethodField()

    class Meta:
        model = ChatRoom
        fields = ['id', 'name', 'type', 'is_active', 'member_count', 'latest_message', 'created_at']
        read_only_fields = ['id', 'created_at']

    def get_member_count(self, obj):
        return obj.members.count()

    def get_latest_message(self, obj):
        msg = obj.messages.order_by('-sent_at').first()
        if msg:
            return {'content': msg.content[:60], 'sent_at': msg.sent_at}
        return None


# ── views.py ──────────────────────────────────────────────
from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import ChatRoom, ChatMessage
from core.permissions import IsAdminOrModerator


class ChatRoomListView(generics.ListAPIView):
    """GET /api/groups/ — list all active peer support rooms."""
    serializer_class = ChatRoomSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ChatRoom.objects.filter(is_active=True).order_by('name')


class ChatRoomDetailView(generics.RetrieveAPIView):
    """GET /api/groups/<id>/ — room info."""
    serializer_class = ChatRoomSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = ChatRoom.objects.filter(is_active=True)


class JoinRoomView(APIView):
    """POST /api/groups/<id>/join/ — join a peer support room."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        try:
            room = ChatRoom.objects.get(pk=pk, is_active=True)
            room.members.add(request.user)
            return Response({'message': f'Joined {room.name}.'})
        except ChatRoom.DoesNotExist:
            return Response({'error': 'Room not found.'}, status=status.HTTP_404_NOT_FOUND)


class LeaveRoomView(APIView):
    """POST /api/groups/<id>/leave/"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        try:
            room = ChatRoom.objects.get(pk=pk)
            room.members.remove(request.user)
            return Response({'message': 'Left room.'})
        except ChatRoom.DoesNotExist:
            return Response({'error': 'Room not found.'}, status=status.HTTP_404_NOT_FOUND)


class RoomMessageListView(generics.ListCreateAPIView):
    """GET  /api/groups/<id>/messages/ — fetch message history
       POST /api/groups/<id>/messages/ — post a message (REST fallback; WS preferred)"""
    serializer_class = ChatMessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ChatMessage.objects.filter(
            room_id=self.kwargs['pk'],
            is_flagged=False
        ).select_related('sender').order_by('sent_at')

    def perform_create(self, serializer):
        serializer.save(room_id=self.kwargs['pk'])


# ── Admin moderation ──────────────────────────────────────

class FlaggedMessagesView(generics.ListAPIView):
    """GET /api/groups/flagged/ — moderation queue."""
    serializer_class = ChatMessageSerializer
    permission_classes = [IsAdminOrModerator]

    def get_queryset(self):
        return ChatMessage.objects.filter(
            is_flagged=True
        ).select_related('sender', 'room').order_by('-sent_at')


@api_view(['POST'])
@permission_classes([IsAdminOrModerator])
def resolve_flag(request, pk):
    """POST /api/groups/messages/<id>/resolve/ — dismiss or escalate a flag."""
    try:
        msg = ChatMessage.objects.get(pk=pk)
        action = request.data.get('action')  # 'dismiss' or 'escalate'
        if action == 'dismiss':
            msg.is_flagged = False
            msg.save(update_fields=['is_flagged'])
            return Response({'message': 'Flag dismissed.'})
        elif action == 'escalate':
            from core.crisis import escalate_crisis
            escalate_crisis(user=msg.sender, source='chat', source_id=msg.id, trigger_text=msg.content)
            return Response({'message': 'Escalated to crisis team.'})
        return Response({'error': 'action must be dismiss or escalate.'}, status=400)
    except ChatMessage.DoesNotExist:
        return Response({'error': 'Message not found.'}, status=404)


# ── urls.py ───────────────────────────────────────────────
from django.urls import path
import groups.views as gv

urlpatterns = [
    path('',                                        gv.ChatRoomListView.as_view(),      name='room-list'),
    path('<uuid:pk>/',                              gv.ChatRoomDetailView.as_view(),    name='room-detail'),
    path('<uuid:pk>/join/',                         gv.JoinRoomView.as_view(),          name='room-join'),
    path('<uuid:pk>/leave/',                        gv.LeaveRoomView.as_view(),         name='room-leave'),
    path('<uuid:pk>/messages/',                     gv.RoomMessageListView.as_view(),   name='room-messages'),
    path('flagged/',                                gv.FlaggedMessagesView.as_view(),   name='flagged-messages'),
    path('messages/<uuid:pk>/resolve/',             gv.resolve_flag,                    name='resolve-flag'),
]
