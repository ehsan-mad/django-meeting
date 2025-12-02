"""
Tests for Meeting Scheduler API.

This module contains tests for the Meeting CRUD API endpoints.
"""
from django.test import TestCase
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.utils import timezone
from datetime import timedelta, datetime
from .models import Meeting, Participant
from .services import ConflictDetector
import json


class MeetingCRUDTestCase(APITestCase):
    """
    Test case for Meeting CRUD operations.
    
    Tests Requirements: 1.1, 5.1, 5.2, 5.3, 5.4, 5.5, 7.1, 7.5
    """
    
    def setUp(self):
        """Set up test client and sample data."""
        self.client = APIClient()
        self.base_url = '/api/meetings/'
        
        # Create sample meeting data
        self.now = timezone.now()
        self.valid_meeting_data = {
            'title': 'Test Meeting',
            'description': 'Test Description',
            'start_time': (self.now + timedelta(hours=1)).isoformat(),
            'end_time': (self.now + timedelta(hours=2)).isoformat(),
        }
    
    def test_create_meeting_success(self):
        """
        Test creating a meeting with valid data.
        Requirement: 1.1
        """
        response = self.client.post(
            self.base_url,
            data=json.dumps(self.valid_meeting_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('id', response.data)
        self.assertEqual(response.data['title'], 'Test Meeting')
        self.assertEqual(response.data['description'], 'Test Description')
    
    def test_create_meeting_invalid_time_range(self):
        """
        Test creating a meeting with end_time before start_time.
        Requirement: 1.2
        """
        invalid_data = self.valid_meeting_data.copy()
        invalid_data['end_time'] = (self.now - timedelta(hours=1)).isoformat()
        
        response = self.client.post(
            self.base_url,
            data=json.dumps(invalid_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('end_time', str(response.data))
    
    def test_create_meeting_missing_required_fields(self):
        """
        Test creating a meeting with missing required fields.
        Requirement: 1.3
        """
        invalid_data = {'description': 'Only description'}
        
        response = self.client.post(
            self.base_url,
            data=json.dumps(invalid_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_retrieve_meeting(self):
        """
        Test retrieving a specific meeting by ID.
        Requirement: 5.1
        """
        # Create a meeting first
        meeting = Meeting.objects.create(
            title='Test Meeting',
            description='Test Description',
            start_time=self.now + timedelta(hours=1),
            end_time=self.now + timedelta(hours=2)
        )
        
        response = self.client.get(f'{self.base_url}{meeting.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], str(meeting.id))
        self.assertEqual(response.data['title'], 'Test Meeting')
    
    def test_retrieve_nonexistent_meeting(self):
        """
        Test retrieving a meeting that doesn't exist.
        Requirement: 7.1
        """
        fake_uuid = '00000000-0000-0000-0000-000000000000'
        response = self.client.get(f'{self.base_url}{fake_uuid}/')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('error', response.data)
    
    def test_update_meeting(self):
        """
        Test updating a meeting.
        Requirement: 5.2
        """
        # Create a meeting first
        meeting = Meeting.objects.create(
            title='Original Title',
            description='Original Description',
            start_time=self.now + timedelta(hours=1),
            end_time=self.now + timedelta(hours=2)
        )
        
        update_data = {
            'title': 'Updated Title',
            'description': 'Updated Description',
            'start_time': (self.now + timedelta(hours=3)).isoformat(),
            'end_time': (self.now + timedelta(hours=4)).isoformat(),
        }
        
        response = self.client.put(
            f'{self.base_url}{meeting.id}/',
            data=json.dumps(update_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Updated Title')
        self.assertEqual(response.data['description'], 'Updated Description')
    
    def test_delete_meeting(self):
        """
        Test deleting a meeting.
        Requirement: 5.3
        """
        # Create a meeting first
        meeting = Meeting.objects.create(
            title='Test Meeting',
            description='Test Description',
            start_time=self.now + timedelta(hours=1),
            end_time=self.now + timedelta(hours=2)
        )
        
        response = self.client.delete(f'{self.base_url}{meeting.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Verify the meeting is deleted
        self.assertFalse(Meeting.objects.filter(id=meeting.id).exists())
    
    def test_list_meetings(self):
        """
        Test listing all meetings.
        Requirement: 5.4
        """
        # Create multiple meetings
        Meeting.objects.create(
            title='Meeting 1',
            start_time=self.now + timedelta(hours=1),
            end_time=self.now + timedelta(hours=2)
        )
        Meeting.objects.create(
            title='Meeting 2',
            start_time=self.now + timedelta(hours=3),
            end_time=self.now + timedelta(hours=4)
        )
        
        response = self.client.get(self.base_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
    
    def test_list_meetings_with_date_filter(self):
        """
        Test listing meetings with date range filtering.
        Requirement: 5.5
        """
        # Create meetings at different times
        meeting1 = Meeting.objects.create(
            title='Meeting 1',
            start_time=self.now + timedelta(days=1),
            end_time=self.now + timedelta(days=1, hours=1)
        )
        meeting2 = Meeting.objects.create(
            title='Meeting 2',
            start_time=self.now + timedelta(days=5),
            end_time=self.now + timedelta(days=5, hours=1)
        )
        meeting3 = Meeting.objects.create(
            title='Meeting 3',
            start_time=self.now + timedelta(days=10),
            end_time=self.now + timedelta(days=10, hours=1)
        )
        
        # Filter for meetings in the first week
        # Use replace to ensure proper ISO format without microseconds
        from urllib.parse import quote
        start_date = (self.now).replace(microsecond=0).isoformat()
        end_date = (self.now + timedelta(days=7)).replace(microsecond=0).isoformat()
        
        # URL encode the dates to preserve the + sign
        response = self.client.get(
            f'{self.base_url}?start_date={quote(start_date)}&end_date={quote(end_date)}'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # Should only get meeting1 and meeting2


class ParticipantManagementTestCase(APITestCase):
    """
    Test case for Participant management operations.
    
    Tests Requirements: 2.1, 2.2, 2.3, 2.4
    """
    
    def setUp(self):
        """Set up test client and sample data."""
        self.client = APIClient()
        self.base_url = '/api/meetings/'
        
        # Create a sample meeting
        self.now = timezone.now()
        self.meeting = Meeting.objects.create(
            title='Test Meeting',
            description='Test Description',
            start_time=self.now + timedelta(hours=1),
            end_time=self.now + timedelta(hours=2)
        )
        
        self.valid_participant_data = {
            'email': 'participant@example.com',
            'name': 'Test Participant'
        }
    
    def test_add_participant_success(self):
        """
        Test adding a participant to a meeting.
        Requirement: 2.1
        """
        response = self.client.post(
            f'{self.base_url}{self.meeting.id}/participants/',
            data=json.dumps(self.valid_participant_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('id', response.data)
        self.assertEqual(response.data['email'], 'participant@example.com')
        self.assertEqual(response.data['name'], 'Test Participant')
        
        # Verify participant is in database
        self.assertTrue(
            Participant.objects.filter(
                meeting=self.meeting,
                email='participant@example.com'
            ).exists()
        )
    
    def test_add_duplicate_participant(self):
        """
        Test adding the same participant twice to prevent duplicates.
        Requirement: 2.2
        """
        # Add participant first time
        response1 = self.client.post(
            f'{self.base_url}{self.meeting.id}/participants/',
            data=json.dumps(self.valid_participant_data),
            content_type='application/json'
        )
        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)
        
        # Try to add the same participant again
        response2 = self.client.post(
            f'{self.base_url}{self.meeting.id}/participants/',
            data=json.dumps(self.valid_participant_data),
            content_type='application/json'
        )
        
        self.assertEqual(response2.status_code, status.HTTP_409_CONFLICT)
        self.assertIn('error', response2.data)
        
        # Verify only one participant exists
        count = Participant.objects.filter(
            meeting=self.meeting,
            email='participant@example.com'
        ).count()
        self.assertEqual(count, 1)
    
    def test_remove_participant_success(self):
        """
        Test removing a participant from a meeting.
        Requirement: 2.3
        """
        # Add a participant first
        participant = Participant.objects.create(
            meeting=self.meeting,
            email='participant@example.com',
            name='Test Participant'
        )
        
        # Remove the participant
        from urllib.parse import quote
        response = self.client.delete(
            f'{self.base_url}{self.meeting.id}/participants/{quote("participant@example.com")}/'
        )
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Verify participant is removed
        self.assertFalse(
            Participant.objects.filter(
                meeting=self.meeting,
                email='participant@example.com'
            ).exists()
        )
        
        # Verify meeting still exists (data integrity)
        self.assertTrue(Meeting.objects.filter(id=self.meeting.id).exists())
    
    def test_remove_nonexistent_participant(self):
        """
        Test removing a participant that doesn't exist.
        Requirement: 2.3
        """
        from urllib.parse import quote
        response = self.client.delete(
            f'{self.base_url}{self.meeting.id}/participants/{quote("nonexistent@example.com")}/'
        )
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('error', response.data)
    
    def test_participant_list_in_meeting_detail(self):
        """
        Test that participant list is included in meeting detail response.
        Requirement: 2.4
        """
        # Add participants to the meeting
        Participant.objects.create(
            meeting=self.meeting,
            email='participant1@example.com',
            name='Participant 1'
        )
        Participant.objects.create(
            meeting=self.meeting,
            email='participant2@example.com',
            name='Participant 2'
        )
        
        # Retrieve the meeting
        response = self.client.get(f'{self.base_url}{self.meeting.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('participants', response.data)
        self.assertEqual(len(response.data['participants']), 2)
        
        # Verify participant details are included
        emails = [p['email'] for p in response.data['participants']]
        self.assertIn('participant1@example.com', emails)
        self.assertIn('participant2@example.com', emails)
    
    def test_add_participant_to_nonexistent_meeting(self):
        """
        Test adding a participant to a meeting that doesn't exist.
        Requirement: 7.1
        """
        fake_uuid = '00000000-0000-0000-0000-000000000000'
        response = self.client.post(
            f'{self.base_url}{fake_uuid}/participants/',
            data=json.dumps(self.valid_participant_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('error', response.data)
    
    def test_participant_independence_across_meetings(self):
        """
        Test that the same participant can be added to multiple meetings independently.
        Requirement: 2.5
        """
        # Create another meeting
        meeting2 = Meeting.objects.create(
            title='Second Meeting',
            description='Second Description',
            start_time=self.now + timedelta(hours=3),
            end_time=self.now + timedelta(hours=4)
        )
        
        # Add same participant to both meetings
        self.client.post(
            f'{self.base_url}{self.meeting.id}/participants/',
            data=json.dumps(self.valid_participant_data),
            content_type='application/json'
        )
        self.client.post(
            f'{self.base_url}{meeting2.id}/participants/',
            data=json.dumps(self.valid_participant_data),
            content_type='application/json'
        )
        
        # Verify participant exists in both meetings
        self.assertTrue(
            Participant.objects.filter(
                meeting=self.meeting,
                email='participant@example.com'
            ).exists()
        )
        self.assertTrue(
            Participant.objects.filter(
                meeting=meeting2,
                email='participant@example.com'
            ).exists()
        )
        
        # Remove participant from first meeting
        from urllib.parse import quote
        self.client.delete(
            f'{self.base_url}{self.meeting.id}/participants/{quote("participant@example.com")}/'
        )
        
        # Verify participant is removed from first meeting but still in second
        self.assertFalse(
            Participant.objects.filter(
                meeting=self.meeting,
                email='participant@example.com'
            ).exists()
        )
        self.assertTrue(
            Participant.objects.filter(
                meeting=meeting2,
                email='participant@example.com'
            ).exists()
        )



class ConflictDetectorTestCase(TestCase):
    """
    Test case for ConflictDetector service.
    
    Tests Requirements: 3.1, 3.2, 3.4
    """
    
    def setUp(self):
        """Set up test data."""
        self.now = timezone.now()
        
        # Create test meetings
        self.meeting1 = Meeting.objects.create(
            title='Meeting 1',
            description='First meeting',
            start_time=self.now + timedelta(hours=1),
            end_time=self.now + timedelta(hours=2)
        )
        
        self.meeting2 = Meeting.objects.create(
            title='Meeting 2',
            description='Second meeting - overlaps with meeting 1',
            start_time=self.now + timedelta(hours=1, minutes=30),
            end_time=self.now + timedelta(hours=2, minutes=30)
        )
        
        self.meeting3 = Meeting.objects.create(
            title='Meeting 3',
            description='Third meeting - no overlap',
            start_time=self.now + timedelta(hours=3),
            end_time=self.now + timedelta(hours=4)
        )
        
        # Create participants
        self.participant1 = Participant.objects.create(
            meeting=self.meeting1,
            email='alice@example.com',
            name='Alice'
        )
        
        self.participant2 = Participant.objects.create(
            meeting=self.meeting2,
            email='alice@example.com',
            name='Alice'
        )
        
        self.participant3 = Participant.objects.create(
            meeting=self.meeting3,
            email='bob@example.com',
            name='Bob'
        )
    
    def test_detect_time_overlap_with_overlap(self):
        """
        Test detecting overlap between two meetings that do overlap.
        Requirement: 3.2
        """
        has_overlap = ConflictDetector.detect_time_overlap(self.meeting1, self.meeting2)
        self.assertTrue(has_overlap)
    
    def test_detect_time_overlap_without_overlap(self):
        """
        Test detecting overlap between two meetings that don't overlap.
        Requirement: 3.2
        """
        has_overlap = ConflictDetector.detect_time_overlap(self.meeting1, self.meeting3)
        self.assertFalse(has_overlap)
    
    def test_detect_time_overlap_adjacent_meetings(self):
        """
        Test that adjacent meetings (end time = start time) don't overlap.
        Requirement: 3.2
        """
        meeting_a = Meeting.objects.create(
            title='Meeting A',
            start_time=self.now + timedelta(hours=5),
            end_time=self.now + timedelta(hours=6)
        )
        meeting_b = Meeting.objects.create(
            title='Meeting B',
            start_time=self.now + timedelta(hours=6),
            end_time=self.now + timedelta(hours=7)
        )
        
        has_overlap = ConflictDetector.detect_time_overlap(meeting_a, meeting_b)
        self.assertFalse(has_overlap)
    
    def test_detect_time_overlap_with_dict(self):
        """
        Test overlap detection with dictionary inputs.
        Requirement: 3.2
        """
        meeting_dict1 = {
            'start_time': self.now + timedelta(hours=1),
            'end_time': self.now + timedelta(hours=2)
        }
        meeting_dict2 = {
            'start_time': self.now + timedelta(hours=1, minutes=30),
            'end_time': self.now + timedelta(hours=2, minutes=30)
        }
        
        has_overlap = ConflictDetector.detect_time_overlap(meeting_dict1, meeting_dict2)
        self.assertTrue(has_overlap)
    
    def test_check_participant_conflicts_with_conflicts(self):
        """
        Test finding conflicts for a participant who has overlapping meetings.
        Requirement: 3.1
        """
        # Alice is in both meeting1 and meeting2, which overlap
        # Exclude meeting1 to check for conflicts with other meetings
        conflicts = ConflictDetector.check_participant_conflicts(
            'alice@example.com',
            self.meeting1,
            exclude_meeting_id=self.meeting1.id
        )
        
        # Should find meeting2 as a conflict
        self.assertEqual(conflicts.count(), 1)
        self.assertIn(self.meeting2, conflicts)
    
    def test_check_participant_conflicts_without_conflicts(self):
        """
        Test finding conflicts for a participant with no overlapping meetings.
        Requirement: 3.1
        """
        # Bob is only in meeting3, which doesn't overlap with anything
        # Exclude meeting3 to check for conflicts with other meetings
        conflicts = ConflictDetector.check_participant_conflicts(
            'bob@example.com',
            self.meeting3,
            exclude_meeting_id=self.meeting3.id
        )
        
        self.assertEqual(conflicts.count(), 0)
    
    def test_check_participant_conflicts_exclude_meeting(self):
        """
        Test that we can exclude a specific meeting from conflict check.
        Requirement: 3.1
        """
        # Check conflicts for alice in meeting1, excluding meeting1 itself
        conflicts = ConflictDetector.check_participant_conflicts(
            'alice@example.com',
            self.meeting1,
            exclude_meeting_id=self.meeting1.id
        )
        
        # Should still find meeting2 as a conflict
        self.assertEqual(conflicts.count(), 1)
        self.assertIn(self.meeting2, conflicts)
    
    def test_check_participant_conflicts_new_participant(self):
        """
        Test checking conflicts for a participant not yet in any meetings.
        Requirement: 3.1
        """
        conflicts = ConflictDetector.check_participant_conflicts(
            'charlie@example.com',
            self.meeting1
        )
        
        # Charlie has no meetings, so no conflicts
        self.assertEqual(conflicts.count(), 0)
    
    def test_get_all_conflicts_with_conflicts(self):
        """
        Test getting all conflicts for all participants in a meeting.
        Requirement: 3.4
        """
        conflicts = ConflictDetector.get_all_conflicts(self.meeting1)
        
        # Alice should have conflicts (meeting2)
        self.assertIn('alice@example.com', conflicts)
        self.assertEqual(len(conflicts['alice@example.com']), 1)
        self.assertIn(self.meeting2, conflicts['alice@example.com'])
    
    def test_get_all_conflicts_without_conflicts(self):
        """
        Test getting conflicts when no conflicts exist.
        Requirement: 3.4
        """
        conflicts = ConflictDetector.get_all_conflicts(self.meeting3)
        
        # Bob has no conflicts
        self.assertEqual(len(conflicts), 0)
    
    def test_get_all_conflicts_multiple_participants(self):
        """
        Test getting conflicts for a meeting with multiple participants.
        Requirement: 3.4
        """
        # Create a meeting that overlaps with meeting1
        meeting_overlap = Meeting.objects.create(
            title='Overlapping Meeting',
            description='Overlaps with meeting 1',
            start_time=self.now + timedelta(hours=1, minutes=15),
            end_time=self.now + timedelta(hours=2, minutes=15)
        )
        
        # Add Bob to both meeting1 and the overlapping meeting
        Participant.objects.create(
            meeting=self.meeting1,
            email='bob@example.com',
            name='Bob'
        )
        Participant.objects.create(
            meeting=meeting_overlap,
            email='bob@example.com',
            name='Bob'
        )
        
        conflicts = ConflictDetector.get_all_conflicts(self.meeting1)
        
        # Alice should have conflicts (meeting2)
        self.assertIn('alice@example.com', conflicts)
        
        # Bob should have conflicts (meeting_overlap)
        self.assertIn('bob@example.com', conflicts)
        self.assertEqual(len(conflicts['bob@example.com']), 1)
        self.assertIn(meeting_overlap, conflicts['bob@example.com'])
    
    def test_has_conflicts_true(self):
        """
        Test has_conflicts returns True when conflicts exist.
        Requirement: 3.1
        """
        has_conflicts = ConflictDetector.has_conflicts(self.meeting1)
        self.assertTrue(has_conflicts)
    
    def test_has_conflicts_false(self):
        """
        Test has_conflicts returns False when no conflicts exist.
        Requirement: 3.1
        """
        has_conflicts = ConflictDetector.has_conflicts(self.meeting3)
        self.assertFalse(has_conflicts)
    
    def test_conflict_detection_with_meeting_update(self):
        """
        Test conflict detection when updating a meeting's time.
        Requirement: 3.3 (from design doc)
        """
        # Create a new meeting that doesn't conflict initially
        meeting4 = Meeting.objects.create(
            title='Meeting 4',
            start_time=self.now + timedelta(hours=10),
            end_time=self.now + timedelta(hours=11)
        )
        
        # Add Alice to meeting4
        Participant.objects.create(
            meeting=meeting4,
            email='alice@example.com',
            name='Alice'
        )
        
        # Initially no conflicts
        conflicts = ConflictDetector.get_all_conflicts(meeting4)
        self.assertEqual(len(conflicts), 0)
        
        # Update meeting4 to overlap with meeting1
        meeting4.start_time = self.now + timedelta(hours=1, minutes=15)
        meeting4.end_time = self.now + timedelta(hours=2, minutes=15)
        meeting4.save()
        
        # Now should have conflicts
        conflicts = ConflictDetector.get_all_conflicts(meeting4)
        self.assertIn('alice@example.com', conflicts)
        self.assertGreater(len(conflicts['alice@example.com']), 0)
    
    def test_conflict_detection_same_start_different_end(self):
        """
        Test overlap detection for meetings with same start time but different end times.
        Requirement: 3.2
        """
        meeting_a = Meeting.objects.create(
            title='Meeting A',
            start_time=self.now + timedelta(hours=20),
            end_time=self.now + timedelta(hours=21)
        )
        meeting_b = Meeting.objects.create(
            title='Meeting B',
            start_time=self.now + timedelta(hours=20),
            end_time=self.now + timedelta(hours=22)
        )
        
        has_overlap = ConflictDetector.detect_time_overlap(meeting_a, meeting_b)
        self.assertTrue(has_overlap)
    
    def test_conflict_detection_one_meeting_contains_another(self):
        """
        Test overlap detection when one meeting completely contains another.
        Requirement: 3.2
        """
        meeting_outer = Meeting.objects.create(
            title='Outer Meeting',
            start_time=self.now + timedelta(hours=30),
            end_time=self.now + timedelta(hours=33)
        )
        meeting_inner = Meeting.objects.create(
            title='Inner Meeting',
            start_time=self.now + timedelta(hours=31),
            end_time=self.now + timedelta(hours=32)
        )
        
        has_overlap = ConflictDetector.detect_time_overlap(meeting_outer, meeting_inner)
        self.assertTrue(has_overlap)



class ConflictEndpointTestCase(APITestCase):
    """
    Test case for the conflicts endpoint.
    
    Tests the GET /api/meetings/{id}/conflicts/ endpoint.
    """
    
    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.base_url = '/api/meetings/'
        self.now = timezone.now()
        
        # Create meetings
        self.meeting1 = Meeting.objects.create(
            title='Meeting 1',
            start_time=self.now + timedelta(hours=1),
            end_time=self.now + timedelta(hours=2)
        )
        
        self.meeting2 = Meeting.objects.create(
            title='Meeting 2',
            start_time=self.now + timedelta(hours=1, minutes=30),
            end_time=self.now + timedelta(hours=2, minutes=30)
        )
        
        # Add participants
        Participant.objects.create(
            meeting=self.meeting1,
            email='alice@example.com',
            name='Alice'
        )
        
        Participant.objects.create(
            meeting=self.meeting2,
            email='alice@example.com',
            name='Alice'
        )
    
    def test_check_conflicts_endpoint_with_conflicts(self):
        """Test the conflicts endpoint when conflicts exist."""
        response = self.client.get(f'{self.base_url}{self.meeting1.id}/check-conflicts/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('has_conflicts', response.data)
        self.assertIn('conflicts', response.data)
        
        # Should have conflicts
        self.assertTrue(response.data['has_conflicts'])
        self.assertIn('alice@example.com', response.data['conflicts'])
        
        # Check conflict details
        alice_conflicts = response.data['conflicts']['alice@example.com']
        self.assertEqual(len(alice_conflicts), 1)
        self.assertEqual(alice_conflicts[0]['id'], str(self.meeting2.id))
    
    def test_check_conflicts_endpoint_without_conflicts(self):
        """Test the conflicts endpoint when no conflicts exist."""
        meeting3 = Meeting.objects.create(
            title='Meeting 3',
            start_time=self.now + timedelta(hours=5),
            end_time=self.now + timedelta(hours=6)
        )
        
        Participant.objects.create(
            meeting=meeting3,
            email='bob@example.com',
            name='Bob'
        )
        
        response = self.client.get(f'{self.base_url}{meeting3.id}/check-conflicts/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['has_conflicts'])
        self.assertEqual(len(response.data['conflicts']), 0)
    
    def test_check_conflicts_endpoint_nonexistent_meeting(self):
        """Test the conflicts endpoint with non-existent meeting."""
        fake_uuid = '00000000-0000-0000-0000-000000000000'
        response = self.client.get(f'{self.base_url}{fake_uuid}/check-conflicts/')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('error', response.json())



class ParticipantQueryTestCase(APITestCase):
    """
    Test case for Participant query endpoints.
    
    Tests Requirements: 6.1, 6.2, 6.3, 6.4
    """
    
    def setUp(self):
        """Set up test client and sample data."""
        self.client = APIClient()
        self.now = timezone.now()
        
        # Create test meetings
        self.meeting1 = Meeting.objects.create(
            title='Meeting 1',
            description='First meeting',
            start_time=self.now + timedelta(hours=1),
            end_time=self.now + timedelta(hours=2)
        )
        
        self.meeting2 = Meeting.objects.create(
            title='Meeting 2',
            description='Second meeting',
            start_time=self.now + timedelta(hours=3),
            end_time=self.now + timedelta(hours=4)
        )
        
        self.meeting3 = Meeting.objects.create(
            title='Meeting 3',
            description='Third meeting',
            start_time=self.now + timedelta(days=5),
            end_time=self.now + timedelta(days=5, hours=1)
        )
        
        # Create participants
        Participant.objects.create(
            meeting=self.meeting1,
            email='alice@example.com',
            name='Alice'
        )
        
        Participant.objects.create(
            meeting=self.meeting2,
            email='alice@example.com',
            name='Alice'
        )
        
        Participant.objects.create(
            meeting=self.meeting3,
            email='alice@example.com',
            name='Alice'
        )
        
        Participant.objects.create(
            meeting=self.meeting2,
            email='bob@example.com',
            name='Bob'
        )
    
    def test_get_participant_meetings(self):
        """
        Test getting all meetings for a participant.
        Requirement: 6.1
        """
        from urllib.parse import quote
        response = self.client.get(f'/api/participants/{quote("alice@example.com")}/meetings/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)
        
        # Verify all meetings are returned
        meeting_ids = [m['id'] for m in response.data]
        self.assertIn(str(self.meeting1.id), meeting_ids)
        self.assertIn(str(self.meeting2.id), meeting_ids)
        self.assertIn(str(self.meeting3.id), meeting_ids)
    
    def test_participant_meetings_chronological_order(self):
        """
        Test that participant meetings are ordered chronologically.
        Requirement: 6.2
        """
        from urllib.parse import quote
        response = self.client.get(f'/api/participants/{quote("alice@example.com")}/meetings/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify chronological ordering
        for i in range(len(response.data) - 1):
            current_start = datetime.fromisoformat(response.data[i]['start_time'].replace('Z', '+00:00'))
            next_start = datetime.fromisoformat(response.data[i + 1]['start_time'].replace('Z', '+00:00'))
            self.assertLessEqual(current_start, next_start)
    
    def test_participant_no_meetings(self):
        """
        Test getting meetings for a participant with no meetings.
        Requirement: 6.3
        """
        from urllib.parse import quote
        response = self.client.get(f'/api/participants/{quote("charlie@example.com")}/meetings/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)
    
    def test_participant_meetings_with_date_filter(self):
        """
        Test filtering participant meetings by date range.
        Requirement: 6.4
        """
        from urllib.parse import quote
        
        # Filter for meetings in the next 2 days
        start_date = self.now.replace(microsecond=0).isoformat()
        end_date = (self.now + timedelta(days=2)).replace(microsecond=0).isoformat()
        
        response = self.client.get(
            f'/api/participants/{quote("alice@example.com")}/meetings/?start_date={quote(start_date)}&end_date={quote(end_date)}'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should only get meeting1 and meeting2, not meeting3 (which is 5 days away)
        self.assertEqual(len(response.data), 2)
        
        meeting_ids = [m['id'] for m in response.data]
        self.assertIn(str(self.meeting1.id), meeting_ids)
        self.assertIn(str(self.meeting2.id), meeting_ids)
        self.assertNotIn(str(self.meeting3.id), meeting_ids)
    
    def test_check_participant_conflicts(self):
        """
        Test checking conflicts for a participant.
        Requirement: 6.1
        """
        # Create overlapping meeting
        meeting_overlap = Meeting.objects.create(
            title='Overlapping Meeting',
            description='Overlaps with meeting1',
            start_time=self.now + timedelta(hours=1, minutes=30),
            end_time=self.now + timedelta(hours=2, minutes=30)
        )
        
        Participant.objects.create(
            meeting=meeting_overlap,
            email='alice@example.com',
            name='Alice'
        )
        
        from urllib.parse import quote
        response = self.client.get(f'/api/participants/{quote("alice@example.com")}/conflicts/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('has_conflicts', response.data)
        self.assertIn('conflicts', response.data)
        self.assertTrue(response.data['has_conflicts'])
        
        # Should have at least one conflict
        self.assertGreater(len(response.data['conflicts']), 0)
    
    def test_participant_no_conflicts(self):
        """
        Test checking conflicts for a participant with no conflicts.
        Requirement: 6.1
        """
        from urllib.parse import quote
        response = self.client.get(f'/api/participants/{quote("bob@example.com")}/conflicts/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['has_conflicts'])
        self.assertEqual(len(response.data['conflicts']), 0)
    
    def test_participant_conflicts_chronological_order(self):
        """
        Test that participant conflicts are ordered chronologically.
        Requirement: 6.2
        """
        # Create multiple overlapping meetings
        meeting_overlap1 = Meeting.objects.create(
            title='Overlap 1',
            start_time=self.now + timedelta(hours=1, minutes=15),
            end_time=self.now + timedelta(hours=1, minutes=45)
        )
        
        meeting_overlap2 = Meeting.objects.create(
            title='Overlap 2',
            start_time=self.now + timedelta(hours=3, minutes=15),
            end_time=self.now + timedelta(hours=3, minutes=45)
        )
        
        Participant.objects.create(
            meeting=meeting_overlap1,
            email='alice@example.com',
            name='Alice'
        )
        
        Participant.objects.create(
            meeting=meeting_overlap2,
            email='alice@example.com',
            name='Alice'
        )
        
        from urllib.parse import quote
        response = self.client.get(f'/api/participants/{quote("alice@example.com")}/conflicts/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify conflicts are in chronological order
        if len(response.data['conflicts']) > 1:
            for i in range(len(response.data['conflicts']) - 1):
                current_start = datetime.fromisoformat(
                    response.data['conflicts'][i]['meeting']['start_time'].replace('Z', '+00:00')
                )
                next_start = datetime.fromisoformat(
                    response.data['conflicts'][i + 1]['meeting']['start_time'].replace('Z', '+00:00')
                )
                self.assertLessEqual(current_start, next_start)
    
    def test_participant_conflicts_with_date_filter(self):
        """
        Test filtering participant conflicts by date range.
        Requirement: 6.4
        """
        # Create overlapping meetings at different times
        meeting_overlap_near = Meeting.objects.create(
            title='Near Overlap',
            start_time=self.now + timedelta(hours=1, minutes=30),
            end_time=self.now + timedelta(hours=2, minutes=30)
        )
        
        meeting_overlap_far = Meeting.objects.create(
            title='Far Overlap',
            start_time=self.now + timedelta(days=5, minutes=30),
            end_time=self.now + timedelta(days=5, hours=1, minutes=30)
        )
        
        Participant.objects.create(
            meeting=meeting_overlap_near,
            email='alice@example.com',
            name='Alice'
        )
        
        Participant.objects.create(
            meeting=meeting_overlap_far,
            email='alice@example.com',
            name='Alice'
        )
        
        from urllib.parse import quote
        
        # Filter for conflicts in the next 2 days
        start_date = self.now.replace(microsecond=0).isoformat()
        end_date = (self.now + timedelta(days=2)).replace(microsecond=0).isoformat()
        
        response = self.client.get(
            f'/api/participants/{quote("alice@example.com")}/conflicts/?start_date={quote(start_date)}&end_date={quote(end_date)}'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Should only include conflicts from the near future, not the far future
        # The far overlap (day 5) should be filtered out
        for conflict in response.data['conflicts']:
            meeting_start = datetime.fromisoformat(
                conflict['meeting']['start_time'].replace('Z', '+00:00')
            )
            self.assertLess(meeting_start, datetime.fromisoformat(end_date))
    
    def test_participant_meetings_invalid_email(self):
        """
        Test getting meetings with missing email parameter.
        """
        response = self.client.get('/api/participants//meetings/')
        
        # Should handle gracefully
        self.assertIn(response.status_code, [status.HTTP_400_BAD_REQUEST, status.HTTP_404_NOT_FOUND])
    
    def test_participant_meetings_invalid_date_format(self):
        """
        Test getting meetings with invalid date format.
        """
        from urllib.parse import quote
        response = self.client.get(
            f'/api/participants/{quote("alice@example.com")}/meetings/?start_date=invalid-date'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)



class ICSGeneratorTestCase(TestCase):
    """
    Test case for ICSGenerator service.
    
    Tests Requirements: 4.1, 4.2, 4.4, 4.5
    """
    
    def setUp(self):
        """Set up test data."""
        self.now = timezone.now()
        
        # Create test meeting
        self.meeting = Meeting.objects.create(
            title='Team Standup',
            description='Daily team standup meeting',
            start_time=self.now + timedelta(hours=1),
            end_time=self.now + timedelta(hours=2)
        )
        
        # Add participants
        self.participant1 = Participant.objects.create(
            meeting=self.meeting,
            email='alice@example.com',
            name='Alice Smith'
        )
        
        self.participant2 = Participant.objects.create(
            meeting=self.meeting,
            email='bob@example.com',
            name='Bob Johnson'
        )
    
    def test_create_calendar_event(self):
        """
        Test creating an iCalendar event from a Meeting object.
        Requirement: 4.2
        """
        from meeting.services import ICSGenerator
        
        event = ICSGenerator.create_calendar_event(self.meeting)
        
        # Verify event has required fields
        self.assertIsNotNone(event.get('uid'))
        self.assertEqual(str(event.get('uid')), str(self.meeting.id))
        self.assertEqual(str(event.get('summary')), self.meeting.title)
        self.assertEqual(str(event.get('description')), self.meeting.description)
        
        # Verify times are present
        self.assertIsNotNone(event.get('dtstart'))
        self.assertIsNotNone(event.get('dtend'))
        self.assertIsNotNone(event.get('dtstamp'))
    
    def test_create_calendar_event_without_description(self):
        """
        Test creating an event for a meeting without description.
        Requirement: 4.2
        """
        from meeting.services import ICSGenerator
        
        meeting_no_desc = Meeting.objects.create(
            title='Quick Meeting',
            description='',
            start_time=self.now + timedelta(hours=3),
            end_time=self.now + timedelta(hours=4)
        )
        
        event = ICSGenerator.create_calendar_event(meeting_no_desc)
        
        self.assertEqual(str(event.get('summary')), 'Quick Meeting')
        # Description should be empty or not present
        desc = event.get('description')
        self.assertTrue(desc is None or str(desc) == '')
    
    def test_format_attendees(self):
        """
        Test formatting participants as ATTENDEE fields per RFC 5545.
        Requirement: 4.4
        """
        from meeting.services import ICSGenerator
        
        participants = self.meeting.participants.all()
        attendees = ICSGenerator.format_attendees(participants)
        
        # Should have 2 attendees
        self.assertEqual(len(attendees), 2)
        
        # Check first attendee
        attendee1 = attendees[0]
        self.assertIn('MAILTO:', str(attendee1))
        self.assertIn('alice@example.com', str(attendee1))
        self.assertEqual(attendee1.params['cn'], 'Alice Smith')
        self.assertEqual(attendee1.params['role'], 'REQ-PARTICIPANT')
        self.assertEqual(attendee1.params['rsvp'], 'TRUE')
    
    def test_format_attendees_empty_list(self):
        """
        Test formatting attendees with empty participant list.
        Requirement: 4.4
        """
        from meeting.services import ICSGenerator
        
        attendees = ICSGenerator.format_attendees([])
        self.assertEqual(len(attendees), 0)
    
    def test_generate_ics(self):
        """
        Test generating complete ICS file content.
        Requirements: 4.1, 4.2, 4.4, 4.5
        """
        from meeting.services import ICSGenerator
        
        ics_content = ICSGenerator.generate_ics(self.meeting)
        
        # Should return bytes
        self.assertIsInstance(ics_content, bytes)
        
        # Convert to string for verification
        ics_str = ics_content.decode('utf-8')
        
        # Remove line folding (RFC 5545 allows lines to be split with \r\n followed by space)
        ics_str_unfolded = ics_str.replace('\r\n ', '').replace('\n ', '')
        
        # Verify ICS structure
        self.assertIn('BEGIN:VCALENDAR', ics_str)
        self.assertIn('END:VCALENDAR', ics_str)
        self.assertIn('BEGIN:VEVENT', ics_str)
        self.assertIn('END:VEVENT', ics_str)
        
        # Verify calendar properties
        self.assertIn('PRODID:-//Meeting Scheduler//Meeting Scheduler API//EN', ics_str)
        self.assertIn('VERSION:2.0', ics_str)
        self.assertIn('CALSCALE:GREGORIAN', ics_str)
        
        # Verify meeting details
        self.assertIn('SUMMARY:Team Standup', ics_str)
        self.assertIn('DESCRIPTION:Daily team standup meeting', ics_str)
        
        # Verify attendees (check in unfolded string due to line wrapping)
        self.assertIn('ATTENDEE', ics_str)
        self.assertIn('alice@example.com', ics_str_unfolded)
        self.assertIn('bob@example.com', ics_str_unfolded)
        self.assertIn('Alice Smith', ics_str)
        self.assertIn('Bob Johnson', ics_str)
    
    def test_generate_ics_without_participants(self):
        """
        Test generating ICS for a meeting without participants.
        Requirement: 4.1
        """
        from meeting.services import ICSGenerator
        
        meeting_no_participants = Meeting.objects.create(
            title='Solo Meeting',
            description='Meeting without participants',
            start_time=self.now + timedelta(hours=5),
            end_time=self.now + timedelta(hours=6)
        )
        
        ics_content = ICSGenerator.generate_ics(meeting_no_participants)
        ics_str = ics_content.decode('utf-8')
        
        # Should still have valid ICS structure
        self.assertIn('BEGIN:VCALENDAR', ics_str)
        self.assertIn('BEGIN:VEVENT', ics_str)
        self.assertIn('SUMMARY:Solo Meeting', ics_str)
    
    def test_ics_timezone_handling(self):
        """
        Test that ICS generation handles timezones correctly (UTC).
        Requirement: 4.5
        """
        from meeting.services import ICSGenerator
        
        ics_content = ICSGenerator.generate_ics(self.meeting)
        ics_str = ics_content.decode('utf-8')
        
        # Should contain UTC timezone indicators
        # ICS format uses Z suffix for UTC times or explicit timezone
        self.assertTrue('Z' in ics_str or 'UTC' in ics_str or 'TZID' in ics_str)
    
    def test_ics_round_trip_parsing(self):
        """
        Test that generated ICS can be parsed by icalendar library.
        Requirement: 4.5 - RFC 5545 compliance
        """
        from meeting.services import ICSGenerator
        from icalendar import Calendar
        
        ics_content = ICSGenerator.generate_ics(self.meeting)
        
        # Parse the generated ICS
        cal = Calendar.from_ical(ics_content)
        
        # Verify calendar properties
        self.assertEqual(cal.get('version'), '2.0')
        
        # Get the event
        events = [component for component in cal.walk() if component.name == 'VEVENT']
        self.assertEqual(len(events), 1)
        
        event = events[0]
        
        # Verify event properties
        self.assertEqual(str(event.get('summary')), self.meeting.title)
        self.assertEqual(str(event.get('description')), self.meeting.description)
        self.assertEqual(str(event.get('uid')), str(self.meeting.id))
        
        # Verify attendees
        attendees = event.get('attendee')
        if not isinstance(attendees, list):
            attendees = [attendees] if attendees else []
        
        self.assertEqual(len(attendees), 2)
    
    def test_ics_special_characters(self):
        """
        Test ICS generation with special characters in title and description.
        Requirement: 4.5 - RFC 5545 compliance
        """
        from meeting.services import ICSGenerator
        
        meeting_special = Meeting.objects.create(
            title='Meeting: Q&A Session (Important!)',
            description='Discussion about "Project X" & next steps; review @mentions',
            start_time=self.now + timedelta(hours=7),
            end_time=self.now + timedelta(hours=8)
        )
        
        ics_content = ICSGenerator.generate_ics(meeting_special)
        
        # Should not raise exception
        self.assertIsInstance(ics_content, bytes)
        
        # Should be parseable
        from icalendar import Calendar
        cal = Calendar.from_ical(ics_content)
        events = [component for component in cal.walk() if component.name == 'VEVENT']
        self.assertEqual(len(events), 1)



class ICSExportEndpointTestCase(APITestCase):
    """
    Test case for ICS export endpoint.
    
    Tests Requirement: 4.1
    """
    
    def setUp(self):
        """Set up test client and sample data."""
        self.client = APIClient()
        self.base_url = '/api/meetings/'
        self.now = timezone.now()
        
        # Create test meeting
        self.meeting = Meeting.objects.create(
            title='Team Standup',
            description='Daily team standup meeting',
            start_time=self.now + timedelta(hours=1),
            end_time=self.now + timedelta(hours=2)
        )
        
        # Add participants
        Participant.objects.create(
            meeting=self.meeting,
            email='alice@example.com',
            name='Alice Smith'
        )
        
        Participant.objects.create(
            meeting=self.meeting,
            email='bob@example.com',
            name='Bob Johnson'
        )
    
    def test_export_meeting_as_ics(self):
        """
        Test exporting a meeting as ICS file.
        Requirement: 4.1
        """
        response = self.client.get(f'{self.base_url}{self.meeting.id}/export/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify Content-Type header
        self.assertEqual(response['Content-Type'], 'text/calendar; charset=utf-8')
        
        # Verify Content-Disposition header
        self.assertIn('Content-Disposition', response)
        self.assertIn('attachment', response['Content-Disposition'])
        self.assertIn('.ics', response['Content-Disposition'])
    
    def test_export_ics_content_structure(self):
        """
        Test that exported ICS has proper structure.
        Requirement: 4.1
        """
        response = self.client.get(f'{self.base_url}{self.meeting.id}/export/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Get content
        ics_content = response.content.decode('utf-8')
        
        # Verify ICS structure
        self.assertIn('BEGIN:VCALENDAR', ics_content)
        self.assertIn('END:VCALENDAR', ics_content)
        self.assertIn('BEGIN:VEVENT', ics_content)
        self.assertIn('END:VEVENT', ics_content)
        
        # Verify meeting details
        self.assertIn('SUMMARY:Team Standup', ics_content)
        self.assertIn('DESCRIPTION:Daily team standup meeting', ics_content)
    
    def test_export_ics_includes_participants(self):
        """
        Test that exported ICS includes participant information.
        Requirement: 4.1
        """
        response = self.client.get(f'{self.base_url}{self.meeting.id}/export/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Get content and unfold lines
        ics_content = response.content.decode('utf-8')
        ics_unfolded = ics_content.replace('\r\n ', '').replace('\n ', '')
        
        # Verify attendees are included
        self.assertIn('ATTENDEE', ics_content)
        self.assertIn('alice@example.com', ics_unfolded)
        self.assertIn('bob@example.com', ics_unfolded)
    
    def test_export_nonexistent_meeting(self):
        """
        Test exporting a meeting that doesn't exist.
        Requirement: 4.1
        """
        fake_uuid = '00000000-0000-0000-0000-000000000000'
        response = self.client.get(f'{self.base_url}{fake_uuid}/export/')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('error', response.json())
    
    def test_export_filename_sanitization(self):
        """
        Test that filename is properly sanitized.
        Requirement: 4.1
        """
        # Create meeting with special characters in title
        meeting_special = Meeting.objects.create(
            title='Meeting: Q&A (Important!)',
            description='Test meeting',
            start_time=self.now + timedelta(hours=3),
            end_time=self.now + timedelta(hours=4)
        )
        
        response = self.client.get(f'{self.base_url}{meeting_special.id}/export/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify filename is sanitized (no special characters except _ - .)
        content_disposition = response['Content-Disposition']
        self.assertIn('.ics', content_disposition)
        # Should not contain special characters like : & ( ) !
        filename_part = content_disposition.split('filename=')[1].strip('"')
        self.assertNotIn(':', filename_part)
        self.assertNotIn('&', filename_part)
        self.assertNotIn('(', filename_part)
        self.assertNotIn(')', filename_part)
        self.assertNotIn('!', filename_part)
    
    def test_export_meeting_without_participants(self):
        """
        Test exporting a meeting without participants.
        Requirement: 4.1
        """
        meeting_no_participants = Meeting.objects.create(
            title='Solo Meeting',
            description='Meeting without participants',
            start_time=self.now + timedelta(hours=5),
            end_time=self.now + timedelta(hours=6)
        )
        
        response = self.client.get(f'{self.base_url}{meeting_no_participants.id}/export/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'text/calendar; charset=utf-8')
        
        # Should still have valid ICS structure
        ics_content = response.content.decode('utf-8')
        self.assertIn('BEGIN:VCALENDAR', ics_content)
        self.assertIn('SUMMARY:Solo Meeting', ics_content)
    
    def test_export_ics_parseable(self):
        """
        Test that exported ICS can be parsed by icalendar library.
        Requirement: 4.1
        """
        from icalendar import Calendar
        
        response = self.client.get(f'{self.base_url}{self.meeting.id}/export/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Parse the ICS content
        cal = Calendar.from_ical(response.content)
        
        # Verify it's a valid calendar
        self.assertEqual(cal.get('version'), '2.0')
        
        # Get events
        events = [component for component in cal.walk() if component.name == 'VEVENT']
        self.assertEqual(len(events), 1)
        
        # Verify event details
        event = events[0]
        self.assertEqual(str(event.get('summary')), self.meeting.title)



class ICSExportEndpointTestCase(APITestCase):
    """
    Test case for ICS export endpoint.
    
    Tests Requirement: 4.1
    """
    
    def setUp(self):
        """Set up test client and sample data."""
        self.client = APIClient()
        self.base_url = '/api/meetings/'
        self.now = timezone.now()
        
        # Create test meeting
        self.meeting = Meeting.objects.create(
            title='Team Standup',
            description='Daily standup meeting',
            start_time=self.now + timedelta(hours=1),
            end_time=self.now + timedelta(hours=2)
        )
        
        # Add participants
        Participant.objects.create(
            meeting=self.meeting,
            email='alice@example.com',
            name='Alice Smith'
        )
        
        Participant.objects.create(
            meeting=self.meeting,
            email='bob@example.com',
            name='Bob Johnson'
        )
    
    def test_export_meeting_as_ics(self):
        """
        Test exporting a meeting as ICS file.
        Requirement: 4.1
        """
        response = self.client.get(f'{self.base_url}{self.meeting.id}/export/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify Content-Type header (may include charset)
        self.assertIn('text/calendar', response['Content-Type'])
        
        # Verify Content-Disposition header
        self.assertIn('Content-Disposition', response)
        self.assertIn('attachment', response['Content-Disposition'])
        self.assertIn('.ics', response['Content-Disposition'])
    
    def test_export_ics_content(self):
        """
        Test that exported ICS content is valid.
        Requirement: 4.1
        """
        response = self.client.get(f'{self.base_url}{self.meeting.id}/export/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Get content
        ics_content = response.content
        ics_str = ics_content.decode('utf-8')
        
        # Verify ICS structure
        self.assertIn('BEGIN:VCALENDAR', ics_str)
        self.assertIn('END:VCALENDAR', ics_str)
        self.assertIn('BEGIN:VEVENT', ics_str)
        self.assertIn('END:VEVENT', ics_str)
        
        # Verify meeting details
        self.assertIn('SUMMARY:Team Standup', ics_str)
        self.assertIn('DESCRIPTION:Daily standup meeting', ics_str)
        
        # Verify attendees are included
        self.assertIn('ATTENDEE', ics_str)
    
    def test_export_ics_parseable(self):
        """
        Test that exported ICS can be parsed by icalendar library.
        Requirement: 4.1
        """
        from icalendar import Calendar
        
        response = self.client.get(f'{self.base_url}{self.meeting.id}/export/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Parse the ICS content
        cal = Calendar.from_ical(response.content)
        
        # Verify it's a valid calendar
        self.assertEqual(cal.get('version'), '2.0')
        
        # Get events
        events = [component for component in cal.walk() if component.name == 'VEVENT']
        self.assertEqual(len(events), 1)
        
        # Verify event details
        event = events[0]
        self.assertEqual(str(event.get('summary')), self.meeting.title)
        self.assertEqual(str(event.get('uid')), str(self.meeting.id))
    
    def test_export_nonexistent_meeting(self):
        """
        Test exporting a meeting that doesn't exist.
        Requirement: 4.1
        """
        fake_uuid = '00000000-0000-0000-0000-000000000000'
        response = self.client.get(f'{self.base_url}{fake_uuid}/export/')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('error', response.json())
    
    def test_export_filename_sanitization(self):
        """
        Test that special characters in meeting title are sanitized in filename.
        Requirement: 4.1
        """
        meeting_special = Meeting.objects.create(
            title='Meeting: Q&A / Review (Important!)',
            description='Special characters test',
            start_time=self.now + timedelta(hours=3),
            end_time=self.now + timedelta(hours=4)
        )
        
        response = self.client.get(f'{self.base_url}{meeting_special.id}/export/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Filename should be sanitized (no special chars except allowed ones)
        content_disposition = response['Content-Disposition']
        self.assertIn('.ics', content_disposition)
        # Should not contain problematic characters
        self.assertNotIn('/', content_disposition.split('filename=')[1])
        self.assertNotIn(':', content_disposition.split('filename=')[1])
    
    def test_export_meeting_without_participants(self):
        """
        Test exporting a meeting without participants.
        Requirement: 4.1
        """
        meeting_no_participants = Meeting.objects.create(
            title='Solo Meeting',
            description='No participants',
            start_time=self.now + timedelta(hours=5),
            end_time=self.now + timedelta(hours=6)
        )
        
        response = self.client.get(f'{self.base_url}{meeting_no_participants.id}/export/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('text/calendar', response['Content-Type'])
        
        # Should still be valid ICS
        ics_str = response.content.decode('utf-8')
        self.assertIn('BEGIN:VCALENDAR', ics_str)
        self.assertIn('SUMMARY:Solo Meeting', ics_str)
