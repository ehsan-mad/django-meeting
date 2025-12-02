# Conflict Detection Testing Guide

## Overview
This guide shows how to test the conflict detection service using Postman or cURL.

## Endpoint
**GET** `/api/meetings/{meeting_id}/check-conflicts/`

This temporary endpoint checks for scheduling conflicts for all participants in a meeting.

---

## Testing Scenario: Create Overlapping Meetings

### Step 1: Create First Meeting
**Method:** `POST`  
**URL:** `http://localhost:8000/api/meetings/`  
**Body:**
```json
{
  "title": "Team Standup",
  "description": "Daily standup meeting",
  "start_time": "2025-12-10T09:00:00+00:00",
  "end_time": "2025-12-10T10:00:00+00:00"
}
```

**Response:** Copy the `id` from the response (let's call it `meeting1_id`)

---

### Step 2: Create Second Meeting (Overlapping)
**Method:** `POST`  
**URL:** `http://localhost:8000/api/meetings/`  
**Body:**
```json
{
  "title": "Project Review",
  "description": "Review project progress",
  "start_time": "2025-12-10T09:30:00+00:00",
  "end_time": "2025-12-10T10:30:00+00:00"
}
```

**Response:** Copy the `id` from the response (let's call it `meeting2_id`)

**Note:** This meeting overlaps with Meeting 1 (9:30-10:30 overlaps with 9:00-10:00)

---

### Step 3: Create Third Meeting (No Overlap)
**Method:** `POST`  
**URL:** `http://localhost:8000/api/meetings/`  
**Body:**
```json
{
  "title": "Lunch Break",
  "description": "Team lunch",
  "start_time": "2025-12-10T12:00:00+00:00",
  "end_time": "2025-12-10T13:00:00+00:00"
}
```

**Response:** Copy the `id` from the response (let's call it `meeting3_id`)

---

### Step 4: Add Participant to Meeting 1
**Method:** `POST`  
**URL:** `http://localhost:8000/api/meetings/{meeting1_id}/participants/`  
**Body:**
```json
{
  "email": "alice@example.com",
  "name": "Alice Smith"
}
```

---

### Step 5: Add Same Participant to Meeting 2 (Overlapping)
**Method:** `POST`  
**URL:** `http://localhost:8000/api/meetings/{meeting2_id}/participants/`  
**Body:**
```json
{
  "email": "alice@example.com",
  "name": "Alice Smith"
}
```

**Note:** Alice is now in two overlapping meetings!

---

### Step 6: Check Conflicts for Meeting 1
**Method:** `GET`  
**URL:** `http://localhost:8000/api/meetings/{meeting1_id}/check-conflicts/`

**Expected Response:**
```json
{
  "has_conflicts": true,
  "conflicts": {
    "alice@example.com": [
      {
        "id": "meeting2_id",
        "title": "Project Review",
        "description": "Review project progress",
        "start_time": "2025-12-10T09:30:00+00:00",
        "end_time": "2025-12-10T10:30:00+00:00"
      }
    ]
  }
}
```

**Explanation:** Alice has a conflict because she's in Meeting 2 which overlaps with Meeting 1.

---

### Step 7: Check Conflicts for Meeting 2
**Method:** `GET`  
**URL:** `http://localhost:8000/api/meetings/{meeting2_id}/check-conflicts/`

**Expected Response:**
```json
{
  "has_conflicts": true,
  "conflicts": {
    "alice@example.com": [
      {
        "id": "meeting1_id",
        "title": "Team Standup",
        "description": "Daily standup meeting",
        "start_time": "2025-12-10T09:00:00+00:00",
        "end_time": "2025-12-10T10:00:00+00:00"
      }
    ]
  }
}
```

**Explanation:** From Meeting 2's perspective, Alice has a conflict with Meeting 1.

---

### Step 8: Add Participant to Meeting 3 (No Overlap)
**Method:** `POST`  
**URL:** `http://localhost:8000/api/meetings/{meeting3_id}/participants/`  
**Body:**
```json
{
  "email": "alice@example.com",
  "name": "Alice Smith"
}
```

---

### Step 9: Check Conflicts for Meeting 3
**Method:** `GET`  
**URL:** `http://localhost:8000/api/meetings/{meeting3_id}/check-conflicts/`

**Expected Response:**
```json
{
  "has_conflicts": false,
  "conflicts": {}
}
```

**Explanation:** Meeting 3 (12:00-13:00) doesn't overlap with Alice's other meetings, so no conflicts.

---

## Testing Scenario: Multiple Participants with Different Conflicts

### Step 10: Add Second Participant to Meeting 1
**Method:** `POST`  
**URL:** `http://localhost:8000/api/meetings/{meeting1_id}/participants/`  
**Body:**
```json
{
  "email": "bob@example.com",
  "name": "Bob Johnson"
}
```

---

### Step 11: Create Fourth Meeting
**Method:** `POST`  
**URL:** `http://localhost:8000/api/meetings/`  
**Body:**
```json
{
  "title": "Design Review",
  "description": "Review design mockups",
  "start_time": "2025-12-10T09:15:00+00:00",
  "end_time": "2025-12-10T09:45:00+00:00"
}
```

**Response:** Copy the `id` (let's call it `meeting4_id`)

---

### Step 12: Add Bob to Meeting 4
**Method:** `POST`  
**URL:** `http://localhost:8000/api/meetings/{meeting4_id}/participants/`  
**Body:**
```json
{
  "email": "bob@example.com",
  "name": "Bob Johnson"
}
```

---

### Step 13: Check Conflicts for Meeting 1 (Multiple Participants)
**Method:** `GET`  
**URL:** `http://localhost:8000/api/meetings/{meeting1_id}/check-conflicts/`

**Expected Response:**
```json
{
  "has_conflicts": true,
  "conflicts": {
    "alice@example.com": [
      {
        "id": "meeting2_id",
        "title": "Project Review",
        "description": "Review project progress",
        "start_time": "2025-12-10T09:30:00+00:00",
        "end_time": "2025-12-10T10:30:00+00:00"
      }
    ],
    "bob@example.com": [
      {
        "id": "meeting4_id",
        "title": "Design Review",
        "description": "Review design mockups",
        "start_time": "2025-12-10T09:15:00+00:00",
        "end_time": "2025-12-10T09:45:00+00:00"
      }
    ]
  }
}
```

**Explanation:** 
- Alice has a conflict with Meeting 2
- Bob has a conflict with Meeting 4
- Both conflicts are reported in a single response

---

## Testing Edge Cases

### Edge Case 1: Adjacent Meetings (No Overlap)
Create two meetings where one ends exactly when the other starts:

**Meeting A:**
```json
{
  "title": "Morning Session",
  "start_time": "2025-12-11T09:00:00+00:00",
  "end_time": "2025-12-11T10:00:00+00:00"
}
```

**Meeting B:**
```json
{
  "title": "Mid-Morning Session",
  "start_time": "2025-12-11T10:00:00+00:00",
  "end_time": "2025-12-11T11:00:00+00:00"
}
```

Add the same participant to both, then check conflicts.

**Expected:** `has_conflicts: false` (adjacent meetings don't overlap)

---

### Edge Case 2: One Meeting Contains Another
**Meeting Outer:**
```json
{
  "title": "All Day Workshop",
  "start_time": "2025-12-12T09:00:00+00:00",
  "end_time": "2025-12-12T17:00:00+00:00"
}
```

**Meeting Inner:**
```json
{
  "title": "Lunch Break",
  "start_time": "2025-12-12T12:00:00+00:00",
  "end_time": "2025-12-12T13:00:00+00:00"
}
```

Add the same participant to both, then check conflicts.

**Expected:** `has_conflicts: true` (inner meeting overlaps with outer)

---

### Edge Case 3: Same Start Time
**Meeting A:**
```json
{
  "title": "Meeting A",
  "start_time": "2025-12-13T14:00:00+00:00",
  "end_time": "2025-12-13T15:00:00+00:00"
}
```

**Meeting B:**
```json
{
  "title": "Meeting B",
  "start_time": "2025-12-13T14:00:00+00:00",
  "end_time": "2025-12-13T16:00:00+00:00"
}
```

Add the same participant to both, then check conflicts.

**Expected:** `has_conflicts: true` (same start time means overlap)

---

## cURL Commands

### Check Conflicts
```bash
curl -X GET http://localhost:8000/api/meetings/{meeting_id}/check-conflicts/
```

### Complete Test Flow
```bash
# 1. Create Meeting 1
MEETING1=$(curl -s -X POST http://localhost:8000/api/meetings/ \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Team Standup",
    "description": "Daily standup",
    "start_time": "2025-12-10T09:00:00+00:00",
    "end_time": "2025-12-10T10:00:00+00:00"
  }' | jq -r '.id')

echo "Meeting 1 ID: $MEETING1"

# 2. Create Meeting 2 (Overlapping)
MEETING2=$(curl -s -X POST http://localhost:8000/api/meetings/ \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Project Review",
    "description": "Review progress",
    "start_time": "2025-12-10T09:30:00+00:00",
    "end_time": "2025-12-10T10:30:00+00:00"
  }' | jq -r '.id')

echo "Meeting 2 ID: $MEETING2"

# 3. Add Alice to Meeting 1
curl -s -X POST http://localhost:8000/api/meetings/$MEETING1/participants/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "alice@example.com",
    "name": "Alice Smith"
  }'

# 4. Add Alice to Meeting 2
curl -s -X POST http://localhost:8000/api/meetings/$MEETING2/participants/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "alice@example.com",
    "name": "Alice Smith"
  }'

# 5. Check conflicts for Meeting 1
echo -e "\n\nConflicts for Meeting 1:"
curl -s -X GET http://localhost:8000/api/meetings/$MEETING1/check-conflicts/ | jq

# 6. Check conflicts for Meeting 2
echo -e "\n\nConflicts for Meeting 2:"
curl -s -X GET http://localhost:8000/api/meetings/$MEETING2/check-conflicts/ | jq
```

---

## Python Test Script

```python
import requests
import json

BASE_URL = "http://localhost:8000/api/meetings/"

# Create meetings
meeting1 = requests.post(BASE_URL, json={
    "title": "Team Standup",
    "description": "Daily standup",
    "start_time": "2025-12-10T09:00:00+00:00",
    "end_time": "2025-12-10T10:00:00+00:00"
}).json()

meeting2 = requests.post(BASE_URL, json={
    "title": "Project Review",
    "description": "Review progress",
    "start_time": "2025-12-10T09:30:00+00:00",
    "end_time": "2025-12-10T10:30:00+00:00"
}).json()

print(f"Meeting 1 ID: {meeting1['id']}")
print(f"Meeting 2 ID: {meeting2['id']}")

# Add participant to both meetings
requests.post(f"{BASE_URL}{meeting1['id']}/participants/", json={
    "email": "alice@example.com",
    "name": "Alice Smith"
})

requests.post(f"{BASE_URL}{meeting2['id']}/participants/", json={
    "email": "alice@example.com",
    "name": "Alice Smith"
})

# Check conflicts
conflicts1 = requests.get(f"{BASE_URL}{meeting1['id']}/check-conflicts/").json()
conflicts2 = requests.get(f"{BASE_URL}{meeting2['id']}/check-conflicts/").json()

print("\nConflicts for Meeting 1:")
print(json.dumps(conflicts1, indent=2))

print("\nConflicts for Meeting 2:")
print(json.dumps(conflicts2, indent=2))
```

---

## Response Format

### No Conflicts
```json
{
  "has_conflicts": false,
  "conflicts": {}
}
```

### With Conflicts
```json
{
  "has_conflicts": true,
  "conflicts": {
    "participant1@example.com": [
      {
        "id": "uuid-of-conflicting-meeting",
        "title": "Conflicting Meeting Title",
        "description": "Meeting description",
        "start_time": "2025-12-10T09:30:00+00:00",
        "end_time": "2025-12-10T10:30:00+00:00"
      }
    ],
    "participant2@example.com": [
      {
        "id": "another-uuid",
        "title": "Another Conflict",
        "description": "Another description",
        "start_time": "2025-12-10T09:15:00+00:00",
        "end_time": "2025-12-10T09:45:00+00:00"
      }
    ]
  }
}
```

---

## Notes

1. **Overlap Logic:** Two meetings overlap if `start_A < end_B AND start_B < end_A`
2. **Adjacent Meetings:** Meetings that end exactly when another starts do NOT overlap
3. **Self-Exclusion:** A meeting doesn't conflict with itself
4. **Multiple Conflicts:** A participant can have multiple conflicting meetings
5. **Empty Conflicts:** If no conflicts exist, the `conflicts` object is empty

---

## Cleanup

To remove the temporary endpoint after testing, remove the `check_conflicts` method from `meeting/views.py`.
