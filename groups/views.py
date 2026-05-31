from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import SupportGroup, ChatMessage
from .serializers import SupportGroupSerializer, ChatMessageSerializer


class SupportGroupListView(generics.ListAPIView):
    serializer_class   = SupportGroupSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset           = SupportGroup.objects.all().order_by('name')


class JoinGroupView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        try:
            group = SupportGroup.objects.get(pk=pk)
            group.members.add(request.user)
            return Response({'message': f'Joined {group.name}.'})
        except SupportGroup.DoesNotExist:
            return Response({'error': 'Group not found.'}, status=404)


class LeaveGroupView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        try:
            group = SupportGroup.objects.get(pk=pk)
            group.members.remove(request.user)
            return Response({'message': 'Left group.'})
        except SupportGroup.DoesNotExist:
            return Response({'error': 'Group not found.'}, status=404)


class GroupMessageListView(generics.ListCreateAPIView):
    serializer_class   = ChatMessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ChatMessage.objects.filter(
            group_id=self.kwargs['pk']
        ).select_related('sender').order_by('created_at')

    def perform_create(self, serializer):
        serializer.save(group_id=self.kwargs['pk'])