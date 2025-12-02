# Meeting Scheduler API Testing Guide

## Base URL
```
http://localhost:8000/api/
```

## Endpoints Overview

### 1. Create Meeting
**Endpoint:** `POST /api/meetings/`  
**Content-Type:** `application/json`

**Sample Request Body:**
```json
{
  "title": "Team Standup",
  "description": "Daily team standup meeting",
  "start_time": "2025-12-05T10:00:00+00:00",
  "end_time": "2025-12-05T10:30:00+00:00"
}
```

**Expected Response (201 Created):**
```json
{
  "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "title": "Team Standup",
  "description": "Daily team standup meeting",
  "start_time": "2025-12-05T10:00:00Z",
  "end_time": "2025-12-05T10:30:00Z",
  "created_at": "2025-12-01T10:00:00Z",
  "updated_at": "2025-12-01T10:00:00Z",
  "participants": []
}
```

**cURL Command:**
```bash
curl -X POST http://localhost:8000/api/meetings/ \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Team Standup",
    "description": "Daily team standup meeting",
    "start_time": "2025-12-05T10:00:00+00:00",
    "end_time": "2025-12-05T10:30:00+00:00"
  }'
```

---

### 2. List All Meetings
**Endpoint:** `GET /api/meetings/`

**Expected Response (200 OK):**
```json
[
  {
    "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "title": "Team Standup",
    "description": "Daily team standup meeting",
    "start_time": "2025-12-05T10:00:00Z",
    "end_time": "2025-12-05T10:30:00Z",
    "created_at": "2025-12-01T10:00:00Z",
    "updated_at": "2025-12-01T10:00:00Z",
    "participants": []
  }
]
```

**cURL Command:**
```bash
curl -X GET http://localhost:8000/api/meetings/
```

---

### 3. List Meetings with Date Range Filter
**Endpoint:** `GET /api/meetings/?start_date={ISO_DATE}&end_date={ISO_DATE}`

**Query Parameters:**
- `start_date`: Filter meetings starting on or after this date (ISO 8601 format)
- `end_date`: Filter meetings starting on or before this date (ISO 8601 format)

**Example URL:**
```
http://localhost:8000/api/meetings/?start_date=2025-12-01T00:00:00%2B00:00&end_date=2025-12-31T23:59:59%2B00:00
```

**cURL Command:**
```bash
curl -X GET "http://localhost:8000/api/meetings/?start_date=2025-12-01T00:00:00%2B00:00&end_date=2025-12-31T23:59:59%2B00:00"
```

**Note:** The `+` in the timezone must be URL-encoded as `%2B`

---

### 4. Retrieve Specific Meeting
**Endpoint:** `GET /api/meetings/{meeting_id}/`

**Example:**
```
GET /api/meetings/a1b2c3d4-e5f6-7890-abcd-ef1234567890/
```

**Expected Response (200 OK):**
```json
{
  "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "title": "Team Standup",
  "description": "Daily team standup meeting",
  "start_time": "2025-12-05T10:00:00Z",
  "end_time": "2025-12-05T10:30:00Z",
  "created_at": "2025-12-01T10:00:00Z",
  "updated_at": "2025-12-01T10:00:00Z",
  "participants": []
}
```

**cURL Command:**
```bash
curl -X GET http://localhost:8000/api/meetings/a1b2c3d4-e5f6-7890-abcd-ef1234567890/
```

---

### 5. Update Meeting (Full Update)
**Endpoint:** `PUT /api/meetings/{meeting_id}/`  
**Content-Type:** `application/json`

**Sample Request Body:**
```json
{
  "title": "Updated Team Standup",
  "description": "Updated description for daily standup",
  "start_time": "2025-12-05T11:00:00+00:00",
  "end_time": "2025-12-05T11:30:00+00:00"
}
```

**Expected Response (200 OK):**
```json
{
  "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "title": "Updated Team Standup",
  "description": "Updated description for daily standup",
  "start_time": "2025-12-05T11:00:00Z",
  "end_time": "2025-12-05T11:30:00Z",
  "created_at": "2025-12-01T10:00:00Z",
  "updated_at": "2025-12-01T10:15:00Z",
  "participants": []
}
```

**cURL Command:**
```bash
curl -X PUT http://localhost:8000/api/meetings/a1b2c3d4-e5f6-7890-abcd-ef1234567890/ \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Updated Team Standup",
    "description": "Updated description for daily standup",
    "start_time": "2025-12-05T11:00:00+00:00",
    "end_time": "2025-12-05T11:30:00+00:00"
  }'
```

---

### 6. Partial Update Meeting
**Endpoint:** `PATCH /api/meetings/{meeting_id}/`  
**Content-Type:** `application/json`

**Sample Request Body (only update title):**
```json
{
  "title": "Quick Standup"
}
```

**Expected Response (200 OK):**
```json
{
  "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "title": "Quick Standup",
  "description": "Updated description for daily standup",
  "start_time": "2025-12-05T11:00:00Z",
  "end_time": "2025-12-05T11:30:00Z",
  "created_at": "2025-12-01T10:00:00Z",
  "updated_at": "2025-12-01T10:20:00Z",
  "participants": []
}
```

**cURL Command:**
```bash
curl -X PATCH http://localhost:8000/api/meetings/a1b2c3d4-e5f6-7890-abcd-ef1234567890/ \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Quick Standup"
  }'
```

---

<!-- adding participant -->

### 7. Add Participant to Meeting
**Endpoint:** `POST /api/meetings/{meeting_id}/participants/`  
**Content-Type:** `application/json`

**Sample Request Body:**
```json
{
  "email": "john.doe@example.com",
  "name": "John Doe"
}
```

**Expected Response (201 Created):**
```json
{
  "id": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
  "email": "john.doe@example.com",
  "name": "John Doe",
  "created_at": "2025-12-01T10:30:00Z"
}
```

**cURL Command:**
```bash
curl -X POST http://localhost:8000/api/meetings/a1b2c3d4-e5f6-7890-abcd-ef1234567890/participants/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john.doe@example.com",
    "name": "John Doe"
  }'
```

---

### 8. Remove Participant from Meeting
**Endpoint:** `DELETE /api/meetings/{meeting_id}/participants/{email}/`

**Example:**
```
DELETE /api/meetings/a1b2c3d4-e5f6-7890-abcd-ef1234567890/participants/john.doe@example.com/
```

**Expected Response (204 No Content):**
```
(Empty response body)
```

**cURL Command:**
```bash
curl -X DELETE http://localhost:8000/api/meetings/a1b2c3d4-e5f6-7890-abcd-ef1234567890/participants/john.doe%40example.com/
```

**Note:** The `@` in the email must be URL-encoded as `%40`

---

### 9. Get All Meetings for a Participant
**Endpoint:** `GET /api/participants/{email}/meetings/`

**Example:**
```
GET /api/participants/alice@example.com/meetings/
```

**Query Parameters (Optional):**
- `start_date`: Filter meetings starting on or after this date (ISO 8601 format)
- `end_date`: Filter meetings starting on or before this date (ISO 8601 format)

**Expected Response (200 OK):**
```json
[
  {
    "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "title": "Team Standup",
    "description": "Daily standup meeting",
    "start_time": "2025-12-05T10:00:00Z",
    "end_time": "2025-12-05T10:30:00Z",
    "created_at": "2025-12-01T10:00:00Z",
    "updated_at": "2025-12-01T10:00:00Z",
    "participants": [...]
  },
  {
    "id": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
    "title": "Project Review",
    "description": "Review project progress",
    "start_time": "2025-12-05T14:00:00Z",
    "end_time": "2025-12-05T15:00:00Z",
    "created_at": "2025-12-01T11:00:00Z",
    "updated_at": "2025-12-01T11:00:00Z",
    "participants": [...]
  }
]
```

**Note:** Results are ordered chronologically by start_time

**cURL Command:**
```bash
curl -X GET http://localhost:8000/api/participants/alice%40example.com/meetings/
```

**With Date Filter:**
```bash
curl -X GET "http://localhost:8000/api/participants/alice%40example.com/meetings/?start_date=2025-12-01T00:00:00%2B00:00&end_date=2025-12-31T23:59:59%2B00:00"
```

---

### 10. Check Conflicts for a Participant
**Endpoint:** `GET /api/participants/{email}/conflicts/`

**Example:**
```
GET /api/participants/alice@example.com/conflicts/
```

**Query Parameters (Optional):**
- `start_date`: Filter conflicts starting on or after this date (ISO 8601 format)
- `end_date`: Filter conflicts starting on or before this date (ISO 8601 format)

**Expected Response (200 OK) - With Conflicts:**
```json
{
  "participant_email": "alice@example.com",
  "has_conflicts": true,
  "conflicts": [
    {
      "meeting": {
        "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
        "title": "Team Standup",
        "description": "Daily standup",
        "start_time": "2025-12-05T10:00:00Z",
        "end_time": "2025-12-05T10:30:00Z",
        "created_at": "2025-12-01T10:00:00Z",
        "updated_at": "2025-12-01T10:00:00Z",
        "participants": [...]
      },
      "conflicting_with": [
        {
          "id": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
          "title": "Project Review",
          "description": "Overlapping meeting",
          "start_time": "2025-12-05T10:15:00Z",
          "end_time": "2025-12-05T10:45:00Z",
          "created_at": "2025-12-01T11:00:00Z",
          "updated_at": "2025-12-01T11:00:00Z",
          "participants": [...]
        }
      ]
    }
  ]
}
```

**Expected Response (200 OK) - No Conflicts:**
```json
{
  "participant_email": "alice@example.com",
  "has_conflicts": false,
  "conflicts": []
}
```

**cURL Command:**
```bash
curl -X GET http://localhost:8000/api/participants/alice%40example.com/conflicts/
```

---

### 11. Export Meeting as ICS File
**Endpoint:** `GET /api/meetings/{meeting_id}/export/`

**Example:**
```
GET /api/meetings/a1b2c3d4-e5f6-7890-abcd-ef1234567890/export/
```

**Response Headers:**
- `Content-Type: text/calendar; charset=utf-8`
- `Content-Disposition: attachment; filename="Team_Standup.ics"`

**Response Body:**
```
BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Meeting Scheduler//Meeting Scheduler API//EN
CALSCALE:GREGORIAN
METHOD:PUBLISH
BEGIN:VEVENT
SUMMARY:Team Standup
DESCRIPTION:Daily team standup meeting
DTSTART:20251205T100000Z
DTEND:20251205T103000Z
UID:a1b2c3d4-e5f6-7890-abcd-ef1234567890
ATTENDEE;CN="Alice Smith";ROLE=REQ-PARTICIPANT;RSVP=TRUE:MAILTO:alice@example.com
ATTENDEE;CN="Bob Johnson";ROLE=REQ-PARTICIPANT;RSVP=TRUE:MAILTO:bob@example.com
DTSTAMP:20251201T100000Z
CREATED:20251201T100000Z
LAST-MODIFIED:20251201T100000Z
END:VEVENT
END:VCALENDAR
```

**cURL Command:**
```bash
curl -X GET http://localhost:8000/api/meetings/a1b2c3d4-e5f6-7890-abcd-ef1234567890/export/ -o meeting.ics
```

**Note:** The exported ICS file can be imported into any standard calendar application (Google Calendar, Outlook, Apple Calendar, etc.)

---

### 12. Delete Meeting
**Endpoint:** `DELETE /api/meetings/{meeting_id}/`

**Expected Response (204 No Content):**
```
(Empty response body)
```

**cURL Command:**
```bash
curl -X DELETE http://localhost:8000/api/meetings/a1b2c3d4-e5f6-7890-abcd-ef1234567890/
```

---

## Error Scenarios

### Invalid Time Range (end_time before start_time)
**Request:**
```json
{
  "title": "Invalid Meeting",
  "start_time": "2025-12-05T10:00:00+00:00",
  "end_time": "2025-12-05T09:00:00+00:00"
}
```

**Response (400 Bad Request):**
```json
{
  "end_time": ["End time must be after start time"]
}
```

---

### Missing Required Fields
**Request:**
```json
{
  "description": "Only description provided"
}
```

**Response (400 Bad Request):**
```json
{
  "title": ["This field is required"],
  "start_time": ["This field is required"],
  "end_time": ["This field is required"]
}
```

---

### Meeting Not Found
**Request:**
```
GET /api/meetings/00000000-0000-0000-0000-000000000000/
```

**Response (404 Not Found):**
```json
{
  "error": "Not found",
  "details": "Meeting with the specified ID does not exist"
}
```

---

### Invalid Date Format in Filter
**Request:**
```
GET /api/meetings/?start_date=invalid-date
```

**Response (400 Bad Request):**
```json
{
  "start_date": ["Invalid date format. Please use ISO 8601 format (e.g., 2025-12-01T10:00:00+00:00)"]
}
```

---

### Duplicate Participant
**Request:**
```json
POST /api/meetings/{meeting_id}/participants/
{
  "email": "john.doe@example.com",
  "name": "John Doe"
}
```
(When participant already exists in the meeting)

**Response (409 Conflict):**
```json
{
  "error": "Conflict",
  "details": "Participant with email john.doe@example.com is already added to this meeting"
}
```

---

### Participant Not Found
**Request:**
```
DELETE /api/meetings/{meeting_id}/participants/nonexistent@example.com/
```

**Response (404 Not Found):**
```json
{
  "error": "Not found",
  "details": "Participant with email nonexistent@example.com not found in this meeting"
}
```

---

## Testing with Postman

### Collection Setup

1. **Create Meeting**
   - Method: POST
   - URL: `http://localhost:8000/api/meetings/`
   - Headers: `Content-Type: application/json`
   - Body (raw JSON):
   ```json
   {
     "title": "Project Review",
     "description": "Quarterly project review meeting",
     "start_time": "2025-12-10T14:00:00+00:00",
     "end_time": "2025-12-10T15:30:00+00:00"
   }
   ```

2. **List Meetings**
   - Method: GET
   - URL: `http://localhost:8000/api/meetings/`

3. **Filter Meetings by Date**
   - Method: GET
   - URL: `http://localhost:8000/api/meetings/`
   - Params:
     - `start_date`: `2025-12-01T00:00:00+00:00`
     - `end_date`: `2025-12-31T23:59:59+00:00`

4. **Get Meeting by ID**
   - Method: GET
   - URL: `http://localhost:8000/api/meetings/{{meeting_id}}/`
   - (Replace `{{meeting_id}}` with actual ID from create response)

5. **Update Meeting**
   - Method: PUT
   - URL: `http://localhost:8000/api/meetings/{{meeting_id}}/`
   - Headers: `Content-Type: application/json`
   - Body (raw JSON):
   ```json
   {
     "title": "Updated Project Review",
     "description": "Updated quarterly project review",
     "start_time": "2025-12-10T15:00:00+00:00",
     "end_time": "2025-12-10T16:30:00+00:00"
   }
   ```

6. **Partial Update**
   - Method: PATCH
   - URL: `http://localhost:8000/api/meetings/{{meeting_id}}/`
   - Headers: `Content-Type: application/json`
   - Body (raw JSON):
   ```json
   {
     "description": "Only updating description"
   }
   ```

7. **Add Participant**
   - Method: POST
   - URL: `http://localhost:8000/api/meetings/{{meeting_id}}/participants/`
   - Headers: `Content-Type: application/json`
   - Body (raw JSON):
   ```json
   {
     "email": "participant@example.com",
     "name": "Participant Name"
   }
   ```

8. **Remove Participant**
   - Method: DELETE
   - URL: `http://localhost:8000/api/meetings/{{meeting_id}}/participants/participant@example.com/`
   - (Note: URL-encode the @ symbol as %40 if needed)

9. **Get Participant Meetings**
   - Method: GET
   - URL: `http://localhost:8000/api/participants/alice@example.com/meetings/`
   - (Note: URL-encode the @ symbol as %40 if needed)
   - Optional Params:
     - `start_date`: `2025-12-01T00:00:00+00:00`
     - `end_date`: `2025-12-31T23:59:59+00:00`

10. **Check Participant Conflicts**
   - Method: GET
   - URL: `http://localhost:8000/api/participants/alice@example.com/conflicts/`
   - (Note: URL-encode the @ symbol as %40 if needed)
   - Optional Params:
     - `start_date`: `2025-12-01T00:00:00+00:00`
     - `end_date`: `2025-12-31T23:59:59+00:00`

11. **Export Meeting as ICS**
   - Method: GET
   - URL: `http://localhost:8000/api/meetings/{{meeting_id}}/export/`
   - Response: Downloads an ICS file
   - Headers: 
     - Content-Type: `text/calendar; charset=utf-8`
     - Content-Disposition: `attachment; filename="Meeting_Title.ics"`

12. **Delete Meeting**
   - Method: DELETE
   - URL: `http://localhost:8000/api/meetings/{{meeting_id}}/`

---

## Testing with Python Requests

```python
import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000/api/meetings/"

# 1. Create a meeting
meeting_data = {
    "title": "Sprint Planning",
    "description": "Planning for next sprint",
    "start_time": "2025-12-15T09:00:00+00:00",
    "end_time": "2025-12-15T11:00:00+00:00"
}

response = requests.post(BASE_URL, json=meeting_data)
print(f"Create: {response.status_code}")
meeting = response.json()
meeting_id = meeting['id']
print(f"Created meeting ID: {meeting_id}")

# 2. List all meetings
response = requests.get(BASE_URL)
print(f"List: {response.status_code}")
print(f"Total meetings: {len(response.json())}")

# 3. Get specific meeting
response = requests.get(f"{BASE_URL}{meeting_id}/")
print(f"Retrieve: {response.status_code}")

# 4. Update meeting
update_data = {
    "title": "Updated Sprint Planning",
    "description": "Updated planning session",
    "start_time": "2025-12-15T10:00:00+00:00",
    "end_time": "2025-12-15T12:00:00+00:00"
}
response = requests.put(f"{BASE_URL}{meeting_id}/", json=update_data)
print(f"Update: {response.status_code}")

# 5. Partial update
patch_data = {"title": "Quick Sprint Planning"}
response = requests.patch(f"{BASE_URL}{meeting_id}/", json=patch_data)
print(f"Partial Update: {response.status_code}")

# 6. Filter by date range
from urllib.parse import quote
start = "2025-12-01T00:00:00+00:00"
end = "2025-12-31T23:59:59+00:00"
response = requests.get(f"{BASE_URL}?start_date={quote(start)}&end_date={quote(end)}")
print(f"Filter: {response.status_code}")

# 7. Add participant
participant_data = {
    "email": "participant@example.com",
    "name": "Test Participant"
}
response = requests.post(f"{BASE_URL}{meeting_id}/participants/", json=participant_data)
print(f"Add Participant: {response.status_code}")

# 8. Remove participant
response = requests.delete(f"{BASE_URL}{meeting_id}/participants/{quote('participant@example.com')}/")
print(f"Remove Participant: {response.status_code}")

# 9. Get all meetings for a participant
response = requests.get(f"http://localhost:8000/api/participants/{quote('alice@example.com')}/meetings/")
print(f"Participant Meetings: {response.status_code}")
print(f"Total meetings for Alice: {len(response.json())}")

# 10. Check conflicts for a participant
response = requests.get(f"http://localhost:8000/api/participants/{quote('alice@example.com')}/conflicts/")
print(f"Participant Conflicts: {response.status_code}")
conflicts_data = response.json()
print(f"Has conflicts: {conflicts_data['has_conflicts']}")

# 11. Export meeting as ICS file
response = requests.get(f"{BASE_URL}{meeting_id}/export/")
print(f"Export ICS: {response.status_code}")
if response.status_code == 200:
    # Save the ICS file
    with open('meeting.ics', 'wb') as f:
        f.write(response.content)
    print("ICS file saved as meeting.ics")

# 12. Delete meeting
response = requests.delete(f"{BASE_URL}{meeting_id}/")
print(f"Delete: {response.status_code}")
```

---

## Quick Start Testing Script

Save this as `test_api.sh` (Linux/Mac) or `test_api.bat` (Windows):

```bash
#!/bin/bash

# Start Django server first: python manage.py runserver

BASE_URL="http://localhost:8000/api/meetings/"

echo "1. Creating a meeting..."
RESPONSE=$(curl -s -X POST $BASE_URL \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Meeting",
    "description": "Testing API",
    "start_time": "2025-12-20T10:00:00+00:00",
    "end_time": "2025-12-20T11:00:00+00:00"
  }')
echo $RESPONSE

MEETING_ID=$(echo $RESPONSE | grep -o '"id":"[^"]*' | cut -d'"' -f4)
echo "Meeting ID: $MEETING_ID"

echo -e "\n2. Listing all meetings..."
curl -s -X GET $BASE_URL | json_pp

echo -e "\n3. Getting specific meeting..."
curl -s -X GET "${BASE_URL}${MEETING_ID}/" | json_pp

echo -e "\n4. Updating meeting..."
curl -s -X PUT "${BASE_URL}${MEETING_ID}/" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Updated Test Meeting",
    "description": "Updated description",
    "start_time": "2025-12-20T11:00:00+00:00",
    "end_time": "2025-12-20T12:00:00+00:00"
  }' | json_pp

echo -e "\n5. Deleting meeting..."
curl -s -X DELETE "${BASE_URL}${MEETING_ID}/"
echo "Deleted!"
```

---

## Notes

1. **Start the Django server** before testing:
   ```bash
   python manage.py runserver
   ```

2. **Date Format**: Always use ISO 8601 format with timezone:
   - `2025-12-05T10:00:00+00:00` (UTC)
   - `2025-12-05T10:00:00-05:00` (EST)

3. **URL Encoding**: When using dates in query parameters, encode the `+` as `%2B`

4. **Meeting IDs**: UUIDs are returned in responses and used in URLs

5. **Cascade Delete**: Deleting a meeting also deletes all associated participants
