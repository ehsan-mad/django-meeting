# Docker Beginner's Guide for Meeting Scheduler

## What is Docker?

Docker is a tool that packages your application and all its dependencies into a "container" - think of it like a portable box that contains everything your app needs to run. This means:
- ✅ No "it works on my machine" problems
- ✅ Easy to share and deploy
- ✅ Consistent environment everywhere

## Prerequisites

### Step 1: Install Docker Desktop

**For Windows:**
1. Download Docker Desktop from: https://www.docker.com/products/docker-desktop
2. Run the installer
3. Restart your computer when prompted
4. Open Docker Desktop - you should see a whale icon in your system tray

**For Mac:**
1. Download Docker Desktop for Mac from the same link
2. Drag Docker.app to Applications folder
3. Open Docker Desktop

**For Linux:**
Follow instructions at: https://docs.docker.com/engine/install/

### Step 2: Verify Docker is Installed

Open your terminal (Command Prompt, PowerShell, or Terminal) and run:

```bash
docker --version
```

You should see something like: `Docker version 24.0.x`

Also check docker-compose:

```bash
docker-compose --version
```

You should see: `Docker Compose version v2.x.x`

---

## Running the Meeting Scheduler with Docker

### Method 1: Using Docker Compose (Easiest! ⭐ Recommended)

Docker Compose lets you start everything with one command.

#### Step 1: Navigate to Project Directory

Open your terminal and go to the project folder:

```bash
cd C:\dev\django\Test-projects\meetingscheduler
```

#### Step 2: Start the Application

Run this single command:

```bash
docker-compose up
```

**What happens:**
- Docker downloads Python and dependencies (first time only - takes a few minutes)
- Creates a container for your application
- Runs database migrations automatically
- Starts the Django server on port 8000

**You'll see logs like:**
```
meeting-scheduler-1  | Starting development server at http://0.0.0.0:8000/
meeting-scheduler-1  | Quit the server with CONTROL-C.
```

#### Step 3: Access the Application

Open your browser and go to:
```
http://localhost:8000/api/meetings/
```

You should see the API response!

#### Step 4: Stop the Application

Press `Ctrl+C` in the terminal where docker-compose is running.

To completely stop and remove containers:

```bash
docker-compose down
```

---

### Method 2: Using Docker Directly (More Control)

If you want more control, you can use Docker commands directly.

#### Step 1: Build the Docker Image

```bash
docker build -t meeting-scheduler .
```

**What this does:**
- `-t meeting-scheduler` gives your image a name
- `.` means use the Dockerfile in the current directory

**First time:** Takes 2-5 minutes to download Python and install dependencies

#### Step 2: Run the Container

```bash
docker run -p 8000:8000 -v "%cd%/data:/data" meeting-scheduler
```

**What this does:**
- `-p 8000:8000` maps port 8000 from container to your computer
- `-v "%cd%/data:/data"` saves the database on your computer (so data persists)
- `meeting-scheduler` is the image name we created

**For Mac/Linux, use:**
```bash
docker run -p 8000:8000 -v "$(pwd)/data:/data" meeting-scheduler
```

#### Step 3: Access the Application

Open your browser:
```
http://localhost:8000/api/meetings/
```

#### Step 4: Stop the Container

Press `Ctrl+C` in the terminal.

---

## Common Docker Commands

### See Running Containers
```bash
docker ps
```

### See All Containers (including stopped)
```bash
docker ps -a
```

### Stop a Running Container
```bash
docker stop <container-id>
```

### Remove a Container
```bash
docker rm <container-id>
```

### See Docker Images
```bash
docker images
```

### Remove an Image
```bash
docker rmi meeting-scheduler
```

### View Container Logs
```bash
docker logs <container-id>
```

### Access Container Shell (for debugging)
```bash
docker exec -it <container-id> /bin/bash
```

---

## Testing the API with Docker Running

Once Docker is running, you can test the API:

### Using cURL (Command Line)

**Create a Meeting:**
```bash
curl -X POST http://localhost:8000/api/meetings/ ^
  -H "Content-Type: application/json" ^
  -d "{\"title\": \"Team Standup\", \"description\": \"Daily standup\", \"start_time\": \"2025-12-10T09:00:00+00:00\", \"end_time\": \"2025-12-10T10:00:00+00:00\"}"
```

**List Meetings:**
```bash
curl http://localhost:8000/api/meetings/
```

### Using Postman

1. Open Postman
2. Create a new request
3. Set URL to: `http://localhost:8000/api/meetings/`
4. Choose method (GET, POST, etc.)
5. For POST, add JSON body in the "Body" tab
6. Click "Send"

### Using Python Script

Run the test script:
```bash
python test_api_endpoints.py
```

---

## Troubleshooting

### Problem: "Docker daemon is not running"

**Solution:** Start Docker Desktop application

### Problem: "Port 8000 is already in use"

**Solution:** Stop any other application using port 8000, or change the port:

```bash
docker-compose up
# Edit docker-compose.yml and change "8000:8000" to "8001:8000"
# Then access at http://localhost:8001
```

### Problem: "Cannot connect to Docker daemon"

**Solution:** 
- Make sure Docker Desktop is running
- On Windows, you might need to enable WSL 2
- Restart Docker Desktop

### Problem: Changes to code not reflected

**Solution:** Rebuild the image:

```bash
docker-compose down
docker-compose build --no-cache
docker-compose up
```

### Problem: Database data lost after restart

**Solution:** Make sure you're using volumes:

```bash
# With docker-compose (automatic)
docker-compose up

# With docker run (manual)
docker run -p 8000:8000 -v "%cd%/data:/data" meeting-scheduler
```

---

## Understanding the Files

### Dockerfile
- Recipe for building your Docker image
- Specifies Python version, dependencies, and how to run the app

### docker-compose.yml
- Configuration for running multiple containers
- Easier than remembering long docker commands
- Handles volumes, ports, and environment variables

### .dockerignore
- Lists files Docker should ignore when building
- Similar to .gitignore

---

## Quick Reference Card

| Task | Command |
|------|---------|
| Start app | `docker-compose up` |
| Start in background | `docker-compose up -d` |
| Stop app | `docker-compose down` |
| View logs | `docker-compose logs` |
| Rebuild after code changes | `docker-compose build` |
| Run migrations | `docker-compose exec web python manage.py migrate` |
| Create superuser | `docker-compose exec web python manage.py createsuperuser` |
| Run tests | `docker-compose exec web python manage.py test` |
| Access shell | `docker-compose exec web /bin/bash` |

---

## Next Steps

1. ✅ Install Docker Desktop
2. ✅ Run `docker-compose up`
3. ✅ Open http://localhost:8000/api/meetings/
4. ✅ Test the API with Postman or cURL
5. ✅ Read API_TESTING_GUIDE.md for API documentation

---

## Getting Help

- Docker Documentation: https://docs.docker.com/
- Docker Desktop Issues: https://github.com/docker/for-win/issues
- Django in Docker: https://docs.docker.com/samples/django/

---

## Summary

**To run the Meeting Scheduler:**

```bash
# 1. Open terminal in project directory
cd C:\dev\django\Test-projects\meetingscheduler

# 2. Start with one command
docker-compose up

# 3. Open browser
# http://localhost:8000/api/meetings/

# 4. Stop when done
# Press Ctrl+C
```

That's it! Docker makes it easy to run the application without installing Python, Django, or any dependencies on your computer. Everything runs in an isolated container.
