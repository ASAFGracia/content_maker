from django.contrib import admin
from .models import User, Project, Task, Meeting, MeetingParticipant


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_active']
    list_filter = ['is_active', 'is_staff']
    search_fields = ['username', 'email']


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'owner', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['name', 'description']


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'assignee', 'status', 'priority', 'due_date']
    list_filter = ['status', 'priority', 'created_at']
    search_fields = ['title', 'description']


@admin.register(Meeting)
class MeetingAdmin(admin.ModelAdmin):
    list_display = ['title', 'organizer', 'start_time', 'end_time']
    list_filter = ['start_time']
    search_fields = ['title', 'description']


@admin.register(MeetingParticipant)
class MeetingParticipantAdmin(admin.ModelAdmin):
    list_display = ['meeting', 'user', 'status']
    list_filter = ['status']

