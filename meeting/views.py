"""
Views for Meeting Scheduler API.

This module provides ViewSets for Meeting CRUD operations with filtering,
error handling, and proper HTTP status codes.

Requirements: 1.1, 2.1, 2.2, 2.3, 2.4, 5.1, 5.2, 5.3, 5.4, 5.5, 7.1, 7.5
"""
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError, NotFound
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import IntegrityError
from .models import Meeting, Participant
from .serializers import MeetingSerializer, ParticipantSerializer
from .services import ConflictDetector, ICSGenerator


class MeetingViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Meeting CRUD operations.
    
    Provides:
    - list: GET /api/meetings/ - List all meetings with optional date filtering
    - create: POST /api/meetings/ - Create a new meeting
    - retrieve: GET /api/meetings/{id}/ - Get a specific meeting
    - update: PUT /api/meetings/{id}/ - Update a meeting
    - partial_update: PATCH /api/meetings/{id}/ - Partially update a meeting
    - destroy: DELETE /api/meetings/{id}/ - Delete a meeting
    
    Requirements: 1.1, 5.1, 5.2, 5.3, 5.4, 5.5, 7.1, 7.5
    """
    queryset = Meeting.objects.all().prefetch_related('participants')
    serializer_class = MeetingSerializer
    
    def get_queryset(self):
        """
        Filter meetings by date range if provided.
        
        Query parameters:
        - start_date: Filter meetings starting on or after this date (ISO format)
        - end_date: Filter meetings starting on or before this date (ISO format)
        
        Requirement: 5.5 - Date range filtering
        """
        from datetime import datetime
        from django.utils.dateparse import parse_datetime
        
        queryset = super().get_queryset()
        
        # Get date range parameters
        start_date = self.request.query_params.get('start_date', None)
        end_date = self.request.query_params.get('end_date', None)
        
        # Apply filters if provided
        if start_date:
            try:
                # Try Django's parse_datetime first
                parsed_start = parse_datetime(start_date)
                
                # If that fails, try Python's fromisoformat
                if parsed_start is None:
                    parsed_start = datetime.fromisoformat(start_date)
                
                if parsed_start is None:
                    raise ValueError("Could not parse datetime")
                
                queryset = queryset.filter(start_time__gte=parsed_start)
            except (ValueError, DjangoValidationError, TypeError) as e:
                raise ValidationError({
                    'start_date': f'Invalid date format. Please use ISO 8601 format (e.g., 2025-12-01T10:00:00+00:00)'
                })
        
        if end_date:
            try:
                # Try Django's parse_datetime first
                parsed_end = parse_datetime(end_date)
                
                # If that fails, try Python's fromisoformat
                if parsed_end is None:
                    parsed_end = datetime.fromisoformat(end_date)
                
                queryset = queryset.filter(start_time__lte=parsed_end)
            except (ValueError, DjangoValidationError, TypeError) as e:
                raise ValidationError({
                    'end_date': f'Invalid date format. Please use ISO 8601 format (e.g., 2025-12-01T10:00:00+00:00)'
                })
        
        return queryset
    
    def list(self, request, *args, **kwargs):
        """
        List all meetings with optional date range filtering.
        
        Requirements: 5.4, 5.5
        """
        try:
            return super().list(request, *args, **kwargs)
        except ValidationError:
            raise
        except Exception as e:
            return Response(
                {
                    'error': 'Internal server error',
                    'details': 'An unexpected error occurred while retrieving meetings'
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def create(self, request, *args, **kwargs):
        """
        Create a new meeting.
        
        Requirements: 1.1, 7.5
        """
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED,
                headers=headers
            )
        except ValidationError:
            raise
        except DjangoValidationError as e:
            return Response(
                {
                    'error': 'Validation failed',
                    'details': e.message_dict if hasattr(e, 'message_dict') else str(e)
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {
                    'error': 'Internal server error',
                    'details': 'An unexpected error occurred while creating the meeting'
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve a specific meeting by ID.
        
        Requirements: 5.1, 7.1
        """
        from django.http import Http404
        
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        except Http404:
            return Response(
                {
                    'error': 'Not found',
                    'details': 'Meeting with the specified ID does not exist'
                },
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {
                    'error': 'Internal server error',
                    'details': 'An unexpected error occurred while retrieving the meeting'
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def update(self, request, *args, **kwargs):
        """
        Update a meeting (full update).
        
        Requirements: 5.2, 7.1, 7.5
        """
        from django.http import Http404
        
        try:
            partial = kwargs.pop('partial', False)
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            
            if getattr(instance, '_prefetched_objects_cache', None):
                instance._prefetched_objects_cache = {}
            
            return Response(serializer.data)
        except Http404:
            return Response(
                {
                    'error': 'Not found',
                    'details': 'Meeting with the specified ID does not exist'
                },
                status=status.HTTP_404_NOT_FOUND
            )
        except ValidationError:
            raise
        except DjangoValidationError as e:
            return Response(
                {
                    'error': 'Validation failed',
                    'details': e.message_dict if hasattr(e, 'message_dict') else str(e)
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {
                    'error': 'Internal server error',
                    'details': 'An unexpected error occurred while updating the meeting'
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def partial_update(self, request, *args, **kwargs):
        """
        Partially update a meeting (PATCH).
        
        Requirements: 5.2, 7.1, 7.5
        """
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        """
        Delete a meeting and all associated participants.
        
        Requirements: 5.3, 7.1
        """
        from django.http import Http404
        
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Http404:
            return Response(
                {
                    'error': 'Not found',
                    'details': 'Meeting with the specified ID does not exist'
                },
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {
                    'error': 'Internal server error',
                    'details': 'An unexpected error occurred while deleting the meeting'
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'], url_path='participants')
    def add_participant(self, request, pk=None):
        """
        Add a participant to a meeting.
        
        POST /api/meetings/{id}/participants/
        
        Request body:
        {
            "email": "participant@example.com",
            "name": "Participant Name"
        }
        
        Requirements: 2.1, 2.2, 2.4
        """
        from django.http import Http404
        from django.db import transaction
        
        try:
            # Get the meeting
            meeting = self.get_object()
            
            # Validate participant data
            serializer = ParticipantSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            # Create participant with meeting association
            # Use atomic block to handle IntegrityError properly
            try:
                with transaction.atomic():
                    participant = Participant.objects.create(
                        meeting=meeting,
                        email=serializer.validated_data['email'],
                        name=serializer.validated_data['name']
                    )
                
                # Return the created participant
                response_serializer = ParticipantSerializer(participant)
                return Response(
                    response_serializer.data,
                    status=status.HTTP_201_CREATED
                )
            
            except IntegrityError:
                # Duplicate participant (unique constraint violation)
                # Requirement: 2.2 - Prevent duplicate participants
                return Response(
                    {
                        'error': 'Conflict',
                        'details': f'Participant with email {serializer.validated_data["email"]} is already added to this meeting'
                    },
                    status=status.HTTP_409_CONFLICT
                )
        
        except Http404:
            return Response(
                {
                    'error': 'Not found',
                    'details': 'Meeting with the specified ID does not exist'
                },
                status=status.HTTP_404_NOT_FOUND
            )
        except ValidationError:
            raise
        except Exception as e:
            return Response(
                {
                    'error': 'Internal server error',
                    'details': 'An unexpected error occurred while adding the participant'
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['get'], url_path='conflicts')
    def check_conflicts(self, request, pk=None):
        """
        Check for scheduling conflicts for all participants in a meeting.
        
        GET /api/meetings/{id}/conflicts/
        
        Returns a list of conflicts for each participant.
        
        This is a test/utility endpoint for verifying conflict detection.
        Requirements: 3.1, 3.2, 3.4
        """
        from django.http import Http404
        
        try:
            # Get the meeting
            meeting = self.get_object()
            
            # Get all conflicts
            conflicts = ConflictDetector.get_all_conflicts(meeting)
            
            # Format the response
            response_data = {
                'meeting_id': str(meeting.id),
                'meeting_title': meeting.title,
                'has_conflicts': len(conflicts) > 0,
                'conflicts': {}
            }
            
            # Add conflict details for each participant
            for email, conflicting_meetings in conflicts.items():
                response_data['conflicts'][email] = [
                    {
                        'id': str(m.id),
                        'title': m.title,
                        'start_time': m.start_time.isoformat(),
                        'end_time': m.end_time.isoformat()
                    }
                    for m in conflicting_meetings
                ]
            
            return Response(response_data, status=status.HTTP_200_OK)
        
        except Http404:
            return Response(
                {
                    'error': 'Not found',
                    'details': 'Meeting with the specified ID does not exist'
                },
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {
                    'error': 'Internal server error',
                    'details': 'An unexpected error occurred while checking conflicts'
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['get'], url_path='check-conflicts')
    def check_conflicts(self, request, pk=None):
        """
        Check for scheduling conflicts for all participants in a meeting.
        
        GET /api/meetings/{id}/check-conflicts/
        
        Returns:
        {
            "has_conflicts": true/false,
            "conflicts": {
                "participant@example.com": [
                    {
                        "id": "uuid",
                        "title": "Conflicting Meeting",
                        "start_time": "...",
                        "end_time": "..."
                    }
                ]
            }
        }
        
        Requirements: 3.1, 3.2, 3.4 (Temporary endpoint for testing)
        """
        from django.http import Http404
        
        try:
            # Get the meeting
            meeting = self.get_object()
            
            # Get all conflicts
            conflicts_dict = ConflictDetector.get_all_conflicts(meeting)
            
            # Format conflicts for response
            formatted_conflicts = {}
            for email, conflicting_meetings in conflicts_dict.items():
                formatted_conflicts[email] = [
                    {
                        'id': str(m.id),
                        'title': m.title,
                        'description': m.description,
                        'start_time': m.start_time.isoformat(),
                        'end_time': m.end_time.isoformat()
                    }
                    for m in conflicting_meetings
                ]
            
            return Response({
                'has_conflicts': len(conflicts_dict) > 0,
                'conflicts': formatted_conflicts
            })
        
        except Http404:
            return Response(
                {
                    'error': 'Not found',
                    'details': 'Meeting with the specified ID does not exist'
                },
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {
                    'error': 'Internal server error',
                    'details': 'An unexpected error occurred while checking conflicts'
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['get'], url_path='export')
    def export(self, request, pk=None):
        """
        Export meeting as ICS (iCalendar) file.
        
        GET /api/meetings/{id}/export/
        
        Returns an ICS file that can be imported into calendar applications.
        
        Requirement: 4.1 - Export meeting as ICS file
        """
        from django.http import HttpResponse, Http404
        
        try:
            # Get the meeting
            meeting = self.get_object()
            
            # Generate ICS content
            ics_content = ICSGenerator.generate_ics(meeting)
            
            # Create HTTP response with proper headers
            response = HttpResponse(
                ics_content,
                content_type='text/calendar; charset=utf-8'
            )
            
            # Set Content-Disposition header for file download
            # Use meeting title for filename (sanitize it)
            filename = f"{meeting.title.replace(' ', '_')}.ics"
            # Remove any characters that might cause issues in filenames
            filename = ''.join(c for c in filename if c.isalnum() or c in ('_', '-', '.'))
            
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            
            return response
        
        except Http404:
            return Response(
                {
                    'error': 'Not found',
                    'details': 'Meeting with the specified ID does not exist'
                },
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {
                    'error': 'Internal server error',
                    'details': 'An unexpected error occurred while exporting the meeting'
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['get'], url_path='export')
    def export_ics(self, request, pk=None):
        """
        Export meeting as ICS file.
        
        GET /api/meetings/{id}/export/
        
        Returns an ICS (iCalendar) file that can be imported into calendar applications.
        
        Requirements: 4.1
        """
        from django.http import HttpResponse, Http404
        
        try:
            # Get the meeting
            meeting = self.get_object()
            
            # Generate ICS content
            ics_content = ICSGenerator.generate_ics(meeting)
            
            # Create HTTP response with proper headers
            response = HttpResponse(ics_content, content_type='text/calendar')
            
            # Set Content-Disposition header for file download
            # Use meeting title in filename (sanitize for filesystem)
            safe_title = "".join(c for c in meeting.title if c.isalnum() or c in (' ', '-', '_')).strip()
            safe_title = safe_title.replace(' ', '_')
            filename = f"{safe_title}_{meeting.id}.ics"
            
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            
            return response
        
        except Http404:
            return Response(
                {
                    'error': 'Not found',
                    'details': 'Meeting with the specified ID does not exist'
                },
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {
                    'error': 'Internal server error',
                    'details': 'An unexpected error occurred while exporting the meeting'
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['delete'], url_path='participants/(?P<participant_email>[^/]+)')
    def remove_participant(self, request, pk=None, participant_email=None):
        """
        Remove a participant from a meeting.
        
        DELETE /api/meetings/{id}/participants/{email}/
        
        Requirements: 2.3, 2.4
        """
        from django.http import Http404
        from urllib.parse import unquote
        
        try:
            # Get the meeting
            meeting = self.get_object()
            
            # Decode the email from URL
            decoded_email = unquote(participant_email) if participant_email else None
            
            if not decoded_email:
                return Response(
                    {
                        'error': 'Bad request',
                        'details': 'Email parameter is required'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Find and delete the participant
            try:
                participant = Participant.objects.get(
                    meeting=meeting,
                    email=decoded_email
                )
                participant.delete()
                
                return Response(status=status.HTTP_204_NO_CONTENT)
            
            except Participant.DoesNotExist:
                return Response(
                    {
                        'error': 'Not found',
                        'details': f'Participant with email {decoded_email} not found in this meeting'
                    },
                    status=status.HTTP_404_NOT_FOUND
                )
        
        except Http404:
            return Response(
                {
                    'error': 'Not found',
                    'details': 'Meeting with the specified ID does not exist'
                },
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {
                    'error': 'Internal server error',
                    'details': 'An unexpected error occurred while removing the participant'
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )



class ParticipantViewSet(viewsets.ViewSet):
    """
    ViewSet for Participant query operations.
    
    Provides:
    - meetings: GET /api/participants/{email}/meetings/ - Get all meetings for a participant
    - conflicts: GET /api/participants/{email}/conflicts/ - Check conflicts for a participant
    
    Requirements: 6.1, 6.2, 6.3, 6.4
    """
    
    def meetings(self, request, email=None):
        """
        Get all meetings for a specific participant.
        
        GET /api/participants/{email}/meetings/
        
        Query parameters:
        - start_date: Filter meetings starting on or after this date (ISO format)
        - end_date: Filter meetings starting on or before this date (ISO format)
        
        Requirements: 6.1, 6.2, 6.3, 6.4
        """
        from datetime import datetime
        from django.utils.dateparse import parse_datetime
        from urllib.parse import unquote
        
        try:
            # Decode email from URL
            decoded_email = unquote(email) if email else None
            
            if not decoded_email:
                return Response(
                    {
                        'error': 'Bad request',
                        'details': 'Email parameter is required'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Get all meetings where this participant is involved
            # Requirement: 6.1 - Return all meetings for participant
            meetings = Meeting.objects.filter(
                participants__email=decoded_email
            ).distinct()
            
            # Apply date range filters if provided
            # Requirement: 6.4 - Date range filtering
            start_date = request.query_params.get('start_date', None)
            end_date = request.query_params.get('end_date', None)
            
            if start_date:
                try:
                    parsed_start = parse_datetime(start_date)
                    if parsed_start is None:
                        parsed_start = datetime.fromisoformat(start_date)
                    meetings = meetings.filter(start_time__gte=parsed_start)
                except (ValueError, TypeError) as e:
                    return Response(
                        {
                            'error': 'Bad request',
                            'details': 'Invalid start_date format. Please use ISO 8601 format'
                        },
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            if end_date:
                try:
                    parsed_end = parse_datetime(end_date)
                    if parsed_end is None:
                        parsed_end = datetime.fromisoformat(end_date)
                    meetings = meetings.filter(start_time__lte=parsed_end)
                except (ValueError, TypeError) as e:
                    return Response(
                        {
                            'error': 'Bad request',
                            'details': 'Invalid end_date format. Please use ISO 8601 format'
                        },
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            # Order chronologically by start time
            # Requirement: 6.2 - Chronological ordering
            meetings = meetings.order_by('start_time')
            
            # Serialize the meetings
            serializer = MeetingSerializer(meetings, many=True)
            
            return Response(serializer.data)
        
        except Exception as e:
            return Response(
                {
                    'error': 'Internal server error',
                    'details': 'An unexpected error occurred while retrieving participant meetings'
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def conflicts(self, request, email=None):
        """
        Check conflicts for a specific participant.
        
        GET /api/participants/{email}/conflicts/
        
        Query parameters:
        - start_date: Filter conflicts starting on or after this date (ISO format)
        - end_date: Filter conflicts starting on or before this date (ISO format)
        
        Returns all meetings where this participant has scheduling conflicts.
        
        Requirements: 6.1, 6.2, 6.4
        """
        from datetime import datetime
        from django.utils.dateparse import parse_datetime
        from urllib.parse import unquote
        
        try:
            # Decode email from URL
            decoded_email = unquote(email) if email else None
            
            if not decoded_email:
                return Response(
                    {
                        'error': 'Bad request',
                        'details': 'Email parameter is required'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Get all meetings where this participant is involved
            meetings = Meeting.objects.filter(
                participants__email=decoded_email
            ).distinct()
            
            # Apply date range filters if provided
            # Requirement: 6.4 - Date range filtering
            start_date = request.query_params.get('start_date', None)
            end_date = request.query_params.get('end_date', None)
            
            if start_date:
                try:
                    parsed_start = parse_datetime(start_date)
                    if parsed_start is None:
                        parsed_start = datetime.fromisoformat(start_date)
                    meetings = meetings.filter(start_time__gte=parsed_start)
                except (ValueError, TypeError) as e:
                    return Response(
                        {
                            'error': 'Bad request',
                            'details': 'Invalid start_date format. Please use ISO 8601 format'
                        },
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            if end_date:
                try:
                    parsed_end = parse_datetime(end_date)
                    if parsed_end is None:
                        parsed_end = datetime.fromisoformat(end_date)
                    meetings = meetings.filter(start_time__lte=parsed_end)
                except (ValueError, TypeError) as e:
                    return Response(
                        {
                            'error': 'Bad request',
                            'details': 'Invalid end_date format. Please use ISO 8601 format'
                        },
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            # Order chronologically
            # Requirement: 6.2 - Chronological ordering
            meetings = meetings.order_by('start_time')
            
            # Find conflicts for each meeting
            conflicts_list = []
            
            for meeting in meetings:
                # Check if this meeting has conflicts with other meetings for this participant
                conflicting_meetings = ConflictDetector.check_participant_conflicts(
                    decoded_email,
                    meeting,
                    exclude_meeting_id=meeting.id
                )
                
                if conflicting_meetings.exists():
                    # This meeting has conflicts
                    conflicts_list.append({
                        'meeting': MeetingSerializer(meeting).data,
                        'conflicting_with': MeetingSerializer(conflicting_meetings, many=True).data
                    })
            
            return Response({
                'participant_email': decoded_email,
                'has_conflicts': len(conflicts_list) > 0,
                'conflicts': conflicts_list
            })
        
        except Exception as e:
            return Response(
                {
                    'error': 'Internal server error',
                    'details': 'An unexpected error occurred while checking participant conflicts'
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
