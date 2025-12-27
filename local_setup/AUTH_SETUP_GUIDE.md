# Authentication Setup Guide

This guide covers the complete setup process for the integrated authentication system in Bolna AI backend, from database initialization to testing the authentication APIs.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Environment Configuration](#environment-configuration)
3. [Database Setup](#database-setup)
4. [Running the Application](#running-the-application)
5. [Testing Authentication APIs](#testing-authentication-apis)
6. [Troubleshooting](#troubleshooting)

## Prerequisites

- Docker and Docker Compose installed
- Access to the project directory
- Basic knowledge of REST APIs and curl/Postman

## Environment Configuration

### Step 1: Create/Update `.env` File

Navigate to the `local_setup` directory and create or update the `.env` file with the following variables:

```bash
cd local_setup
```

Create or edit `.env` file:

```env
# MySQL Database Configuration
MYSQL_USER=bolna_user
MYSQL_PASSWORD=bolna_password
MYSQL_DB=bolna
MYSQL_ROOT_PASSWORD=rootpassword

# JWT Configuration
JWT_SECRET=your_secret_key_here_change_this_in_production
JWT_EXPIRE_MINUTES=1440

# Redis Configuration (if not already set)
REDIS_URL=redis://redis:6379/0

# Other existing environment variables...
```

**Important Notes:**
- `JWT_SECRET`: Use a strong, random secret key in production
- `MYSQL_HOST`: Will be automatically set to `mysql` by docker-compose.yml (no need to set in .env)
- The MySQL credentials should match what's configured in `docker-compose.yml`

## Database Setup

### Step 2: Start Docker Containers

Start all services including MySQL:

```bash
cd local_setup
docker-compose up -d
```

This will start:
- MySQL database service
- Redis service
- Bolna application service
- Other services (ngrok, telephony servers)

### Step 3: Wait for MySQL to be Ready

Wait for MySQL to fully initialize (usually takes 10-30 seconds). Check logs:

```bash
docker-compose logs mysql
```

Look for the message:
```
MySQL init process done. Ready for start up.
```

### Step 4: Initialize Database Tables

Create the authentication tables (users table):

```bash
cd local_setup
docker-compose exec bolna-app python -m bolna.auth.init_db
```

**Expected Output:**
```
INFO: Database tables created successfully
```

This creates the `users` table with the following structure:
- `id` (Primary Key)
- `email` (Unique, Indexed)
- `hashed_password`
- `is_active`
- `created_at`

## Running the Application

### Step 5: Verify Application is Running

Check if the bolna-app container is running:

```bash
docker-compose ps
```

Check application logs:

```bash
docker-compose logs bolna-app
```

**Expected Output:**
```
INFO:     Started server process [1]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:5001 (Press CTRL+C to quit)
```

### Step 6: Verify Application Health

The application should be accessible at:
- **Base URL**: `http://localhost:5001`
- **API Documentation**: `http://localhost:5001/docs` (FastAPI Swagger UI)

## Testing Authentication APIs

### Step 7: Test User Signup

Create a new user account:

**Using curl:**
```bash
curl -X POST "http://localhost:5001/auth/signup" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePassword123!"
  }'
```

**Using Postman:**
1. Method: `POST`
2. URL: `http://localhost:5001/auth/signup`
3. Headers: `Content-Type: application/json`
4. Body (raw JSON):
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!"
}
```

**Expected Response (201 Created):**
```json
{
  "id": 1,
  "email": "user@example.com",
  "is_active": true,
  "created_at": "2025-12-27T04:55:10.123456"
}
```

**Error Cases:**
- **400 Bad Request**: Email already registered
- **422 Validation Error**: Invalid email format or missing fields

### Step 8: Test User Login

Authenticate and get JWT token:

**Using curl:**
```bash
curl -X POST "http://localhost:5001/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePassword123!"
  }'
```

**Using Postman:**
1. Method: `POST`
2. URL: `http://localhost:5001/auth/login`
3. Headers: `Content-Type: application/json`
4. Body (raw JSON):
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!"
}
```

**Expected Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Error Cases:**
- **401 Unauthorized**: Incorrect email or password
- **403 Forbidden**: User account is inactive
- **422 Validation Error**: Invalid email format or missing fields

### Step 9: Test Protected Endpoints

Use the JWT token to access protected routes:

**Using curl:**
```bash
# Save the token from login response
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

# Test protected endpoint - Get all agents
curl -X GET "http://localhost:5001/all" \
  -H "Authorization: Bearer $TOKEN"

# Test protected endpoint - Create agent
curl -X POST "http://localhost:5001/agent" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "agent_config": { ... },
    "agent_prompts": { ... }
  }'
```

**Using Postman:**
1. Add Authorization Header:
   - Type: `Bearer Token`
   - Token: `<paste_token_from_login_response>`
2. Make requests to protected endpoints:
   - `GET /all` - Get all agents
   - `GET /agent/{agent_id}` - Get specific agent
   - `POST /agent` - Create new agent
   - `PUT /agent/{agent_id}` - Update agent
   - `DELETE /agent/{agent_id}` - Delete agent

**Expected Behavior:**
- **200 OK**: Request successful with valid token
- **401 Unauthorized**: Missing or invalid token
- **403 Forbidden**: User account is inactive

## Complete Test Flow Example

Here's a complete test flow using curl:

```bash
# 1. Signup
curl -X POST "http://localhost:5001/auth/signup" \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "testpass123"}'

# 2. Login and save token
RESPONSE=$(curl -s -X POST "http://localhost:5001/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "testpass123"}')

TOKEN=$(echo $RESPONSE | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

# 3. Use token to access protected endpoint
curl -X GET "http://localhost:5001/all" \
  -H "Authorization: Bearer $TOKEN"
```

## Troubleshooting

### Issue: "Can't connect to MySQL server on 'localhost'"

**Solution:**
- Ensure MySQL service is running: `docker-compose ps mysql`
- Check MySQL logs: `docker-compose logs mysql`
- Verify `MYSQL_HOST` is set to `mysql` in docker-compose.yml
- Restart containers: `docker-compose restart bolna-app`

### Issue: "Database tables created successfully" but signup fails

**Solution:**
- Verify database connection: Check `docker-compose logs bolna-app` for connection errors
- Ensure MySQL is fully initialized before running init_db
- Check MySQL credentials match in `.env` and `docker-compose.yml`

### Issue: "JWT_SECRET environment variable is required"

**Solution:**
- Add `JWT_SECRET` to your `.env` file
- Restart the container: `docker-compose restart bolna-app`

### Issue: "Email already registered"

**Solution:**
- This is expected if the email already exists
- Use a different email or delete the existing user from the database

### Issue: "401 Unauthorized" on protected endpoints

**Solution:**
- Verify the token is included in the Authorization header
- Check token format: `Bearer <token>`
- Ensure token hasn't expired (default: 24 hours)
- Login again to get a new token

### Issue: Container won't start

**Solution:**
- Rebuild the container: `docker-compose build bolna-app`
- Check for port conflicts: Ensure port 5001 is available
- View detailed logs: `docker-compose logs bolna-app`

## Quick Reference Commands

```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# View logs
docker-compose logs -f bolna-app

# Restart a specific service
docker-compose restart bolna-app

# Rebuild and restart
docker-compose build bolna-app
docker-compose up -d

# Initialize database
docker-compose exec bolna-app python -m bolna.auth.init_db

# Access container shell
docker-compose exec bolna-app bash

# Check service status
docker-compose ps
```

## API Endpoints Summary

### Public Endpoints (No Authentication Required)

- `POST /auth/signup` - Create new user account
- `POST /auth/login` - Authenticate and get JWT token

### Protected Endpoints (Require JWT Token)

- `GET /agent/{agent_id}` - Get agent by ID
- `POST /agent` - Create new agent
- `PUT /agent/{agent_id}` - Update agent
- `DELETE /agent/{agent_id}` - Delete agent
- `GET /all` - Get all agents

**Note:** All protected endpoints require the `Authorization: Bearer <token>` header.

## Security Notes

1. **JWT_SECRET**: Always use a strong, random secret in production
2. **Password**: Enforce strong password policies in production
3. **HTTPS**: Use HTTPS in production to protect tokens in transit
4. **Token Expiry**: Adjust `JWT_EXPIRE_MINUTES` based on your security requirements
5. **Database**: Use strong MySQL passwords in production

## Next Steps

After successful authentication setup:

1. Integrate authentication into your frontend application
2. Implement token refresh mechanism (if needed)
3. Add role-based access control (RBAC) if required
4. Set up proper logging and monitoring
5. Configure production database with proper backups

---

**For more information, refer to the main README.md or API documentation at `/docs` endpoint.**
