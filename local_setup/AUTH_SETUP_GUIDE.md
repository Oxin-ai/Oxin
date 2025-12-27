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

Create the authentication tables (tenants and users tables):

```bash
cd local_setup
docker-compose exec bolna-app python -m bolna.auth.init_db
```

**Expected Output:**
```
INFO: Database tables created successfully
```

This creates the following tables:

**`tenants` table:**
- `id` (Primary Key)
- `name` (Required)
- `slug` (Unique, Indexed, URL-friendly)
- `is_active` (Default: true)
- `created_at` (Timestamp)

**`users` table:**
- `id` (Primary Key)
- `email` (Unique, Indexed)
- `hashed_password`
- `tenant_id` (Foreign Key → tenants.id, Required)
- `role` (Default: "user")
- `is_active` (Default: true)
- `created_at` (Timestamp)

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

### Step 7: Test User Signup (with Tenant Creation)

Create a new tenant and user account. The signup process automatically:
1. Creates a new tenant with the provided tenant name
2. Generates a unique slug from the tenant name
3. Creates the first user with role "owner"
4. Returns a JWT token with tenant context

**Using curl:**
```bash
curl -X POST "http://localhost:5001/auth/signup" \
  -H "Content-Type: application/json" \
  -d '{
    "tenant_name": "Acme Corporation",
    "email": "owner@acme.com",
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
  "tenant_name": "Acme Corporation",
  "email": "owner@acme.com",
  "password": "SecurePassword123!"
}
```

**Expected Response (201 Created):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJlbWFpbCI6Im93bmVyQGFjbWUuY29tIiwidGVuYW50X2lkIjoxLCJyb2xlIjoib3duZXIiLCJleHAiOjE3MDUwNzI3MTAsImlhdCI6MTcwNTA2OTEwMH0...",
  "token_type": "bearer"
}
```

**JWT Token Payload (decoded):**
The JWT token contains:
- `user_id`: User's unique identifier
- `email`: User's email address
- `tenant_id`: Tenant's unique identifier
- `role`: User's role (will be "owner" for signup)
- `exp`: Token expiration timestamp
- `iat`: Token issued at timestamp

**Error Cases:**
- **400 Bad Request**: Email already registered
- **422 Validation Error**: Invalid email format or missing fields (tenant_name, email, password)

**Note:** Each signup creates a new tenant. If you want to add users to an existing tenant, use a separate endpoint (not included in this implementation).

### Step 8: Test User Login

Authenticate and get JWT token with tenant context:

**Using curl:**
```bash
curl -X POST "http://localhost:5001/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "owner@acme.com",
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
  "email": "owner@acme.com",
  "password": "SecurePassword123!"
}
```

**Expected Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJlbWFpbCI6Im93bmVyQGFjbWUuY29tIiwidGVuYW50X2lkIjoxLCJyb2xlIjoib3duZXIiLCJleHAiOjE3MDUwNzI3MTAsImlhdCI6MTcwNTA2OTEwMH0...",
  "token_type": "bearer"
}
```

**JWT Token Payload (decoded):**
The JWT token contains:
- `user_id`: User's unique identifier
- `email`: User's email address
- `tenant_id`: User's tenant identifier
- `role`: User's role (e.g., "owner", "user")
- `exp`: Token expiration timestamp
- `iat`: Token issued at timestamp

**Error Cases:**
- **401 Unauthorized**: Incorrect email or password
- **403 Forbidden**: User account is inactive
- **422 Validation Error**: Invalid email format or missing fields

### Step 9: Verify JWT Token Contains Tenant Context

You can decode and verify the JWT token to confirm it contains tenant information:

**Using Online JWT Decoder:**
1. Copy the `access_token` from the signup/login response
2. Visit https://jwt.io
3. Paste the token in the "Encoded" section
4. Verify the payload contains:
   - `user_id`
   - `email`
   - `tenant_id` (should be present)
   - `role` (should be "owner" for signup)

**Using Python (in container):**
```bash
# Access container shell
docker-compose exec bolna-app python

# In Python shell:
from bolna.auth.security import decode_access_token
token = "your_token_here"
payload = decode_access_token(token)
print(payload)
# Should show: {'user_id': 1, 'email': 'owner@acme.com', 'tenant_id': 1, 'role': 'owner', 'exp': ..., 'iat': ...}
```

**Using curl with jq (if installed):**
```bash
# Login and extract token
RESPONSE=$(curl -s -X POST "http://localhost:5001/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "owner@acme.com", "password": "SecurePassword123!"}')

TOKEN=$(echo $RESPONSE | jq -r '.access_token')

# Decode token (requires base64 and jq)
echo $TOKEN | cut -d. -f2 | base64 -d 2>/dev/null | jq .
```

### Step 10: Test Protected Endpoints

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

**Note:** The JWT token now includes `tenant_id` and `role` which can be used for tenant isolation and role-based access control in future implementations.

## Complete Test Flow Example

Here's a complete test flow using curl with tenant support:

```bash
# 1. Signup (creates tenant and user, returns JWT token)
SIGNUP_RESPONSE=$(curl -s -X POST "http://localhost:5001/auth/signup" \
  -H "Content-Type: application/json" \
  -d '{
    "tenant_name": "Test Company",
    "email": "test@example.com",
    "password": "testpass123"
  }')

echo "Signup Response: $SIGNUP_RESPONSE"

# Extract token from signup response
TOKEN=$(echo $SIGNUP_RESPONSE | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)
echo "Token: $TOKEN"

# 2. Login (alternative way to get token)
LOGIN_RESPONSE=$(curl -s -X POST "http://localhost:5001/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "testpass123"}')

echo "Login Response: $LOGIN_RESPONSE"

# Extract token from login response
TOKEN=$(echo $LOGIN_RESPONSE | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

# 3. Use token to access protected endpoint
curl -X GET "http://localhost:5001/all" \
  -H "Authorization: Bearer $TOKEN"

# 4. Verify token contains tenant_id (using Python in container)
docker-compose exec bolna-app python -c "
from bolna.auth.security import decode_access_token
import sys
token = sys.argv[1]
payload = decode_access_token(token)
print('Token Payload:', payload)
print('Tenant ID:', payload.get('tenant_id'))
print('Role:', payload.get('role'))
" "$TOKEN"
```

**Expected Output:**
```
Signup Response: {"access_token":"eyJ...","token_type":"bearer"}
Token: eyJ...
Login Response: {"access_token":"eyJ...","token_type":"bearer"}
Token Payload: {'user_id': 1, 'email': 'test@example.com', 'tenant_id': 1, 'role': 'owner', 'exp': ..., 'iat': ...}
Tenant ID: 1
Role: owner
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

### Issue: "Access denied for user 'bolna_user'@'...' (using password: YES)"

**Solution:**
- This error occurs when the MySQL user doesn't have permissions from the Docker network
- The user might exist but only have `localhost` permissions, not network permissions
- **Quick Fix:** Run the provided fix script:
  ```bash
  # On Windows (PowerShell)
  cd local_setup
  .\fix_mysql_permissions.ps1
  
  # On Linux/Mac
  cd local_setup
  chmod +x fix_mysql_permissions.sh
  ./fix_mysql_permissions.sh
  ```
- **Manual Fix:** Connect to MySQL as root and grant permissions:
  ```bash
  # Connect to MySQL container
  docker-compose exec mysql mysql -uroot -prootpassword
  
  # In MySQL prompt, run:
  CREATE USER IF NOT EXISTS 'bolna_user'@'%' IDENTIFIED BY 'bolna_password';
  GRANT ALL PRIVILEGES ON `bolna`.* TO 'bolna_user'@'%';
  CREATE USER IF NOT EXISTS 'bolna_user'@'localhost' IDENTIFIED BY 'bolna_password';
  GRANT ALL PRIVILEGES ON `bolna`.* TO 'bolna_user'@'localhost';
  FLUSH PRIVILEGES;
  EXIT;
  
  # Restart the application
  docker-compose restart bolna-app
  ```
- **Verify credentials:**
  ```bash
  # Check what user/password the app is trying to use
  docker-compose exec bolna-app env | grep MYSQL
  
  # Test MySQL connection manually (after database is created)
  docker-compose exec mysql mysql -u bolna_user -pbolna_password bolna -e "SELECT 1;"
  ```

### Issue: "Access denied for user 'root'@'...' (using password: YES)"

**Solution:**
- This error occurs when MySQL credentials don't match
- The application is trying to use `root` user but the password is incorrect
- **Recommended Fix:** Use the default `bolna_user` instead of `root`:
  1. Check your `.env` file in `local_setup/` directory
  2. Ensure it has:
     ```env
     MYSQL_USER=bolna_user
     MYSQL_PASSWORD=bolna_password
     ```
  3. Remove or comment out any `MYSQL_USER=root` line
  4. Restart the container: `docker-compose restart bolna-app`
- **Alternative:** If you must use `root`:
  1. Set `MYSQL_USER=root` in `.env`
  2. Set `MYSQL_PASSWORD` to match `MYSQL_ROOT_PASSWORD` (default: `rootpassword`)
  3. Restart: `docker-compose restart bolna-app`

### Issue: "JWT_SECRET environment variable is required"

**Solution:**
- Add `JWT_SECRET` to your `.env` file
- Restart the container: `docker-compose restart bolna-app`

### Issue: "Email already registered"

**Solution:**
- This is expected if the email already exists
- Use a different email or delete the existing user from the database
- Note: Each signup creates a new tenant. If you want to add users to an existing tenant, you'll need a separate endpoint (not included in this implementation)

### Issue: Tenant slug conflicts

**Solution:**
- The system automatically handles slug conflicts by appending numbers (e.g., "acme", "acme-1", "acme-2")
- Slugs are generated from tenant names and made URL-friendly
- If you see duplicate slug errors, check the database for existing tenants

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

- `POST /auth/signup` - Create new tenant and user account
  - **Request Body:**
    ```json
    {
      "tenant_name": "string (required)",
      "email": "string (required, valid email)",
      "password": "string (required)"
    }
    ```
  - **Response:** JWT token with `user_id`, `email`, `tenant_id`, and `role` (owner)
  
- `POST /auth/login` - Authenticate and get JWT token
  - **Request Body:**
    ```json
    {
      "email": "string (required, valid email)",
      "password": "string (required)"
    }
    ```
  - **Response:** JWT token with `user_id`, `email`, `tenant_id`, and `role`

### Protected Endpoints (Require JWT Token)

- `GET /agent/{agent_id}` - Get agent by ID
- `POST /agent` - Create new agent
- `PUT /agent/{agent_id}` - Update agent
- `DELETE /agent/{agent_id}` - Delete agent
- `GET /all` - Get all agents

**Note:** 
- All protected endpoints require the `Authorization: Bearer <token>` header
- JWT tokens now include `tenant_id` and `role` for tenant isolation and role-based access control

## Security Notes

1. **JWT_SECRET**: Always use a strong, random secret in production
2. **Password**: Enforce strong password policies in production
3. **HTTPS**: Use HTTPS in production to protect tokens in transit
4. **Token Expiry**: Adjust `JWT_EXPIRE_MINUTES` based on your security requirements
5. **Database**: Use strong MySQL passwords in production

## Testing Multi-Tenancy

To verify multi-tenancy is working correctly:

1. **Create Multiple Tenants:**
   ```bash
   # Tenant 1
   curl -X POST "http://localhost:5001/auth/signup" \
     -H "Content-Type: application/json" \
     -d '{"tenant_name": "Company A", "email": "owner@companya.com", "password": "pass123"}'
   
   # Tenant 2
   curl -X POST "http://localhost:5001/auth/signup" \
     -H "Content-Type: application/json" \
     -d '{"tenant_name": "Company B", "email": "owner@companyb.com", "password": "pass123"}'
   ```

2. **Verify Different Tenant IDs:**
   - Login with each user and decode their JWT tokens
   - Confirm each token has a different `tenant_id`
   - Verify each user has `role: "owner"`

3. **Check Database:**
   ```bash
   # Access MySQL container
   docker-compose exec mysql mysql -u bolna_user -pbolna_password bolna
   
   # View tenants
   SELECT * FROM tenants;
   
   # View users with their tenant
   SELECT u.id, u.email, u.role, u.tenant_id, t.name as tenant_name 
   FROM users u 
   JOIN tenants t ON u.tenant_id = t.id;
   ```

## Next Steps

After successful authentication setup:

1. Integrate authentication into your frontend application
2. Implement token refresh mechanism (if needed)
3. Add tenant middleware to enforce tenant isolation on protected routes
4. Implement role-based access control (RBAC) using the `role` field
5. Add endpoints to manage users within a tenant (add users, change roles)
6. Set up proper logging and monitoring
7. Configure production database with proper backups

---

**For more information, refer to the main README.md or API documentation at `/docs` endpoint.**
