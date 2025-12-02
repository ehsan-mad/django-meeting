# Meeting Scheduler API

A Django REST API for managing meetings with participant management, conflict detection, and ICS calendar export functionality.

## Features

- ✅ **Meeting Management**: Create, read, update, and delete meetings
- ✅ **Participant Management**: Add and remove participants from meetings
- ✅ **Conflict Detection**: Automatically detect scheduling conflicts for participants
- ✅ **ICS Export**: Export meetings to ICS format for calendar applications
- ✅ **Date Filtering**: Filter meetings by date range
- ✅ **RESTful API**: Clean, well-documented REST API
- ✅ **Docker Support**: Containerized deployment with Docker and Docker Compose

## Quick Start

### Using Docker Compose (Recommended)

```bash
# Clone the repository
git clone <repository-url>
cd meetingscheduler

# Create environment file
cp .env.example .env

# Start the service
docker-compose up -d

# Access the API
curl http://localhost:8000/api/meetings/
```

### Manual Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Start development server
python manage.py runserver

# Access the API
curl http://localhost:8000/api/meetings/
```

## API Endpoints

### Meetings

- `POST /api/meetings/` - Create a new meeting
- `GET /api/meetings/` - List all meetings
- `GET /api/meetings/{id}/` - Get a specific meeting
- `PUT /api/meetings/{id}/` - Update a meeting
- `DELETE /api/meetings/{id}/` - Delete a meeting
- `GET /api/meetings/{id}/export/` - Export meeting as ICS file

### Participants

- `POST /api/meetings/{id}/participants/` - Add participant to meeting
- `DELETE /api/meetings/{id}/participants/{email}/` - Remove participant from meeting
- `GET /api/participants/{email}/meetings/` - Get all meetings for a participant
- `GET /api/participants/{email}/conflicts/` - Check conflicts for a participant

## Documentation

- **[API Testing Guide](./API_TESTING_GUIDE.md)** - Complete API documentation with examples
- **[Docker Compose Guide](./DOCKER_COMPOSE_GUIDE.md)** - Docker deployment guide
- **[Conflict Detection Testing](./CONFLICT_DETECTION_TESTING.md)** - Conflict detection examples

## Technology Stack

- **Framework**: Django 4.x + Django REST Framework
- **Database**: SQLite (easily replaceable with PostgreSQL/MySQL)
- **Calendar**: icalendar library for RFC 5545 compliance
- **Testing**: pytest + Hypothesis for property-based testing
- **Containerization**: Docker + Docker Compose

## Development

### Running Tests

```bash
# Run all tests
python manage.py test

# Run specific test class
python manage.py test meeting.tests.MeetingCRUDTestCase

# Run with coverage
pytest --cov=meeting
```

### Project Structure

```
meetingscheduler/
├── meeting/                 # Main application
│   ├── models.py           # Meeting and Participant models
│   ├── serializers.py      # DRF serializers
│   ├── views.py            # API views
│   ├── services.py         # Business logic (ConflictDetector, ICSGenerator)
│   ├── urls.py             # URL routing
│   └── tests.py            # Test suite
├── meetingscheduler/       # Django project settings
├── docker-compose.yml      # Docker Compose configuration
├── Dockerfile              # Docker image definition
├── requirements.txt        # Python dependencies
└── manage.py               # Django management script
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DJANGO_SECRET_KEY` | Django secret key | `dev-secret-key-change-in-production` |
| `DJANGO_DEBUG` | Debug mode | `True` |
| `DJANGO_ALLOWED_HOSTS` | Allowed hosts | `*` |
| `DATABASE_PATH` | Database file path | `/data/db.sqlite3` |
| `PORT` | Server port | `8000` |

## API Examples

### Create a Meeting

```bash
curl -X POST http://localhost:8000/api/meetings/ \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Team Standup",
    "description": "Daily standup meeting",
    "start_time": "2025-12-10T09:00:00+00:00",
    "end_time": "2025-12-10T09:30:00+00:00"
  }'
```

### Add Participant

```bash
curl -X POST http://localhost:8000/api/meetings/{meeting-id}/participants/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "alice@example.com",
    "name": "Alice Smith"
  }'
```

### Export to ICS

```bash
curl -X GET http://localhost:8000/api/meetings/{meeting-id}/export/ -o meeting.ics
```

### Check Conflicts

```bash
curl -X GET http://localhost:8000/api/participants/alice@example.com/conflicts/
```

## Requirements

### Functional Requirements

1. **Meeting Management**: CRUD operations for meetings
2. **Participant Management**: Add/remove participants with duplicate prevention
3. **Conflict Detection**: Identify scheduling overlaps for participants
4. **ICS Export**: RFC 5545 compliant calendar file generation
5. **Date Filtering**: Query meetings by date range
6. **Error Handling**: Comprehensive error responses

### Non-Functional Requirements

1. **Performance**: Efficient database queries with indexing
2. **Scalability**: Containerized for easy horizontal scaling
3. **Maintainability**: Clean code architecture with service layer
4. **Testability**: 60+ unit tests with 100% coverage of core logic
5. **Documentation**: Complete API documentation and guides

## Testing

The project includes comprehensive test coverage:

- **60+ Unit Tests**: Covering all API endpoints and business logic
- **Property-Based Tests**: Using Hypothesis for edge case discovery
- **Integration Tests**: End-to-end API workflow testing
- **Service Tests**: ConflictDetector and ICSGenerator validation

```bash
# Run all tests
python manage.py test

# Run with verbose output
python manage.py test -v 2

# Run specific test module
python manage.py test meeting.tests.ConflictDetectorTestCase
```

## Deployment

### Docker Compose (Recommended)

```bash
# Production deployment
docker-compose -f docker-compose.yml up -d

# View logs
docker-compose logs -f

# Stop service
docker-compose down
```

### Manual Deployment

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export DJANGO_DEBUG=False
export DJANGO_SECRET_KEY=your-secret-key
export DJANGO_ALLOWED_HOSTS=yourdomain.com

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Start with Gunicorn
gunicorn meetingscheduler.wsgi:application --bind 0.0.0.0:8000
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License.

## Support

For issues, questions, or contributions:
- Open an issue in the repository
- Check the documentation in the `docs/` folder
- Review the API Testing Guide for usage examples
