"""
URL configuration for meeting app.

This module defines the URL patterns for the Meeting Scheduler API endpoints.

Requirements: 1.1, 5.1, 5.2, 5.3, 5.4, 5.5, 6.1, 6.2, 6.3, 6.4
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MeetingViewSet, ParticipantViewSet

# Create a router and register our viewsets
router = DefaultRouter()
router.register(r'meetings', MeetingViewSet, basename='meeting')

# Participant endpoints (custom URLs)
participant_meetings = ParticipantViewSet.as_view({'get': 'meetings'})
participant_conflicts = ParticipantViewSet.as_view({'get': 'conflicts'})

# The API URLs are determined automatically by the router
urlpatterns = [
    path('', include(router.urls)),
    path('participants/<str:email>/meetings/', participant_meetings, name='participant-meetings'),
    path('participants/<str:email>/conflicts/', participant_conflicts, name='participant-conflicts'),
]
