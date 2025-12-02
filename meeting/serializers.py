"""
Serializers for Meeting Scheduler API.

This module provides serializers for validating and transforming data
for Meeting and Participant models.

Requirements: 1.3, 7.3
"""
from rest_framework import serializers
from .models import Meeting, Participant


class ParticipantSerializer(serializers.ModelSerializer):
    """
    Serializer for Participant model with email validation.
    
    Requirements: 1.3, 7.3
    """
    
    class Meta:
        model = Participant
        fields = ['id', 'email', 'name', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def validate_email(self, value):
        """
        Validate email format and ensure it's not empty.
        
        Requirement: 7.3 - Detailed validation error messages
        """
        if not value or not value.strip():
            raise serializers.ValidationError("Email address cannot be empty")
        
        # Django's EmailField already validates format, but we add extra checks
        value = value.strip().lower()
        
        return value
    
    def validate_name(self, value):
        """
        Validate name is not empty.
        
        Requirement: 7.3 - Detailed validation error messages
        """
        if not value or not value.strip():
            raise serializers.ValidationError("Name cannot be empty")
        
        return value.strip()


class MeetingSerializer(serializers.ModelSerializer):
    """
    Serializer for Meeting model with validation for required fields and time logic.
    
    Requirements: 1.3, 7.3
    """
    participants = ParticipantSerializer(many=True, read_only=True)
    
    class Meta:
        model = Meeting
        fields = [
            'id', 
            'title', 
            'description', 
            'start_time', 
            'end_time', 
            'created_at', 
            'updated_at',
            'participants'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate_title(self, value):
        """
        Validate title is not empty.
        
        Requirement: 1.3 - Required field validation
        """
        if not value or not value.strip():
            raise serializers.ValidationError("Title cannot be empty")
        
        return value.strip()
    
    def validate(self, data):
        """
        Validate that end_time is after start_time.
        
        Requirements: 
        - 1.2: End time validation
        - 1.3: Required field validation
        - 7.3: Detailed validation error messages
        """
        # Check if we're updating and need to get existing values
        if self.instance:
            start_time = data.get('start_time', self.instance.start_time)
            end_time = data.get('end_time', self.instance.end_time)
        else:
            start_time = data.get('start_time')
            end_time = data.get('end_time')
        
        # Validate required fields for creation
        if not self.instance:
            if not start_time:
                raise serializers.ValidationError({
                    'start_time': 'This field is required'
                })
            if not end_time:
                raise serializers.ValidationError({
                    'end_time': 'This field is required'
                })
            if 'title' not in data:
                raise serializers.ValidationError({
                    'title': 'This field is required'
                })
        
        # Validate time logic
        if start_time and end_time:
            if end_time <= start_time:
                raise serializers.ValidationError({
                    'end_time': 'End time must be after start time'
                })
        
        return data
