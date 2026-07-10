# Log Sources Management Implementation

## Overview
Implemented complete log sources management functionality for SecMon Linux Security, allowing dynamic management of log sources with default entries for common Linux log files.

## Files Created/Modified

### 1. Database Migration
**File:** `database/migrations/006_log_sources_defaults.sql`

- Creates default log sources:
  - SSH Journal (/var/log/auth.log) - SSH log parser
  - Privileged Logs (/var/log/authpriv.log) - System privileged logs
  - Secure Logs (/var/log/secure) - Security-focused logs
- Creates indexes for faster queries on status, last_scanned, and parser_type

### 2. Service Layer
**File:** `backend/services/log_sources.py`

Complete service implementation with the following methods:

#### Core CRUD Operations
- `create_log_source(name, device_path, parser_type, status)` - Create new log source
- `get_log_source(log_source_id)` - Get log source by ID
- `get_log_source_by_name(name)` - Get log source by name
- `get_all_log_sources()` - List all log sources
- `update_log_source(log_source_id, name, device_path, parser_type, status)` - Update existing log source
- `delete_log_source(log_source_id)` - Delete a log source

#### Timestamp Management
- `set_last_scanned(log_source_id, timestamp)` - Update the last scanned timestamp

#### Default Sources
- `get_default_log_sources()` - Get default log source definitions without creating them
- `ensure_default_log_sources_exist()` - Create default sources if they don't exist

### 3. Model Updates
**File:** `backend/models/__init__.py`

Added new Pydantic models:
- `LogSourcesCreate` - Request model for creating log sources
- `LogSourcesUpdate` - Request model for updating log sources

### 4. Tests
**File:** `tests/test_log_sources.py`

Comprehensive test suite covering:
- Creating log sources (with validation for duplicate names)
- Getting log sources by ID and name
- Listing all log sources
- Updating log sources (full and partial updates)
- Deleting log sources
- Setting last scanned timestamps
- Ensuring default log sources exist
- Verifying default source properties

### 5. Manual Test Script
**File:** `test_log_sources_manual.py`

Interactive test script to verify all functionality manually.

## Database Schema

The `log_sources` table is already defined in the initial migration (`001_initial.sql`):

```sql
CREATE TABLE IF NOT EXISTS log_sources (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    device_path TEXT,
    parser_type TEXT,
    status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'error')),
    last_scanned TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

## Features Implemented

### 1. Table Structure ✓
- ID (auto-increment primary key)
- Name (unique, required)
- Device Path (path to log file/device)
- Parser Type (type of parser to use)
- Status (active/inactive/error, with CHECK constraint)
- Last Scanned (timestamp)
- Created At (timestamp)

### 2. Default Entries ✓
- SSH Journal (/var/log/auth.log) with SSH parser
- Privileged Logs (/var/log/authpriv.log) with syslog parser
- Secure Logs (/var/log/secure) with syslog parser

### 3. Dynamic Source Management ✓
- Create new log sources programmatically
- Update existing sources (full or partial updates)
- Delete log sources
- Query by ID or name
- List all sources

### 4. Last Scan Tracking ✓
- Automatic timestamp tracking for scans
- Update last_scanned when logs are processed
- Support for custom timestamps

## Usage Examples

### Basic Usage
```python
from backend.services.log_sources import LogSourcesService
from pathlib import Path

# Initialize service
service = LogSourcesService(database_path)

# Ensure defaults exist
service.ensure_default_log_sources_exist()

# Create a new log source
log_source_id = service.create_log_source(
    name="Custom SSH",
    device_path="/var/log/custom_ssh.log",
    parser_type="ssh",
    status="active"
)

# Get all sources
sources = service.get_all_log_sources()

# Update a source
service.update_log_source(log_source_id, status="inactive")

# Set last scanned
service.set_last_scanned(log_source_id)

# Delete a source
service.delete_log_source(log_source_id)
```

### Running the Tests
```bash
# Run comprehensive test suite
python -m pytest tests/test_log_sources.py -v

# Run manual verification script
python test_log_sources_manual.py
```

## Notes

1. The database migration `006_log_sources_defaults.sql` should be run before using the service to ensure default sources exist.

2. Log source names must be unique (database constraint).

3. Status values are validated to only allow 'active', 'inactive', or 'error'.

4. The service uses the existing `Database` class for connection management with WAL mode and foreign key constraints.

5. All operations include proper error handling and rollback on failure.
