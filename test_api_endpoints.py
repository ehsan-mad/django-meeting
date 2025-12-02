#!/usr/bin/env python
"""
Quick API Testing Script for Meeting Scheduler

Run this script after starting the Django server:
    python manage.py runserver

Then in another terminal:
    python test_api_endpoints.py
"""

import requests
import json
from datetime import datetime, timedelta
from urllib.parse import quote

BASE_URL = "http://localhost:8000/api/meetings/"

def print_response(title, response):
    """Pretty print API response"""
    print(f"\n{'='*60}")
    print(f"{title}")
    print(f"{'='*60}")
    print(f"Status Code: {response.status_code}")
    if response.text:
        try:
            print(f"Response:\n{json.dumps(response.json(), indent=2)}")
        except:
            print(f"Response: {response.text}")
    else:
        print("Response: (empty)")
    print(f"{'='*60}\n")

def test_create_meeting():
    """Test: Create a new meeting"""
    meeting_data = {
        "title": "Sprint Planning",
        "description": "Planning for next sprint",
        "start_time": "2025-12-15T09:00:00+00:00",
        "end_time": "2025-12-15T11:00:00+00:00"
    }
    
    response = requests.post(BASE_URL, json=meeting_data)
    print_response("1. CREATE MEETING (POST /api/meetings/)", response)
    
    if response.status_code == 201:
        return response.json()['id']
    return None

def test_list_meetings():
    """Test: List all meetings"""
    response = requests.get(BASE_URL)
    print_response("2. LIST ALL MEETINGS (GET /api/meetings/)", response)

def test_list_with_filter():
    """Test: List meetings with date range filter"""
    start_date = "2025-12-01T00:00:00+00:00"
    end_date = "2025-12-31T23:59:59+00:00"
    
    url = f"{BASE_URL}?start_date={quote(start_date)}&end_date={quote(end_date)}"
    response = requests.get(url)
    print_response("3. LIST WITH DATE FILTER (GET /api/meetings/?start_date=...&end_date=...)", response)

def test_retrieve_meeting(meeting_id):
    """Test: Retrieve a specific meeting"""
    response = requests.get(f"{BASE_URL}{meeting_id}/")
    print_response(f"4. RETRIEVE MEETING (GET /api/meetings/{meeting_id}/)", response)

def test_update_meeting(meeting_id):
    """Test: Full update of a meeting"""
    update_data = {
        "title": "Updated Sprint Planning",
        "description": "Updated planning session for sprint",
        "start_time": "2025-12-15T10:00:00+00:00",
        "end_time": "2025-12-15T12:00:00+00:00"
    }
    
    response = requests.put(f"{BASE_URL}{meeting_id}/", json=update_data)
    print_response(f"5. UPDATE MEETING (PUT /api/meetings/{meeting_id}/)", response)

def test_partial_update_meeting(meeting_id):
    """Test: Partial update of a meeting"""
    patch_data = {
        "title": "Quick Sprint Planning"
    }
    
    response = requests.patch(f"{BASE_URL}{meeting_id}/", json=patch_data)
    print_response(f"6. PARTIAL UPDATE (PATCH /api/meetings/{meeting_id}/)", response)

def test_add_participant(meeting_id):
    """Test: Add a participant to a meeting"""
    participant_data = {
        "email": "john.doe@example.com",
        "name": "John Doe"
    }
    
    response = requests.post(f"{BASE_URL}{meeting_id}/participants/", json=participant_data)
    print_response(f"7. ADD PARTICIPANT (POST /api/meetings/{meeting_id}/participants/)", response)
    return response.status_code == 201

def test_add_duplicate_participant(meeting_id):
    """Test: Try to add duplicate participant"""
    participant_data = {
        "email": "john.doe@example.com",
        "name": "John Doe"
    }
    
    response = requests.post(f"{BASE_URL}{meeting_id}/participants/", json=participant_data)
    print_response(f"8. ADD DUPLICATE PARTICIPANT (POST /api/meetings/{meeting_id}/participants/)", response)

def test_remove_participant(meeting_id):
    """Test: Remove a participant from a meeting"""
    email = "john.doe@example.com"
    response = requests.delete(f"{BASE_URL}{meeting_id}/participants/{quote(email)}/")
    print_response(f"9. REMOVE PARTICIPANT (DELETE /api/meetings/{meeting_id}/participants/{email}/)", response)

def test_export_meeting(meeting_id):
    """Test: Export meeting as ICS file"""
    response = requests.get(f"{BASE_URL}{meeting_id}/export/")
    print_response(f"10. EXPORT MEETING AS ICS (GET /api/meetings/{meeting_id}/export/)", response)
    
    if response.status_code == 200:
        # Optionally save the ICS file
        with open('exported_meeting.ics', 'wb') as f:
            f.write(response.content)
        print("✅ ICS file saved as 'exported_meeting.ics'")

def test_delete_meeting(meeting_id):
    """Test: Delete a meeting"""
    response = requests.delete(f"{BASE_URL}{meeting_id}/")
    print_response(f"11. DELETE MEETING (DELETE /api/meetings/{meeting_id}/)", response)

def test_error_scenarios():
    """Test: Various error scenarios"""
    print("\n" + "="*60)
    print("ERROR SCENARIO TESTS")
    print("="*60)
    
    # Test 1: Invalid time range
    print("\n--- Test: Invalid Time Range (end_time before start_time) ---")
    invalid_data = {
        "title": "Invalid Meeting",
        "start_time": "2025-12-05T10:00:00+00:00",
        "end_time": "2025-12-05T09:00:00+00:00"
    }
    response = requests.post(BASE_URL, json=invalid_data)
    print_response("ERROR: Invalid Time Range", response)
    
    # Test 2: Missing required fields
    print("\n--- Test: Missing Required Fields ---")
    incomplete_data = {
        "description": "Only description provided"
    }
    response = requests.post(BASE_URL, json=incomplete_data)
    print_response("ERROR: Missing Required Fields", response)
    
    # Test 3: Non-existent meeting
    print("\n--- Test: Retrieve Non-existent Meeting ---")
    fake_id = "00000000-0000-0000-0000-000000000000"
    response = requests.get(f"{BASE_URL}{fake_id}/")
    print_response("ERROR: Meeting Not Found", response)
    
    # Test 4: Invalid date format in filter
    print("\n--- Test: Invalid Date Format in Filter ---")
    response = requests.get(f"{BASE_URL}?start_date=invalid-date")
    print_response("ERROR: Invalid Date Format", response)

def main():
    """Run all API tests"""
    print("\n" + "="*60)
    print("MEETING SCHEDULER API TESTING")
    print("="*60)
    print(f"Base URL: {BASE_URL}")
    print("="*60)
    
    try:
        # Test basic CRUD operations
        meeting_id = test_create_meeting()
        
        if meeting_id:
            test_list_meetings()
            test_list_with_filter()
            test_retrieve_meeting(meeting_id)
            test_update_meeting(meeting_id)
            test_partial_update_meeting(meeting_id)
            
            # Test participant management
            test_add_participant(meeting_id)
            test_add_duplicate_participant(meeting_id)
            test_retrieve_meeting(meeting_id)  # Show participants in meeting detail
            test_remove_participant(meeting_id)
            
            # Test ICS export
            test_export_meeting(meeting_id)
            
            test_delete_meeting(meeting_id)
        else:
            print("\n❌ Failed to create meeting. Cannot continue with other tests.")
            return
        
        # Test error scenarios
        test_error_scenarios()
        
        print("\n" + "="*60)
        print("✅ ALL TESTS COMPLETED!")
        print("="*60)
        
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Could not connect to the server.")
        print("Make sure Django server is running:")
        print("    python manage.py runserver")
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")

if __name__ == "__main__":
    main()
