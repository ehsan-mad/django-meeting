"""
Service classes for Meeting Scheduler business logic.

This module provides service classes for conflict detection and other
business logic operations.

Requirements: 3.1, 3.2, 3.4, 4.1, 4.2, 4.4, 4.5
"""
from django.db.models import Q
from django.utils import timezone as django_timezone
from .models import Meeting, Participant
from icalendar import Calendar, Event, vCalAddress, vText
from datetime import datetime, timezone


class ConflictDetector:
    """
    Service class for detecting scheduling conflicts between meetings.
    
    Provides methods to:
    - Check if two meetings have overlapping time ranges
    - Find conflicts for a specific participant
    - Find all conflicts for all participants in a meeting
    
    Requirements: 3.1, 3.2, 3.4
    """
    
    @staticmethod
    def detect_time_overlap(meeting1, meeting2):
        """
        Determine if two meetings have overlapping time ranges.
        
        Two meetings overlap if their time intervals intersect:
        - Meeting A: [start_A, end_A]
        - Meeting B: [start_B, end_B]
        - Overlap exists if: start_A < end_B AND start_B < end_A
        
        Args:
            meeting1: First Meeting object or dict with start_time and end_time
            meeting2: Second Meeting object or dict with start_time and end_time
        
        Returns:
            bool: True if meetings overlap, False otherwise
        
        Requirement: 3.2 - Time overlap detection logic
        """
        # Handle both Meeting objects and dicts
        start1 = meeting1.start_time if hasattr(meeting1, 'start_time') else meeting1['start_time']
        end1 = meeting1.end_time if hasattr(meeting1, 'end_time') else meeting1['end_time']
        start2 = meeting2.start_time if hasattr(meeting2, 'start_time') else meeting2['start_time']
        end2 = meeting2.end_time if hasattr(meeting2, 'end_time') else meeting2['end_time']
        
        # Check for overlap: start_A < end_B AND start_B < end_A
        return start1 < end2 and start2 < end1
    
    @staticmethod
    def check_participant_conflicts(participant_email, meeting, exclude_meeting_id=None):
        """
        Find all meetings that conflict with the given meeting for a specific participant.
        
        Args:
            participant_email (str): Email of the participant to check
            meeting: Meeting object or dict with start_time and end_time
            exclude_meeting_id (UUID, optional): Meeting ID to exclude from conflict check
                                                  (useful when updating existing meetings)
        
        Returns:
            QuerySet: Meetings that conflict with the given meeting for this participant
        
        Requirements: 3.1, 3.2 - Participant conflict detection
        """
        # Get start and end times
        start_time = meeting.start_time if hasattr(meeting, 'start_time') else meeting['start_time']
        end_time = meeting.end_time if hasattr(meeting, 'end_time') else meeting['end_time']
        
        # Find all meetings where this participant is involved
        participant_meetings = Meeting.objects.filter(
            participants__email=participant_email
        )
        
        # Exclude the current meeting if specified (for update scenarios)
        if exclude_meeting_id:
            participant_meetings = participant_meetings.exclude(id=exclude_meeting_id)
        
        # Find overlapping meetings using database-level filtering
        # Overlap condition: start_time < other_end_time AND other_start_time < end_time
        conflicting_meetings = participant_meetings.filter(
            Q(start_time__lt=end_time) & Q(end_time__gt=start_time)
        )
        
        return conflicting_meetings
    
    @staticmethod
    def get_all_conflicts(meeting):
        """
        Find all conflicts for all participants in a meeting.
        
        Returns a dictionary mapping participant emails to their conflicting meetings.
        
        Args:
            meeting: Meeting object with participants
        
        Returns:
            dict: Dictionary with structure:
                {
                    'participant_email': [list of conflicting Meeting objects],
                    ...
                }
        
        Requirement: 3.4 - Complete conflict reporting for all participants
        """
        conflicts = {}
        
        # Get meeting ID to exclude from conflict checks
        meeting_id = meeting.id if hasattr(meeting, 'id') else None
        
        # Get all participants for this meeting
        participants = meeting.participants.all() if hasattr(meeting, 'participants') else []
        
        # Check conflicts for each participant
        for participant in participants:
            conflicting_meetings = ConflictDetector.check_participant_conflicts(
                participant.email,
                meeting,
                exclude_meeting_id=meeting_id
            )
            
            # Only include participants who have conflicts
            if conflicting_meetings.exists():
                conflicts[participant.email] = list(conflicting_meetings)
        
        return conflicts
    
    @staticmethod
    def has_conflicts(meeting):
        """
        Check if a meeting has any scheduling conflicts with its participants.
        
        Args:
            meeting: Meeting object with participants
        
        Returns:
            bool: True if any participant has conflicts, False otherwise
        """
        conflicts = ConflictDetector.get_all_conflicts(meeting)
        return len(conflicts) > 0



class ICSGenerator:
    """
    Service class for generating RFC 5545 compliant ICS (iCalendar) files.
    
    Provides methods to:
    - Convert Meeting model to iCalendar event
    - Format participant data as ATTENDEE fields
    - Generate complete ICS file content
    
    Requirements: 4.1, 4.2, 4.4, 4.5
    """
    
    @staticmethod
    def create_calendar_event(meeting):
        """
        Create an iCalendar event from a Meeting object.
        
        Args:
            meeting: Meeting object with all fields populated
        
        Returns:
            Event: iCalendar Event object
        
        Requirement: 4.2 - Convert Meeting model to iCalendar event
        """
        event = Event()
        
        # Add unique identifier
        event.add('uid', str(meeting.id))
        
        # Add meeting title as SUMMARY
        event.add('summary', meeting.title)
        
        # Add description if present
        if meeting.description:
            event.add('description', meeting.description)
        
        # Add start and end times with UTC timezone
        # Requirement: 4.5 - Proper timezone handling (UTC)
        utc = timezone.utc
        
        # Ensure times are timezone-aware and in UTC
        start_time = meeting.start_time
        end_time = meeting.end_time
        
        if start_time.tzinfo is None:
            start_time = start_time.replace(tzinfo=utc)
        else:
            start_time = start_time.astimezone(utc)
        
        if end_time.tzinfo is None:
            end_time = end_time.replace(tzinfo=utc)
        else:
            end_time = end_time.astimezone(utc)
        
        event.add('dtstart', start_time)
        event.add('dtend', end_time)
        
        # Add timestamps
        created_at = meeting.created_at
        if created_at.tzinfo is None:
            created_at = created_at.replace(tzinfo=utc)
        else:
            created_at = created_at.astimezone(utc)
        
        event.add('dtstamp', created_at)
        event.add('created', created_at)
        
        updated_at = meeting.updated_at
        if updated_at.tzinfo is None:
            updated_at = updated_at.replace(tzinfo=utc)
        else:
            updated_at = updated_at.astimezone(utc)
        
        event.add('last-modified', updated_at)
        
        return event
    
    @staticmethod
    def format_attendees(participants):
        """
        Format participant data as ATTENDEE fields per RFC 5545.
        
        Args:
            participants: QuerySet or list of Participant objects
        
        Returns:
            list: List of vCalAddress objects formatted as ATTENDEE fields
        
        Requirement: 4.4 - Format participant data as ATTENDEE fields per RFC 5545
        """
        attendees = []
        
        for participant in participants:
            # Create calendar address for the participant
            attendee = vCalAddress(f'MAILTO:{participant.email}')
            
            # Add common name (CN) parameter
            attendee.params['cn'] = vText(participant.name)
            
            # Add role parameter (REQ-PARTICIPANT is standard for required attendees)
            attendee.params['role'] = vText('REQ-PARTICIPANT')
            
            # Add RSVP parameter (request response)
            attendee.params['rsvp'] = vText('TRUE')
            
            attendees.append(attendee)
        
        return attendees
    
    @staticmethod
    def generate_ics(meeting):
        """
        Generate complete ICS file content for a meeting.
        
        Args:
            meeting: Meeting object with participants
        
        Returns:
            bytes: ICS file content as bytes
        
        Requirements: 4.1, 4.2, 4.4, 4.5
        """
        # Create calendar
        cal = Calendar()
        
        # Add required calendar properties
        cal.add('prodid', '-//Meeting Scheduler//Meeting Scheduler API//EN')
        cal.add('version', '2.0')
        cal.add('calscale', 'GREGORIAN')
        cal.add('method', 'PUBLISH')
        
        # Create event from meeting
        event = ICSGenerator.create_calendar_event(meeting)
        
        # Add attendees to event
        # Requirement: 4.4 - Format participant data as ATTENDEE fields
        participants = meeting.participants.all() if hasattr(meeting, 'participants') else []
        attendees = ICSGenerator.format_attendees(participants)
        
        for attendee in attendees:
            event.add('attendee', attendee, encode=0)
        
        # Add event to calendar
        cal.add_component(event)
        
        # Generate ICS content
        # Requirement: 4.5 - Follow RFC 5545 iCalendar format standards
        ics_content = cal.to_ical()
        
        return ics_content
