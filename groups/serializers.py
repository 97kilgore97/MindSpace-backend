from rest_framework import serializers
from .models import SupportGroup, ChatMessage


class SupportGroupSerializer(serializers.ModelSerializer):
    member_count   = serializers.SerializerMethodField()
    latest_message = serializers.SerializerMethodField()

    class Meta:
        model  = SupportGroup
        fields = ['id', 'name', 'description', 'member_count', 'latest_message', 'created_at']

    def get_member_count(self, obj):
        return obj.members.count()

    def get_latest_message(self, obj):
        msg = obj.messages.order_by('-created_at').first()
        if msg:
            return {'content': msg.text[:60], 'sent_at': msg.created_at}
        return None


class ChatMessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.SerializerMethodField()

    class Meta:
        model  = ChatMessage
        fields = ['id', 'sender', 'sender_name', 'group', 'text', 'is_anonymous', 'created_at']
        read_only_fields = ['id', 'sender', 'created_at']

    def get_sender_name(self, obj):
        if obj.is_anonymous or not obj.sender:
            return 'Anonymous'
        return obj.sender.display_name

    def create(self, validated_data):
        validated_data['sender'] = self.context['request'].user
        return super().create(validated_data)