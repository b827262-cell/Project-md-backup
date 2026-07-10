# Log Sources Management - API Reference

## Service Class
```python
class LogSourcesService:
    """Service for managing log sources."""
```

## Methods

### Create Log Source
```python
def create_log_source(
    name: str,
    device_path: str,
    parser_type: str,
    status: str = "active"
) -> int
```

Creates a new log source.

**Parameters:**
- `name` (str): Log source name (must be unique)
- `device_path` (str): Path to the log file/device
- `parser_type` (str): Type of parser to use
- `status` (str): Status of the log source ('active', 'inactive', 'error')

**Returns:** int - ID of the created log source

**Raises:** RuntimeError if name already exists

**Example:**
```python
service = LogSourcesService(db_path)
source_id = service.create_log_source(
    name="My SSH Logs",
    device_path="/var/log/my_ssh.log",
    parser_type="ssh",
    status="active"
)
```

---

### Get Log Source by ID
```python
def get_log_source(log_source_id: int) -> Optional[LogSource]
```

Retrieves a log source by its ID.

**Parameters:**
- `log_source_id` (int): Log source ID

**Returns:** LogSource object or None if not found

**Example:**
```python
source = service.get_log_source(1)
if source:
    print(f"Source: {source.name}")
```

---

### Get Log Source by Name
```python
def get_log_source_by_name(name: str) -> Optional[LogSource]
```

Retrieves a log source by its name.

**Parameters:**
- `name` (str): Log source name

**Returns:** LogSource object or None if not found

**Example:**
```python
source = service.get_log_source_by_name("SSH Journal")
```

---

### Get All Log Sources
```python
def get_all_log_sources() -> List[LogSource]
```

Retrieves all log sources ordered by ID.

**Returns:** List of LogSource objects

**Example:**
```python
sources = service.get_all_log_sources()
for source in sources:
    print(f"{source.name}: {source.device_path}")
```

---

### Update Log Source
```python
def update_log_source(
    log_source_id: int,
    name: Optional[str] = None,
    device_path: Optional[str] = None,
    parser_type: Optional[str] = None,
    status: Optional[str] = None
) -> bool
```

Updates a log source with provided fields.

**Parameters:**
- `log_source_id` (int): Log source ID
- `name` (Optional[str]): New name (optional)
- `device_path` (Optional[str]): New device path (optional)
- `parser_type` (Optional[str]): New parser type (optional)
- `status` (Optional[str]): New status (optional)

**Returns:** True if updated successfully, False otherwise

**Example:**
```python
# Update status and name
service.update_log_source(1, name="New Name", status="inactive")

# Only update device path
service.update_log_source(1, device_path="/var/log/new_path.log")
```

---

### Delete Log Source
```python
def delete_log_source(log_source_id: int) -> bool
```

Deletes a log source.

**Parameters:**
- `log_source_id` (int): Log source ID

**Returns:** True if deleted successfully, False otherwise

**Example:**
```python
success = service.delete_log_source(1)
if success:
    print("Log source deleted")
```

---

### Set Last Scanned Timestamp
```python
def set_last_scanned(
    log_source_id: int,
    timestamp: Optional[datetime] = None
) -> bool
```

Updates the last scanned timestamp for a log source.

**Parameters:**
- `log_source_id` (int): Log source ID
- `timestamp` (Optional[datetime]): Timestamp to set (defaults to now)

**Returns:** True if updated successfully, False otherwise

**Example:**
```python
from datetime import datetime

# Set to specific time
service.set_last_scanned(1, datetime(2024, 1, 1, 12, 30, 45))

# Set to now
service.set_last_scanned(1)
```

---

### Get Default Log Sources
```python
def get_default_log_sources() -> List[LogSource]
```

Retrieves default log source definitions without creating them.

**Returns:** List of LogSource objects (SSH Journal, Privileged Logs, Secure Logs)

**Example:**
```python
defaults = service.get_default_log_sources()
for source in defaults:
    print(f"{source.name}: {source.device_path}")
```

---

### Ensure Default Log Sources Exist
```python
def ensure_default_log_sources_exist() -> List[LogSource]
```

Creates default log sources if they don't already exist.

**Returns:** List of all log sources after creation

**Example:**
```python
service.ensure_default_log_sources_exist()
sources = service.get_all_log_sources()
```

## Data Models

### LogSource
```python
class LogSource(BaseModel):
    id: int
    name: str
    source_type: str        # device_path
    source_path: str | None
    config_json: str | None
    enabled: int
    status: str
    last_event_at: str | None
    last_error: str | None
    events_today: int
    parse_errors_today: int
    created_at: str
    updated_at: str
```

### LogSourcesCreate
```python
class LogSourcesCreate(BaseModel):
    name: str
    device_path: str
    parser_type: str
    status: str = "active"
```

### LogSourcesUpdate
```python
class LogSourcesUpdate(BaseModel):
    name: Optional[str] = None
    device_path: Optional[str] = None
    parser_type: Optional[str] = None
    status: Optional[str] = None
```

## Status Values

Valid status values for log sources:
- `'active'` - Log source is active and collecting logs
- `'inactive'` - Log source is disabled
- `'error'` - Log source has encountered errors

## Database Schema

```sql
CREATE TABLE log_sources (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    device_path TEXT,
    parser_type TEXT,
    status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'error')),
    last_scanned TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

## Default Log Sources

The following default log sources are created:

1. **SSH Journal**
   - Path: `/var/log/auth.log`
   - Parser: `ssh`
   - Status: `active`

2. **Privileged Logs**
   - Path: `/var/log/authpriv.log`
   - Parser: `syslog`
   - Status: `active`

3. **Secure Logs**
   - Path: `/var/log/secure`
   - Parser: `syslog`
   - Status: `active`
