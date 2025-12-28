# BOLNA_BACKEND_ARCHITECTURE_RESEARCH

> Short status: I inspected the codebase end-to-end and documented concrete behavior and gaps (no assumptions). Next step: finalize and cross-check each section with code references.

---

## 1. Project Overview ✅

**What Bolna does (based on code):**
- Bolna is an orchestration backend that runs real-time voice conversations by combining ASR (transcribers), LLMs, and TTS (synthesizers) over WebSockets and telephony integrations. (See: `local_setup/quickstart_server.py`, `bolna/agent_manager/task_manager.py`, `bolna/providers.py`)
- It exposes a WebSocket endpoint (`/chat/v1/{agent_id}`) to handle live audio/text streaming, and HTTP endpoints to create/edit/delete `agent` configurations. (See: `quickstart_server.py` endpoints and websocket handler.)

**Problems it solves:**
- Orchestrates streaming audio → ASR → LLM → TTS pipelines.
- Provides pluggable provider support (Deepgram, OpenAI, LiteLLM, ElevenLabs, Polly, Azure, etc.) via `bolna/providers.py`.
- Supports telephony bridging (Twilio / Plivo) to turn calls into WebSocket streams (`local_setup/telephony_server/*`).
- Enables RAG-style knowledge retrieval via a RAG proxy client (`bolna/helpers/rag_service_client.py`) integrated into agents.

**Problems it does NOT solve (explicitly absent):**
- Proper multi-tenant data isolation for agents and run data. Agents are stored in Redis without tenant scoping (`local_setup/quickstart_server.py` / `redis_client`).
- Durable run/call history in a central DB (calls, transcript history, usage/ billing) — only per-run logs (CSV files) and ephemeral in-memory structures are used.
- Billing and metering persistence (analytics helper exists but no central persistence for aggregated usage or per-tenant accounting.)
- Advanced SaaS features: rate-limiting, role-based admin/tenant scoping for agents, secret rotation, audit logs, durable queuing.

**Engine/backend/library?:**
- This repository is a backend orchestration engine (not just a library). It provides a FastAPI service (`quickstart_server.py`) and connector services for telephony. It is *not* a finished SaaS product — it is an orchestration engine/demo backend.

---

## 2. High-Level Architecture 🔧

### Modules / Layers
- API / Edge: `local_setup/quickstart_server.py`, telephony servers in `local_setup/telephony_server/`.
- Auth / Identity: `bolna/auth/*` (MySQL + JWT).
- Agent orchestration: `bolna/agent_manager/` (AssistantManager, TaskManager).
- Providers: `bolna/providers.py` references implementations in `bolna/llms/`, `bolna/transcriber/`, `bolna/synthesizer/`, `bolna/input_handlers/`, `bolna/output_handlers/`.
- Helpers & utilities: `bolna/helpers/*` (utils, analytics_helpers, rag_service_client, logging, file storage).
- Memory & caching: `bolna/memory/cache/*` (in-memory vector cache, etc.).
- Persistence layers: Redis (agents), MySQL (auth), S3 local-prefetch support (optional), local file logs.

### Entry point / request flow (text diagram)

Telephony (Twilio/Plivo) or Web client
    ↓ (calls / streams audio via HTTP Webhook or client WebSocket)
FastAPI WebSocket endpoint (/chat/v1/{agent_id}) in `quickstart_server.py`
    ↓
AssistantManager (loads agent config from Redis)
    ↓
TaskManager per-task (sets up IO handlers, transcriber, LLM agent, synthesizer, output handler)
    ↓
Pipelines (example):
    transcriber (Deepgram) -> LLM (OpenAI/LiteLLM) -> synthesizer (ElevenLabs/OpenAI TTS) -> output handler (Twilio/Websocket)

### Sync vs Async
- Predominantly asynchronous (asyncio + FastAPI). Transcribers, LLM streaming clients, synthesizers expose async streaming/generator APIs.
- Uses async Redis (`redis.asyncio`) and aiohttp/httpx clients in LLM/RAG clients.

### WebSocket usage
- WebSocket (path `/chat/v1/{agent_id}`) is the core real-time transport for client-side sessions and for telephony server 'connect.stream' integrations. (`quickstart_server.py`)
- Input handler (`DefaultInputHandler` / `TelephonyInputHandler`) reads websocket messages and pushes to TaskManager queues.
- Output handler (`DefaultOutputHandler` or telephony-specific handlers) sends synthesized audio/text back over the WebSocket or telephony API.

---

## 3. API Layer (detailed) 🔒

What exists:
- HTTP endpoints (in `local_setup/quickstart_server.py`):
  - GET `/agent/{agent_id}`
  - POST `/agent` (create agent stored in Redis)
  - PUT `/agent/{agent_id}` (update in Redis)
  - DELETE `/agent/{agent_id}`
  - GET `/all` (returns all Redis keys)
- Auth routes under `/auth` (`bolna/auth/routes.py`) provide `/signup` and `/login` and issue JWTs.
- WebSocket: `@app.websocket('/chat/v1/{agent_id}')` is the main real-time entry (see `quickstart_server.py`).

Validation:
- API request bodies validate using Pydantic models in `bolna/models.py` (`AgentModel`, `Task`, `ToolsConfig`, `Synthesizer`, `Transcriber`, etc.).

Authentication / Authorization:
- JWT-based auth using `bolna/auth/security.py` and `bolna/auth/dependencies.py` (HTTPBearer). `get_current_user` dependency is used on agent endpoints.

How API calls trigger voice orchestration:
- POST `/agent` stores agent config in Redis and persisted prompts via `store_file` (local/S3). The WebSocket endpoint loads that agent config by ID and instantiates AssistantManager → TaskManager to run tasks.

Multi-tenant API safety:
- **Not safe out-of-the-box**. Agent data is stored under raw Redis keys (UUIDs), and `create_agent` does not persist tenant information or use tenant-prefixed Redis keys. `GET /all` calls `redis.keys('*')` and returns *all* agent configs. This needs per-tenant scoping before SaaS usage.

---

## 4. Call Lifecycle & Orchestration ☎️

How a call starts:
- Telephony: `local_setup/telephony_server/twilio_api_server.py` or `plivo_api_server.py` creates a call which streams to `{bolna_host}/chat/v1/{agent_id}`.
- Web dashboard or client: `quickstart_client.py` connects to `/chat/v1/{agent_id}` and streams audio frames.

Key orchestration pieces:
- `AssistantManager` reads the agent config and sequentially runs tasks (calls `TaskManager` per task). (See `bolna/agent_manager/assistant_manager.py` and `task_manager.py`.)
- `TaskManager` wires input handlers → transcriber → LLM agent → synthesizer → output handler and orchestrates asynchronous queues and generators.

Call states & state machine:
- Internal boolean flags exist: `conversation_ended`, `hangup_triggered`, `turned-based_conversation` and others. There is no explicit, centralized FSM class; instead TaskManager keeps per-call state and observables (e.g., `ObservableVariable` objects).

Telephony events handling:
- `TelephonyInputHandler` handles 'start', 'media', 'mark', 'dtmf', 'stop' events (buffers inbound audio and sends to transcriber queue). On telephony stop, it sends an EOS packet to the transcriber queue to start cleanup.

WebSocket streaming:
- Client sends JSON messages `{type: 'audio', data: <base64>}` or `{type: 'text', data: '...'};` `DefaultInputHandler.process_message()` pushes to queues for downstream tasks.

Call termination:
- Several paths:
  - Telephony 'stop' → EOS to transcriber → finalization.
  - LLM-based hangup (optional): `use_llm_to_determine_hangup` triggers a completion prompt and may call `process_call_hangup()`.
  - Agent 'hangup' mark events (output handler emits `agent_hangup` mark).

Failure handling (ASR/LLM/TTS):
- ASR failure: transcribers (e.g., DeepgramTranscriber) detect stuck utterances via `utterance_timeout` and force-finalize with last interim transcript.
- LLM failure: `OpenAiLLM`/`LiteLLM` catch and log specific exceptions (auth, rate limit, connection, API errors). Some errors are re-raised so the caller can decide. LiteLLM handles content policy violations by logging and returning gracefully.
- TTS failure: synths yield exceptions; TaskManager logs and attempts cleanup; no global retry/circuit-breaker policy.

Is there a dedicated call state machine? No formal state machine implementation; TaskManager's internal flags and observable variables act as the state tracking and control flow.

---

## 5. LLM, ASR, and TTS Integration 🧠🔊

LLMs
- Implementations: `OpenAiLLM`, `LiteLLM`, `AzureLLM` (`bolna/llms/*`).
- Streaming: `generate_stream` yields tokens/chunks; LLM classes support streaming and function calling. They emit latency/service-tier metadata for analysis.
- Error handling: code explicitly catches AuthenticationError, PermissionDeniedError, RateLimitError, APIConnectionError, APIError and logs/re-raises where appropriate (OpenAI), while LiteLLM swallows content policy violations and logs them.
- Prompt handling: TaskManager constructs messages via `format_messages` and `structure_system_prompt`, and passes context. Function calling payloads are processed by `function_calling_helpers`.

ASR
- Implementations: Deepgram, Azure, AssemblyAI, Google, etc. (see `bolna/transcriber/`).
- Streaming: Deepgram transcriber uses a websocket to Deepgram, sends frames and handles `SpeechStarted`, interim results (`interim_transcript_received`), and final transcripts (`transcript`). It monitors heartbeats and has an `utterance_timeout` to force-finalize stuck utterances.
- Buffering and timeouts: audio is buffered per provider decisions (e.g., Twilio uses 200ms frames). DeepgramTranscriber keeps frame timestamps and computes latencies.
- Failures: connection errors are logged, closed; transcriber emits `transcriber_connection_closed` to the TaskManager queue to trigger cleanup.

TTS
- Implementations: `OPENAISynthesizer`, `ElevenlabsSynthesizer`, Polly, Azure, etc (`bolna/synthesizer/`).
- Streaming vs batch: Many synthesizers support stream and non-stream generation. `synthesizer.generate()` is an async generator yielding audio chunks and `meta_info` flags like `is_first_chunk`, `end_of_synthesizer_stream`.
- Latency/Buffering: TaskManager controls `buffer_size` (characters) and chunk sizes (via `output_chunk_size`) to manage latency and interruption.
- Caching: synthesized outputs can be cached as preprocessed audio (md5 hashed) and replayed from S3/local to save latency.

---

## 6. Agent Management (VERY IMPORTANT) 🤖

What an agent is (code-wise):
- `AgentModel` (Pydantic) describes agent config including `agent_name`, `agent_type`, list of `Task` definitions (`bolna/models.py`). A Task encapsulates `tools_config` and `toolchain`.

Where agent configs live:
- Primary store: Redis (async) — the agent JSON is stored as a value keyed by UUID in `local_setup/quickstart_server.py`.
- Prompts are also stored via `store_file` into local preprocess dir or S3 as `conversation_details.json`.

How behavior is controlled:
- `AssistantManager` + `TaskManager` read agent config and dynamically instantiate the correct input/output/transcriber/llm/synthesizer classes per `tools_config` and `toolchain`.
- Agent behavior is entirely driven by the JSON config and prompts (no compiled artifacts).

Persistence & sharing:
- Agent configs are persistent in Redis and file- storage for prompts. Multiple calls can reuse the same agent config by referencing the same agent_id.

Production readiness assessment:
- **Demo/engine-grade**: Agent storage is functional but missing key SaaS features:
  - No tenant scoping on agent keys (creates risk of cross-tenant access).
  - No audit trail or historical runs persisted in DB.
  - No role-based access beyond basic auth for user accounts.
- For SaaS: agent storage/ownership, ACLs, per-tenant keys, and persistent run records + analytics must be added.

---

## 7. Transcript & Event Logging 📝

How transcripts are generated:
- Transcribers push interim/final transcripts into TaskManager which appends message objects to `self.history` and converts to request logs.
- Interim results handled separately (interim vs final) in `TaskManager._listen_transcriber()` and `DeepgramTranscriber` specifically handles `Results`, `SpeechStarted`, and timeouts.

Storage & structure:
- Primary logging: `convert_to_request_log()` writes structured rows to `./logs/{run_id}.csv` via `write_request_logs()` (see `bolna/helpers/utils.py`). Columns include Time, Component, Direction, Leg ID, Sequence ID, Model, Data, Input/Output tokens, Latency, etc.
- Conversation recordings are held in-memory in `self.conversation_recording` (audio bytes) and can be uploaded to S3 by `save_audio_file_to_s3()`.

Timestamps & partial transcripts:
- Timestamps are present in logs (`Time` column). The system distinguishes interim vs final transcripts via `meta_info['is_final']` or flagging fields.

Event logging
- `Mark` events are used to indicate synthesized chunk boundaries, welcome/hangup messages, and are stored in `MarkEventMetaData` (in-process). Observers toggle flags (e.g., final chunk played, agent hangup observable).
- Overall logging is mostly file-based and in logging statements (no centralized telemetry DB).

Debuggability
- The system produces CSV logs per run and extensive debug logs. These files are helpful but need a central storage and retention policy for production.

---

## 8. Database Design (If Any) 🗄️

What exists:
- SQL (MySQL via SQLAlchemy) is used only for authentication/tenancy (`bolna/auth/database.py`, `bolna/auth/models.py`). Tables: `tenants`, `users`.

What’s NOT stored but should be for SaaS:
- Per-call history metadata (timestamps, duration, agent id, tenant, transcript pointers).
- Usage metrics (tokens, minutes) stored per tenant for billing.
- Aggregated analytics and alerts.
- Agent ownership mapping in Redis (agent → tenant ID) — currently missing.

---

## 9. Caching & State Management ⚡

Redis
- Redis is used to store agent configs (JSON). (See `local_setup/quickstart_server.py`).
- No TTL or namespaces per tenant by default.
- `GET /all` lists keys with `redis.keys('*')` — not tenant-aware.

In-memory caches
- VectorCache (in `bolna/memory/cache/vector_cache.py`) keeps embeddings and documents in RAM.
- Request logs and conversation recordings are in-memory until flushed to disk or S3.

Risks
- No tenant isolation in Redis.
- Memory-heavy in-memory stores (audio buffers) could be OOM on large concurrent usage.
- No centralized cache invalidation or TTLs for many ephemeral caches.

---

## 10. Authentication & Security 🔐

Authentication:
- JWT tokens issued via `/auth/signup` and `/auth/login` using `bolna/auth/security.py` and required via `get_current_user` (HTTPBearer dependency).

Secrets & keys:
- API keys for providers and JWT_SECRET are read from environment variables. No specialized secret management present.

Security risks:
- Lack of tenant scoping and lack of access control for Redis-stored agents is a major risk.
- No rate limiting / abuse mitigation on API or websocket endpoints.
- No secret rotation, HSM support, or centralized audit logs.

---

## 11. Error Handling & Resilience 🛠️

- Most components use try/except and log exceptions (good for debugging).
- Provider clients (OpenAI, LiteLLM, Deepgram) catch and classify errors (auth, rate limit, connection, api) in-line; some re-raise, some swallow (e.g., LiteLLM content policy).
- No uniform retry/backoff/circuit-breaker strategy for downstream providers.
- TaskManager cancelation paths exist (e.g., `process_task_cancellation`) and tasks are cleaned up when calls end.

Recommendation: add centralized error/retry policies, backoff and circuit breakers for vendor calls and a monitoring/alerting layer.

---

## 12. Webhooks, Callbacks & External Events 🔁

- Telephony servers handle provider-specific webhook patterns:
  - Twilio: `twilio_connect` uses Twilio `Connect().stream(...)` to stream to websocket.
  - Plivo: endpoints include `plivo_hangup_callback`. (`local_setup/telephony_server/plivo_api_server.py`).
- RAG service integration uses HTTP to `rag-proxy-server` and expects a responsive service.
- No general-purpose webhook subscription/persistence layer.

Reliability: telephony callbacks are handled but not retried/persisted by Bolna; external webhook errors need upstream retry or stronger guarantees.

---

## 13. Analytics & Usage Tracking 📊

- `bolna/helpers/analytics_helpers.py` contains routines to calculate token cost and update aggregate metrics in memory.
- Per-run traces are written as CSVs with request logs (`./logs/{run_id}.csv`) by `convert_to_request_log`.
- There is **no** central analytics DB or billing pipeline. No tenant-level aggregation is persisted.

Therefore: Bolna alone isn’t sufficient for SaaS billing — you must add persistent metering, tenant-level aggregation, and billing pipelines.

---

## 14. RAG, Memory, and Context Handling 📚

- RAG: KnowledgeBaseAgent and GraphAgent call out to `RAGServiceClient` (a client for an external rag-proxy-server). RAG is supported but implemented externally (requires a separate RAG proxy server). (See `bolna/helpers/rag_service_client.py` and `bolna/agent_types/knowledgebase_agent.py`).
- Conversation memory: TaskManager keeps `self.history` in memory for the life of a call; not persisted to database by default.
- Limits: history is trimmed by agents (e.g., KnowledgeBaseAgent limits messages) but long-term memory and user profiles are not persisted.

---

## 15. Deployment & Runtime Model 🚀

- Local Docker files and `docker-compose` are present under `local_setup/dockerfiles` and `local_setup/docker-compose.yml`.
- `uvicorn` is used to run FastAPI (`quickstart_server.py` in Dockerfile). Telephony servers have their own endpoints.
- Environment variables control DB URL, Redis URL, API keys, JWT_SECRET, RAG server URL, S3 bucket information.
- For production: recommended to run behind a managed Redis, MySQL and have credentials & secret management, plus central logging and observability.

---

## 16. SaaS Readiness Evaluation ✅ / ⚠️

Component | Present | Missing | Needs Refactor | Notes
---|---:|---|---|---
Auth (tenant+user) | ✅ (MySQL models, JWT) | — | needs hardening | Good base (`bolna/auth/*`) but needs RBAC, audit logs
Agent storage | ✅ (Redis) | Tenant scoping, ACLs | **Refactor** to tenant-prefixed keys | `create_agent` does not bind agent to tenant
Call history & transcripts | ✅ (per-run CSV logs + in-memory) | Central persistence, indexing | **Needs** service + DB | Logs exist but not centrally queryable
LLM/ASR/TTS integration | ✅ | Provider-specific retries and circuit breakers | add resilience | Good pluggable provider layer
RAG/Knowledge | ✅ (client) | RAG service infra | depends on external service | Integration present but relies on a separate service
Monitoring/analytics | partial | Persistent metrics, billing | add pipeline & DB | Analytics helpers exist but not persisted for SaaS
Secrets | partial (env) | Rotation, vault | refactor to secret manager | Env vars must be removed for prod
Multi-tenant isolation | ❌ | Full isolation/ACLs | **Must** implement | Redis/global resources currently unscoped

Key takeaways for SaaS:
- Reusable: providers, TaskManager orchestration, transcriber/synthesizer interfaces are good building blocks.
- Must be wrapped/replaced: Redis agent storage needs tenant-scoping, call data needs to be persisted and partitioned, and metrics & billing pipelines are required before exposing public APIs.
- Must NOT be exposed to frontends directly: internal provider keys, `GET /all` (returns all Redis keys), and any endpoints that leak cross-tenant agent configs.

---

## 17. Summary for Future Developers 👩‍💻👨‍💻

Where to start reading (short guided path):
1. `local_setup/quickstart_server.py` — the FastAPI entry, agent CRUD and websocket handler.
2. `bolna/agent_manager/assistant_manager.py` → `bolna/agent_manager/task_manager.py` — core orchestration and state.
3. `bolna/models.py` — Pydantic models (how agent configuration is structured).
4. `bolna/providers.py` and `bolna/llms/`, `bolna/transcriber/`, `bolna/synthesizer/` — provider classes and streaming semantics.
5. `bolna/input_handlers/` and `bolna/output_handlers/` — how audio/websocket/telephony messages are ingested and emitted.
6. `bolna/helpers/utils.py` and `analytics_helpers.py` — logging, cost calc and file persistence.

Files you can skip at first:
- Example scripts (`script/initiate_agent_call.py`) and demos in `examples/` (useful for integration tests but not core).

Mental model:
- The agent config (= JSON) is the "program"; AssistantManager runs tasks that connect IO handlers and tools (transcriber, LLM, synthesizer). The TaskManager is the main runtime for a call — it manages queues, streaming, latencies, and the output pipeline.

---

## Appendix — Concrete file references (evidence)
- WebSocket endpoints & agent CRUD: `local_setup/quickstart_server.py`
- Auth models & routes: `bolna/auth/models.py`, `bolna/auth/routes.py`, `bolna/auth/security.py` and `bolna/auth/dependencies.py`
- Agent orchestration: `bolna/agent_manager/assistant_manager.py`, `bolna/agent_manager/task_manager.py`
- Transcribers: `bolna/transcriber/deepgram_transcriber.py` (example of streaming, utterance timeout, forced finalization)
- LLM: `bolna/llms/openai_llm.py`, `bolna/llms/litellm.py` (streaming, function calls, error handling)
- Synthesizers: `bolna/synthesizer/*` (OpenAI, ElevenLabs, Polly examples)
- Providers: `bolna/providers.py` (mapping of names to classes)
- RAG client: `bolna/helpers/rag_service_client.py`
- Logging & request logs: `bolna/helpers/utils.convert_to_request_log`, `write_request_logs`

---

## Final recommendations (practical next steps)
1. Add tenant scoping for agent keys in Redis and store agent ownership metadata in the SQL `tenants`/`users` DB.
2. Add a persistent call/run DB table to store per-call metadata and link logs for billing/analytics.
3. Implement a billing/metering pipeline: persist token counts + durations per tenant.
4. Add rate limiting and API throttling on the FastAPI layer (per-tenant limits).
5. Introduce centralized retries, circuit-breakers, and monitoring for provider calls.
6. Use a secrets manager for provider keys and rotate JWT secrets.

---

If you'd like, I can now:
- Generate a concise checklist and implementation plan for production-hardening (multi-tenancy, billing, metrics), or
- Create an initial PR with the `BOLNA_BACKEND_ARCHITECTURE_RESEARCH.md` added and link TODOs in code.

(Everything above references code observed in the repository — I did not assume behavior not present in the code.)
