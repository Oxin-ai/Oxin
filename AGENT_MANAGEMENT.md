# Agent Management MySQL Implementation

This implementation replaces the Redis-based agent storage with a secure, tenant-isolated MySQL database system following the same pattern as the existing auth system.

## Key Features

### Security & Tenant Isolation
- **Tenant-scoped access**: All agents belong to a specific tenant
- **User ownership tracking**: Track who created each agent
- **Soft delete**: Agents are marked as deleted, not permanently removed
- **UUID-based external IDs**: Prevents ID enumeration attacks

### Database Schema

#### `agents` table
- Primary agent metadata and ownership
- Tenant isolation via `tenant_id` foreign key
- Soft delete support with `status` and `deleted_at`

#### `agent_configurations` table  
- Stores agent configuration JSON with versioning
- Links to agents via foreign key
- Supports multiple versions with `is_active` flag

#### `agent_prompts` table
- Stores agent prompts with versioning
- Replaces local file storage for consistency
- Links to agents via foreign key

## API Changes

### New Endpoints (Secure)
- `POST /agent` - Create agent (tenant-scoped)
- `GET /agent/{agent_id}` - Get agent (tenant-scoped)
- `PUT /agent/{agent_id}` - Update agent (tenant-scoped)
- `DELETE /agent/{agent_id}` - Soft delete agent (tenant-scoped)
- `GET /agent` - List tenant agents (replaces unsafe `/all`)

### Security Improvements
- All endpoints require JWT authentication
- Automatic tenant isolation via `current_user.tenant_id`
- No cross-tenant data access possible
- Input validation via Pydantic models

## Migration Steps

1. **Create tables**:
   ```bash
   python create_agent_tables.py
   ```

2. **Update server**: The main server now uses `agent_router` instead of inline endpoints

3. **Test implementation**:
   ```bash
   python test_agent_management.py
   ```

## Backward Compatibility

The WebSocket endpoint includes Redis fallback during migration:
- First tries MySQL database
- Falls back to Redis if agent not found in MySQL
- Allows gradual migration of existing agents

## Production Considerations

### Required Environment Variables
- MySQL connection settings (same as auth system)
- Redis URL (for caching and fallback)

### Security Notes
- WebSocket endpoint needs authentication (TODO)
- Consider rate limiting on agent operations
- Implement proper role-based permissions within tenants

### Performance
- Database indexes on tenant_id + uuid for fast lookups
- Redis caching can be added for frequently accessed agents
- Connection pooling configured in database.py

## File Structure

```
bolna/agent_management/
├── __init__.py          # Module exports
├── models.py            # SQLAlchemy models
├── routes.py            # FastAPI endpoints
└── service.py           # Database operations
```

## Usage Example

```python
# The system automatically handles tenant isolation
# Users can only access agents within their tenant

# Create agent
POST /agent
{
  "agent_config": {...},
  "agent_prompts": {...}
}

# Get agent (only if user owns it or is in same tenant)
GET /agent/{uuid}

# List all agents in user's tenant
GET /agent
```

This implementation provides a secure, scalable foundation for agent management that prevents the security issues present in the Redis-based system.