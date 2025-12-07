from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from django.utils import timezone
from django.shortcuts import render
from .models import User, Project, Task, Meeting, MeetingParticipant
from .serializers import (
    UserSerializer, ProjectSerializer, TaskSerializer,
    MeetingSerializer, MeetingParticipantSerializer
)


class IndexView(APIView):
    """Главная страница"""
    permission_classes = [AllowAny]
    
    def get(self, request):
        return render(request, 'index.html')


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]


class ProjectViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Project.objects.filter(owner=user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        status_filter = self.request.query_params.get('status', None)
        queryset = Task.objects.filter(assignee=user) | Task.objects.filter(creator=user)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        return queryset.distinct()

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)

    @action(detail=True, methods=['post'])
    def change_status(self, request, pk=None):
        task = self.get_object()
        new_status = request.data.get('status')
        if new_status in dict(Task.STATUS_CHOICES):
            task.status = new_status
            task.save()
            return Response({'status': 'success'})
        return Response({'error': 'Invalid status'}, status=status.HTTP_400_BAD_REQUEST)


class MeetingViewSet(viewsets.ModelViewSet):
    serializer_class = MeetingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Meeting.objects.filter(participants__user=user) | Meeting.objects.filter(organizer=user)

    def perform_create(self, serializer):
        meeting = serializer.save(organizer=self.request.user)
        participant_ids = self.request.data.get('participant_ids', [])
        for user_id in participant_ids:
            MeetingParticipant.objects.create(
                meeting=meeting,
                user_id=user_id,
                status='pending'
            )

    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        meetings = self.get_queryset().filter(start_time__gte=timezone.now())
        serializer = self.get_serializer(meetings, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def respond(self, request, pk=None):
        meeting = self.get_object()
        response_status = request.data.get('status', 'accepted')
        participant, created = MeetingParticipant.objects.get_or_create(
            meeting=meeting,
            user=request.user
        )
        participant.status = response_status
        participant.save()
        return Response({'status': 'success'})
