# Meeting Scheduler Workflow Rules

This document defines the workflow rules for the Meeting Scheduler application based on its current implementation and requirements.

## 1. Meeting Management Workflow Rules

### 1.1 Meeting Creation
- Meetings must have a title, start time, and end time
- End time must be after start time
- All meetings are stored with UUID primary keys
- Created meetings are automatically validated for time constraints
- New meetings are assigned creation and update timestamps

### 1.2 Meeting Retrieval
- Meetings can be retrieved individually by UUID
- All meetings can be listed with optional date range filtering
- Meetings are ordered chronologically by start time
- Retrieved meetings include associated participants

### 1.3 Meeting Updates
- Meetings can be fully updated (PUT) or partially updated (PATCH)
- Time validation is enforced on updates
- Update operations maintain data integrity
- Updated meetings refresh their timestamp

### 1.4 Meeting Deletion
- Deleting a meeting removes all associated participants
- Cascade deletion ensures data consistency
- Successful deletion returns 204 No Content status

## 2. Participant Management Workflow Rules

### 2.1 Adding Participants
- Participants must have a valid email and name
- Participants are associated with a specific meeting
- Duplicate participants (same email for same meeting) are prevented
- Adding participants returns the created participant details

### 2.2 Participant Validation
- Email addresses must be valid format
- Names cannot be empty
- Participants inherit meeting time zone context

### 2.3 Removing Participants
- Participants can be removed by email address
- Removal is specific to a meeting context
- Removing non-existent participants returns appropriate error
- Participant removal maintains meeting integrity

### 2.4 Participant Listing
- Meetings include their participant lists in detail responses
- Participants are indexed by email for performance

## 3. Conflict Detection Workflow Rules

### 3.1 Time Overlap Detection
- Meetings overlap if: start_A < end_B AND start_B < end_A
- Adjacent meetings (end time = start time) do not conflict
- Overlap detection works with datetime objects and dictionaries

### 3.2 Participant Conflict Checking
- Conflicts are checked per participant across all their meetings
- Current meeting can be excluded from conflict checks (for updates)
- Conflict detection is database-efficient with proper querying

### 3.3 Conflict Reporting
- Complete conflict reports include all participants with conflicts
- Reports show conflicting meetings with full details
- Participants without conflicts are omitted from reports
- Conflict status is boolean for quick assessment

## 4. ICS Export Workflow Rules

### 4.1 Calendar Generation
- Generated ICS files comply with RFC 5545 standard
- Events include UID, summary, description, and time details
- All timestamps are converted to UTC
- Calendar includes proper metadata (PRODID, VERSION)

### 4.2 Attendee Formatting
- Participants are formatted as ATTENDEE fields per RFC 5545
- Each attendee includes CN (common name), ROLE, and RSVP parameters
- Email addresses are formatted as mailto: URIs

### 4.3 File Delivery
- Exported files are delivered with proper MIME type (text/calendar)
- Filenames are sanitized for cross-platform compatibility
- Export includes Content-Disposition header for file download
- ICS content is UTF-8 encoded

## 5. API Endpoint Workflow Rules

### 5.1 RESTful Design
- All endpoints follow REST conventions
- Appropriate HTTP status codes for all responses
- JSON request/response format
- Consistent URL structure with plural nouns

### 5.2 Error Handling
- Comprehensive error responses with descriptive messages
- Standardized error format across all endpoints
- Specific error codes for different failure scenarios
- Internal server errors are gracefully handled

### 5.3 Data Validation
- Input validation at serializer level
- Database-level constraints for critical validations
- Clear error messages for validation failures
- Required field enforcement

### 5.4 Filtering and Querying
- Date range filtering for meetings and participant data
- URL-encoded parameters for special characters
- Chronological ordering of results
- Efficient database queries with proper indexing

## 6. Testing Workflow Rules

### 6.1 Test Coverage
- Unit tests cover all API endpoints
- Service layer tests for business logic
- Integration tests for end-to-end workflows
- Property-based tests for edge cases

### 6.2 Test Quality
- Tests verify both success and failure scenarios
- Mock external dependencies when appropriate
- Use realistic test data
- Validate response structures and content

### 6.3 Test Execution
- Tests can be run individually or as suite
- Verbose output available for debugging
- Tests clean up after themselves
- Continuous integration compatible

## 7. Deployment Workflow Rules

### 7.1 Containerization
- Application packaged as Docker container
- Multi-stage build for optimized image size
- Environment variables for configuration
- Health checks for service availability

### 7.2 Database Management
- Automatic migration on startup
- Persistent data storage with volume mounting
- SQLite database with configurable path
- Data integrity maintained across deployments

### 7.3 Environment Configuration
- Configurable through environment variables
- Sensible defaults for development
- Security-sensitive defaults for production
- Port configuration flexibility

These workflow rules represent the current state and expected behavior of the Meeting Scheduler application. They should be referenced when making changes or additions to ensure consistency with the established patterns and requirements.