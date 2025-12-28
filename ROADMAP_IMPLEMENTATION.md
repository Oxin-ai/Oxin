# Bolna SaaS Implementation Roadmap

## 🎯 PHASE 1: Database Integration (Week 1)

### 1.1 Agent Management Database Migration
**Priority: HIGH**

**Current State:**
- Agents stored in Redis (no tenant isolation)
- `GET /all` returns all agents (security risk)
- No persistent agent metadata

**Target State:**
- Agents in MySQL with tenant isolation
- Proper ACL and ownership
- Version history tracking

**Implementation Steps:**

1. **Create Agent Service Layer**
```python
# File: bolna/services/agent_service.py
class AgentService:
    async def create_agent(self, tenant_id: int, user_id: int, agent_config: dict) -> Agent
    async def get_agent(self, tenant_id: int, agent_id: str) -> Agent
    async def list_agents(self, tenant_id: int) -> List[Agent]
    async def update_agent(self, tenant_id: int, agent_id: str, config: dict) -> Agent
    async def delete_agent(self, tenant_id: int, agent_id: str) -> bool
```

2. **Update API Endpoints**
```python
# File: local_setup/quickstart_server.py
# Replace Redis calls with AgentService calls
# Add tenant_id from JWT token to all operations
```

3. **Migration Script**
```python
# File: scripts/migrate_redis_to_db.py
# Move existing Redis agents to database
```

### 1.2 Call Management Integration
**Priority: HIGH**

**Current State:**
- Call data in CSV files
- No structured call history
- No real-time call status

**Target State:**
- Calls table with proper state machine
- Real-time call events
- Searchable call history

**Implementation Steps:**

1. **Create Call Service**
```python
# File: bolna/services/call_service.py
class CallService:
    async def create_call(self, tenant_id: int, agent_id: int, external_data: dict) -> Call
    async def update_call_status(self, call_id: int, status: str) -> Call
    async def add_call_event(self, call_id: int, event_type: str, payload: dict)
    async def get_call_history(self, tenant_id: int, filters: dict) -> List[Call]
```

2. **Integrate with TaskManager**
```python
# File: bolna/agent_manager/task_manager.py
# Add call_service.create_call() at start
# Add call_service.update_call_status() on state changes
# Add call_service.add_call_event() for major events
```

### 1.3 Transcript Storage
**Priority: MEDIUM**

**Implementation Steps:**

1. **Create Transcript Service**
```python
# File: bolna/services/transcript_service.py
class TranscriptService:
    async def store_transcript_chunk(self, call_id: int, speaker: str, text: str, timing: dict)
    async def get_call_transcript(self, call_id: int) -> List[Transcript]
```

2. **Integrate with Transcribers**
```python
# Update: bolna/transcriber/deepgram_transcriber.py
# Add transcript_service.store_transcript_chunk() calls
```

## 🎯 PHASE 2: Usage Tracking & Billing (Week 2)

### 2.1 Real-time Usage Tracking
**Priority: HIGH**

**Implementation Steps:**

1. **Create Usage Service**
```python
# File: bolna/services/usage_service.py
class UsageService:
    async def record_token_usage(self, tenant_id: int, call_id: int, tokens: int, cost: float)
    async def record_minute_usage(self, tenant_id: int, call_id: int, minutes: float, cost: float)
    async def get_tenant_usage(self, tenant_id: int, date_range: tuple) -> dict
```

2. **Add Usage Middleware**
```python
# File: bolna/middleware/usage_middleware.py
# Intercept LLM calls and record token usage
# Intercept call duration and record minute usage
```

3. **Integrate with Providers**
```python
# Update: bolna/llms/openai_llm.py, bolna/llms/litellm.py
# Add usage_service.record_token_usage() after each API call
```

### 2.2 Daily Aggregation Job
**Priority: MEDIUM**

**Implementation Steps:**

1. **Create Aggregation Service**
```python
# File: bolna/services/aggregation_service.py
class AggregationService:
    async def aggregate_daily_usage(self, date: datetime.date)
    async def generate_tenant_reports(self, tenant_id: int, month: int, year: int)
```

2. **Add Cron Job**
```python
# File: bolna/jobs/daily_aggregation.py
# Run daily at midnight to aggregate previous day's usage
```

## 🎯 PHASE 3: Caching & Performance (Week 3)

### 3.1 Multi-level Caching Strategy

**Implementation Steps:**

1. **Agent Config Caching**
```python
# File: bolna/cache/agent_cache.py
# Cache agent configs in Redis with tenant prefix
# TTL: 1 hour, invalidate on updates
```

2. **Call State Caching**
```python
# File: bolna/cache/call_cache.py
# Cache active call states in Redis
# TTL: Call duration + 1 hour
```

3. **Usage Caching**
```python
# File: bolna/cache/usage_cache.py
# Cache current day usage in Redis
# Update real-time, flush to DB every 5 minutes
```

### 3.2 Database Optimization

**Implementation Steps:**

1. **Add Database Indexes**
```sql
-- Already present in models.py, verify in production
CREATE INDEX idx_calls_tenant_status ON calls(tenant_id, status);
CREATE INDEX idx_usage_tenant_time ON usage_ledger(tenant_id, recorded_at);
```

2. **Connection Pooling**
```python
# File: bolna/db/connection.py
# Configure SQLAlchemy connection pool
# Add read replicas for analytics queries
```

## 🎯 PHASE 4: Security & Production Readiness (Week 4)

### 4.1 Enhanced Security

**Implementation Steps:**

1. **Rate Limiting**
```python
# File: bolna/middleware/rate_limiter.py
# Per-tenant API rate limits
# Per-user WebSocket connection limits
```

2. **Input Validation**
```python
# File: bolna/validators/
# Strict Pydantic models for all inputs
# SQL injection prevention
# XSS protection
```

3. **Audit Logging**
```python
# File: bolna/services/audit_service.py
# Log all CRUD operations
# Log authentication events
# Log billing events
```

### 4.2 Monitoring & Observability

**Implementation Steps:**

1. **Health Checks**
```python
# File: bolna/health/
# Database connectivity
# Redis connectivity
# External provider status
```

2. **Metrics Collection**
```python
# File: bolna/metrics/
# Prometheus metrics
# Call success rates
# Provider latencies
# Usage trends
```

## 🚀 IMMEDIATE NEXT STEPS (Today/Tomorrow)

### Step 1: Create Database Services
```bash
mkdir -p bolna/services
touch bolna/services/__init__.py
touch bolna/services/agent_service.py
touch bolna/services/call_service.py
touch bolna/services/usage_service.py
```

### Step 2: Update quickstart_server.py
- Add tenant_id extraction from JWT
- Replace Redis agent operations with database operations
- Add proper error handling

### Step 3: Test Database Integration
- Create test agents via API
- Verify tenant isolation
- Test agent CRUD operations

### Step 4: Migrate Existing Data
- Export Redis agents
- Import to database with proper tenant assignment

## 📊 SUCCESS METRICS

### Week 1 Targets:
- [ ] All agents stored in database with tenant isolation
- [ ] Call history properly tracked in database
- [ ] Basic transcript storage working

### Week 2 Targets:
- [ ] Real-time usage tracking implemented
- [ ] Daily usage aggregation working
- [ ] Basic billing data available

### Week 3 Targets:
- [ ] Redis caching implemented
- [ ] API response times < 200ms
- [ ] Database queries optimized

### Week 4 Targets:
- [ ] Rate limiting active
- [ ] Security audit passed
- [ ] Production deployment ready

## 🔧 DEVELOPMENT WORKFLOW

1. **Create feature branch for each phase**
2. **Write tests first (TDD approach)**
3. **Implement service layer**
4. **Update API endpoints**
5. **Add caching layer**
6. **Performance testing**
7. **Security review**
8. **Deploy to staging**

## 📝 NOTES

- Keep Redis for caching, move persistent data to MySQL
- Maintain backward compatibility during migration
- Add comprehensive logging for debugging
- Use database transactions for data consistency
- Implement proper error handling and rollback mechanisms

---

**Next Action:** Start with `bolna/services/agent_service.py` implementation