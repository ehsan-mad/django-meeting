# Quick Test Commands

## Start the Server
```bash
python manage.py runserver
```

## Quick Test with Python Script
```bash
python test_api_endpoints.py
```

---

## Manual cURL Commands

### 1. Create Meeting
```bash
curl -X POST http://localhost:8000/api/meetings/ \
  -H "Content-Type: application/json" \
  -d "{\"title\":\"Team Meeting\",\"description\":\"Weekly sync\",\"start_time\":\"2025-12-10T10:00:00+00:00\",\"end_time\":\"2025-12-10T11:00:00+00:00\"}"
```

### 2. List All Meetings
```bash
curl -X GET http://localhost:8000/api/meetings/
```

### 3. List with Date Filter
```bash
curl -X GET "http://localhost:8000/api/meetings/?start_date=2025-12-01T00:00:00%2B00:00&end_date=2025-12-31T23:59:59%2B00:00"
```

### 4. Get Specific Meeting (replace {id} with actual UUID)
```bash
curl -X GET http://localhost:8000/api/meetings/{id}/
```

### 5. Update Meeting (replace {id} with actual UUID)
```bash
curl -X PUT http://localhost:8000/api/meetings/{id}/ \
  -H "Content-Type: application/json" \
  -d "{\"title\":\"Updated Meeting\",\"description\":\"Updated desc\",\"start_time\":\"2025-12-10T11:00:00+00:00\",\"end_time\":\"2025-12-10T12:00:00+00:00\"}"
```

### 6. Partial Update (replace {id} with actual UUID)
```bash
curl -X PATCH http://localhost:8000/api/meetings/{id}/ \
  -H "Content-Type: application/json" \
  -d "{\"title\":\"New Title Only\"}"
```

### 7. Delete Meeting (replace {id} with actual UUID)
```bash
curl -X DELETE http://localhost:8000/api/meetings/{id}/
```

---

## Sample JSON Payloads

### Valid Meeting Creation
```json
{
  "title": "Project Review",
  "description": "Quarterly project review meeting",
  "start_time": "2025-12-10T14:00:00+00:00",
  "end_time": "2025-12-10T15:30:00+00:00"
}
```

### Minimal Meeting (description is optional)
```json
{
  "title": "Quick Sync",
  "start_time": "2025-12-11T09:00:00+00:00",
  "end_time": "2025-12-11T09:15:00+00:00"
}
```

### Invalid - End Time Before Start Time (should return 400)
```json
{
  "title": "Invalid Meeting",
  "start_time": "2025-12-05T10:00:00+00:00",
  "end_time": "2025-12-05T09:00:00+00:00"
}
```

### Invalid - Missing Required Fields (should return 400)
```json
{
  "description": "Only description"
}
```

---

## Expected HTTP Status Codes

- **200 OK** - Successful GET, PUT, PATCH
- **201 Created** - Successful POST (meeting created)
- **204 No Content** - Successful DELETE
- **400 Bad Request** - Validation errors, malformed data
- **404 Not Found** - Meeting ID doesn't exist
- **500 Internal Server Error** - Unexpected server errors

---

## Testing Workflow

1. **Start server**: `python manage.py runserver`
2. **Create a meeting** and save the returned `id`
3. **List meetings** to see your created meeting
4. **Retrieve** the specific meeting using the `id`
5. **Update** the meeting with new data
6. **Partial update** to change only specific fields
7. **Delete** the meeting
8. **Verify deletion** by trying to retrieve it (should get 404)

---

## PowerShell Commands (Windows)

### Create Meeting
```powershell
$body = @{
    title = "Team Meeting"
    description = "Weekly sync"
    start_time = "2025-12-10T10:00:00+00:00"
    end_time = "2025-12-10T11:00:00+00:00"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/api/meetings/" -Method Post -Body $body -ContentType "application/json"
```

### List Meetings
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/meetings/" -Method Get
```

### Get Specific Meeting
```powershell
$meetingId = "your-meeting-id-here"
Invoke-RestMethod -Uri "http://localhost:8000/api/meetings/$meetingId/" -Method Get
```

### Update Meeting
```powershell
$meetingId = "your-meeting-id-here"
$body = @{
    title = "Updated Meeting"
    description = "Updated description"
    start_time = "2025-12-10T11:00:00+00:00"
    end_time = "2025-12-10T12:00:00+00:00"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/api/meetings/$meetingId/" -Method Put -Body $body -ContentType "application/json"
```

### Delete Meeting
```powershell
$meetingId = "your-meeting-id-here"
Invoke-RestMethod -Uri "http://localhost:8000/api/meetings/$meetingId/" -Method Delete
```
