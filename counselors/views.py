from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Counselor, Session, TimeSlot
from .serializers import (
    CounselorSerializer, SessionSerializer, TimeSlotSerializer,
    BookSessionSerializer, SessionUpdateSerializer
)
from core.permissions import IsAdminOrModerator, IsCounselorOrAdmin
from core.sms import send_session_confirmation_sms


class CounselorListView(generics.ListAPIView):
    """GET /api/counselors/ — list all verified counselors."""
    serializer_class = CounselorSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        qs = Counselor.objects.filter(is_verified=True)
        status_filter = self.request.query_params.get('status')
        if status_filter:
            qs = qs.filter(status=status_filter)
        return qs.order_by('-rating')


class CounselorDetailView(generics.RetrieveAPIView):
    """GET /api/counselors/<id>/ — single counselor profile."""
    serializer_class = CounselorSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    queryset = Counselor.objects.filter(is_verified=True)


class CounselorTimeSlotsView(generics.ListAPIView):
    """GET /api/counselors/<id>/slots/ — available booking slots."""
    serializer_class = TimeSlotSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return TimeSlot.objects.filter(
            counselor_id=self.kwargs['pk'],
            is_booked=False
        ).order_by('start_time')


class BookSessionView(APIView):
    """POST /api/counselors/book/ — book a session with a counselor."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = BookSessionSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        session = serializer.save()

        # Send SMS confirmation if user has a phone number
        phone = getattr(request.user.profile, 'phone', None)
        if phone:
            send_session_confirmation_sms(
                phone=phone,
                counselor_name=session.counselor.full_name,
                scheduled_at=session.scheduled_at,
            )

        return Response(
            SessionSerializer(session).data,
            status=status.HTTP_201_CREATED
        )


class MySessionsView(generics.ListAPIView):
    """GET /api/counselors/my-sessions/ — user's own sessions."""
    serializer_class = SessionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Session.objects.filter(
            user=self.request.user
        ).select_related('counselor').order_by('-scheduled_at')


class SessionDetailView(generics.RetrieveUpdateAPIView):
    """GET/PATCH /api/counselors/sessions/<id>/ — view or update a session."""
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'PATCH':
            return SessionUpdateSerializer
        return SessionSerializer

    def get_queryset(self):
        user = self.request.user
        if user.role in ['admin', 'counselor', 'moderator']:
            return Session.objects.all()
        return Session.objects.filter(user=user)


class CancelSessionView(APIView):
    """POST /api/counselors/sessions/<id>/cancel/ — cancel a booked session."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        try:
            session = Session.objects.get(pk=pk, user=request.user)
            if session.status == 'completed':
                return Response(
                    {'error': 'Cannot cancel a completed session.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            session.status = 'cancelled'
            session.save(update_fields=['status'])

            # Free the slot back up
            TimeSlot.objects.filter(
                counselor=session.counselor,
                start_time=session.scheduled_at
            ).update(is_booked=False)

            return Response({'message': 'Session cancelled.'})
        except Session.DoesNotExist:
            return Response({'error': 'Session not found.'}, status=status.HTTP_404_NOT_FOUND)


# ─── Admin views ──────────────────────────────────────────

class AdminCounselorManageView(generics.ListCreateAPIView):
    """GET/POST /api/counselors/admin/ — admin: list & onboard counselors."""
    serializer_class = CounselorSerializer
    permission_classes = [IsAdminOrModerator]
    queryset = Counselor.objects.all().order_by('-created_at')


@api_view(['POST'])
@permission_classes([IsAdminOrModerator])
def set_counselor_status(request, pk):
    """POST /api/counselors/<id>/status/ — admin: toggle counselor availability."""
    try:
        counselor = Counselor.objects.get(pk=pk)
        new_status = request.data.get('status')
        if new_status not in ['online', 'busy', 'offline']:
            return Response({'error': 'Invalid status.'}, status=status.HTTP_400_BAD_REQUEST)
        counselor.status = new_status
        counselor.save(update_fields=['status'])
        return Response({'message': f'{counselor.full_name} is now {new_status}.'})
    except Counselor.DoesNotExist:
        return Response({'error': 'Counselor not found.'}, status=status.HTTP_404_NOT_FOUND)


class AllSessionsView(generics.ListAPIView):
    """GET /api/counselors/admin/sessions/ — admin: all sessions."""
    serializer_class = SessionSerializer
    permission_classes = [IsAdminOrModerator]
    queryset = Session.objects.all().select_related('user', 'counselor').order_by('-created_at')
