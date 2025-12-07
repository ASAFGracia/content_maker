from rest_framework import serializers
from .models import User, Project, Task, Meeting, MeetingParticipant


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'is_active']
        read_only_fields = ['id']


class ProjectSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)
    owner_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = Project
        fields = ['id', 'name', 'description', 'owner', 'owner_id', 'status', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class TaskSerializer(serializers.ModelSerializer):
    assignee = UserSerializer(read_only=True)
    assignee_id = serializers.UUIDField(write_only=True, required=False, allow_null=True)
    creator = UserSerializer(read_only=True)
    project = ProjectSerializer(read_only=True)
    project_id = serializers.UUIDField(write_only=True, required=False, allow_null=True)

    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'project', 'project_id', 'assignee', 'assignee_id',
                  'creator', 'status', 'priority', 'due_date', 'created_at', 'updated_at']
        read_only_fields = ['id', 'creator', 'created_at', 'updated_at']


class MeetingParticipantSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = MeetingParticipant
        fields = ['id', 'user', 'status']


class MeetingSerializer(serializers.ModelSerializer):
    organizer = UserSerializer(read_only=True)
    participants = MeetingParticipantSerializer(many=True, read_only=True)
    participant_ids = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True,
        required=False
    )

    class Meta:
        model = Meeting
        fields = ['id', 'title', 'description', 'organizer', 'start_time', 'end_time',
                  'location', 'participants', 'participant_ids', 'created_at', 'updated_at']
        read_only_fields = ['id', 'organizer', 'created_at', 'updated_at']

