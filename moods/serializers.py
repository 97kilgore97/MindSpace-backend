from rest_framework import serializers
from .models import MoodLog, JournalEntry


class MoodLogSerializer(serializers.ModelSerializer):
    class Meta:
        model  = MoodLog
        fields = ['id', 'score', 'note', 'logged_at']
        read_only_fields = ['id', 'logged_at']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class JournalEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model  = JournalEntry
        fields = ['id', 'content', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class MoodSummarySerializer(serializers.Serializer):
    average_score  = serializers.FloatField()
    total_entries  = serializers.IntegerField()
    streak_days    = serializers.IntegerField()
    weekly         = serializers.ListField(child=serializers.DictField())