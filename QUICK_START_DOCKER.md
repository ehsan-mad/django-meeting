# 🚀 Quick Start with Docker (5 Minutes)

## Step 1: Install Docker Desktop ⬇️

### Windows Users:
1. Go to: https://www.docker.com/products/docker-desktop
2. Click "Download for Windows"
3. Run the installer (Docker Desktop Installer.exe)
4. Follow the installation wizard
5. **Restart your computer**
6. Open Docker Desktop from Start Menu
7. Wait for Docker to start (you'll see a whale icon 🐳 in system tray)

### Mac Users:
1. Go to: https://www.docker.com/products/docker-desktop
2. Click "Download for Mac"
3. Open the .dmg file
4. Drag Docker to Applications
5. Open Docker from Applications
6. Grant permissions when asked

---

## Step 2: Verify Docker is Working ✅

Open **Command Prompt** (Windows) or **Terminal** (Mac) and type:

```bash
docker --version
```

You should see something like:
```
Docker version 24.0.7, build afdd53b
```

---

## Step 3: Navigate to Project Folder 📁

In your terminal, go to the project directory:

**Windows:**
```bash
cd C:\dev\django\Test-projects\meetingscheduler
```

**Mac/Linux:**
```bash
cd /path/to/meetingscheduler
```

---

## Step 4: Start the Application 🎯

Run this ONE command:

```bash
docker-compose up
```

### What You'll See:

```
[+] Building 45.2s (18/18) FINISHED
[+] Running 2/2
 ✔ Network meetingscheduler_meeting-network  Created
 ✔ Container meeting-scheduler               Created
Attaching to meeting-scheduler
meeting-scheduler  | Starting Meeting Scheduler...
meeting-scheduler  | Checking database connection...
meeting-scheduler  | Running database migrations...
meeting-scheduler  | Operations to perform:
meeting-scheduler  |   Apply all migrations: admin, auth, contenttypes, meeting, sessions
meeting-scheduler  | Running migrations:
meeting-scheduler  |   Applying contenttypes.0001_initial... OK
meeting-scheduler  |   Applying auth.0001_initial... OK
meeting-scheduler  |   ...
meeting-scheduler  | Starting application...
meeting-scheduler  | Starting development server at http://0.0.0.0:8000/
meeting-scheduler  | Quit the server with CONTROL-C.
```

**✅ When you see "Starting development server" - it's ready!**

---

## Step 5: Test the API 🧪

### Option A: Use Your Web Browser

Open your browser and go to:
```
http://localhost:8000/api/meetings/
```

You should see:
```json
[]
```
(Empty list because no meetings exist yet)

### Option B: Use Postman

1. Open Postman
2. Create new request
3. Set to `GET`
4. URL: `http://localhost:8000/api/meetings/`
5. Click "Send"

### Option C: Use cURL (Command Line)

Open a **NEW** terminal window (keep docker-compose running in the first one):

```bash
curl http://localhost:8000/api/meetings/
```

---

## Step 6: Create Your First Meeting 📅

### Using cURL:

**Windows (Command Prompt):**
```bash
curl -X POST http://localhost:8000/api/meetings/ -H "Content-Type: application/json" -d "{\"title\": \"My First Meeting\", \"description\": \"Testing Docker\", \"start_time\": \"2025-12-10T09:00:00+00:00\", \"end_time\": \"2025-12-10T10:00:00+00:00\"}"
```

**Windows (PowerShell):**
```powershell
$body = @{
    title = "My First Meeting"
    description = "Testing Docker"
    start_time = "2025-12-10T09:00:00+00:00"
    end_time = "2025-12-10T10:00:00+00:00"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/api/meetings/" -Method Post -Body $body -ContentType "application/json"
```

**Mac/Linux:**
```bash
curl -X POST http://localhost:8000/api/meetings/ \
  -H "Content-Type: application/json" \
  -d '{
    "title": "My First Meeting",
    "description": "Testing Docker",
    "start_time": "2025-12-10T09:00:00+00:00",
    "end_time": "2025-12-10T10:00:00+00:00"
  }'
```

### Using Postman:

1. Create new request
2. Set to `POST`
3. URL: `http://localhost:8000/api/meetings/`
4. Go to "Body" tab
5. Select "raw" and "JSON"
6. Paste:
```json
{
  "title": "My First Meeting",
  "description": "Testing Docker",
  "start_time": "2025-12-10T09:00:00+00:00",
  "end_time": "2025-12-10T10:00:00+00:00"
}
```
7. Click "Send"

**You should get a response with the created meeting including an ID!**

---

## Step 7: View Your Meeting 👀

Go back to your browser:
```
http://localhost:8000/api/meetings/
```

You should now see your meeting in the list!

---

## Step 8: Stop the Application 🛑

Go back to the terminal where `docker-compose up` is running.

Press: **Ctrl + C**

You'll see:
```
Gracefully stopping... (press Ctrl+C again to force)
[+] Stopping 1/1
 ✔ Container meeting-scheduler  Stopped
```

To completely clean up:
```bash
docker-compose down
```

---

## 🎉 Congratulations!

You've successfully:
- ✅ Installed Docker
- ✅ Started the Meeting Scheduler in a container
- ✅ Created your first meeting via API
- ✅ Stopped the application

---

## What's Next?

### Run in Background (Detached Mode)
```bash
docker-compose up -d
```

Now you can close the terminal and the app keeps running!

To stop:
```bash
docker-compose down
```

### View Logs
```bash
docker-compose logs
```

### Follow Logs in Real-Time
```bash
docker-compose logs -f
```

### Run Tests
```bash
docker-compose exec web python manage.py test
```

### Access Container Shell
```bash
docker-compose exec web /bin/bash
```

---

## Common Issues & Solutions

### ❌ "Cannot connect to Docker daemon"
**Solution:** Make sure Docker Desktop is running (look for whale icon 🐳)

### ❌ "Port 8000 is already in use"
**Solution:** Stop other applications using port 8000, or edit `docker-compose.yml`:
```yaml
ports:
  - "8001:8000"  # Change 8000 to 8001
```
Then access at `http://localhost:8001`

### ❌ "docker-compose: command not found"
**Solution:** 
- Make sure Docker Desktop is installed and running
- Try `docker compose` (without hyphen) instead

### ❌ Changes to code not showing up
**Solution:** Rebuild the container:
```bash
docker-compose down
docker-compose build
docker-compose up
```

---

## Useful Commands Cheat Sheet

| What You Want | Command |
|---------------|---------|
| Start app | `docker-compose up` |
| Start in background | `docker-compose up -d` |
| Stop app | `Ctrl+C` or `docker-compose down` |
| View logs | `docker-compose logs` |
| Rebuild after changes | `docker-compose build` |
| See running containers | `docker ps` |
| Remove everything | `docker-compose down -v` |

---

## Need More Help?

- 📖 Read: `DOCKER_BEGINNER_GUIDE.md` for detailed explanations
- 📖 Read: `API_TESTING_GUIDE.md` for API documentation
- 🌐 Visit: https://docs.docker.com/get-started/

---

## Summary

**To run the app anytime:**

```bash
# 1. Open terminal
cd C:\dev\django\Test-projects\meetingscheduler

# 2. Start
docker-compose up

# 3. Open browser
http://localhost:8000/api/meetings/

# 4. Stop
Ctrl+C
```

**That's it! 🎊**
