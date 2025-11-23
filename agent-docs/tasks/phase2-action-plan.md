---
title: "Phase 2 Action Plan - Docker Containerization"
description: "Detailed step-by-step action plan for Phase 2 implementation"
type: task
status: draft
created: "2025-11-23"
updated: "2025-11-23"
author: "Nexus AI System"
tags:
  - phase2
  - docker
  - containerization
  - deployment
  - action-plan
llm_summary: |
  Step-by-step action plan for Phase 2 Docker containerization.
  Includes detailed tasks, code examples, validation steps, and success criteria.
  Estimated duration: 4-6 hours. Ready to start after Phase 1 completion.
---

# Phase 2 Action Plan: Docker Containerization

**Start Date:** 2025-11-23 (after Phase 1 validation)  
**Estimated Duration:** 4-6 hours  
**Status:** 🔜 Ready to Start  
**Priority:** HIGH

---

## 🎯 Objectives

Transform the validated Phase 1 local installation into a portable, containerized service that:
- Runs on any Docker-enabled system (Windows, Linux, macOS)
- Includes all dependencies (Python, Rust, tools)
- Persists state across container restarts
- Scales horizontally in future phases

---

## 📋 Task Breakdown

### Task 2.1: Create Multi-Stage Dockerfile ⏱️ 2-3 hours

**Goal:** Build optimized Docker image with Rust compilation and Python runtime.

#### Subtask 2.1.1: Rust Builder Stage (1 hour)

**File:** `Dockerfile` (create in project root)

```dockerfile
# ═══════════════════════════════════════════════════════════
# Stage 1: Rust Builder
# ═══════════════════════════════════════════════════════════
FROM rust:1.75-slim as rust-builder

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    pkg-config \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /build

# Copy Rust source code
COPY rust_core/ ./

# Build Rust module in release mode
RUN cargo build --release

# Verify output
RUN ls -lh target/release/
```

**Validation:**
```bash
# Test builder stage only
docker build --target rust-builder -t nexus-rust-builder .
docker run --rm nexus-rust-builder ls -lh target/release/
```

**Expected Output:**
```text
-rwxr-xr-x 1 root root 2.5M Nov 23 12:00 libcde_rust_core.so
```

#### Subtask 2.1.2: Python Runtime Stage (1 hour)

**File:** `Dockerfile` (append)

```dockerfile
# ═══════════════════════════════════════════════════════════
# Stage 2: Python Runtime
# ═══════════════════════════════════════════════════════════
FROM python:3.14-slim

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    libssl3 \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN useradd -m -u 1000 nexus && \
    mkdir -p /app /app/workspaces /app/.cde && \
    chown -R nexus:nexus /app

# Set working directory
WORKDIR /app

# Copy Rust compiled library from builder
COPY --from=rust-builder /build/target/release/libcde_rust_core.so /usr/local/lib/
RUN ldconfig

# Copy Python requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install maturin for building wheel
RUN pip install --no-cache-dir maturin

# Copy Rust source for maturin
COPY --from=rust-builder /build /app/rust_core

# Build and install Python wheel
WORKDIR /app/rust_core
RUN maturin build --release && \
    pip install --no-cache-dir target/wheels/*.whl

# Copy application code
WORKDIR /app
COPY src/ ./src/
COPY .cde/ ./.cde/
COPY specs/ ./specs/
COPY scripts/ ./scripts/

# Switch to non-root user
USER nexus

# Expose FastMCP port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import cde_rust_core; print('OK')" || exit 1

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV LOG_LEVEL=INFO

# Entrypoint
CMD ["python", "src/server.py"]
```

**Validation:**
```bash
# Build complete image
docker build -t nexus-ai:latest .

# Test Python and Rust module
docker run --rm nexus-ai:latest python -c "import cde_rust_core; print(dir(cde_rust_core))"
```

**Expected Output:**
```python
['__doc__', '__file__', '__loader__', '__name__', '__package__', '__spec__', 
 'kill_process', 'monitor_process_health', 'spawn_agent_async', 'spawn_agents_parallel']
```

#### Subtask 2.1.3: Optimize Image Size (30 min)

**Actions:**
- [ ] Remove unnecessary build artifacts
- [ ] Use `.dockerignore` to exclude files
- [ ] Verify final image size (target: < 1GB)

**File:** `.dockerignore` (create in project root)

```text
# Git
.git/
.gitignore

# Python
__pycache__/
*.py[cod]
*$py.class
.pytest_cache/
.venv/
venv/
*.egg-info/

# Rust
rust_core/target/
rust_core/Cargo.lock

# Documentation
docs/
agent-docs/
*.md
!README.md

# Tests
tests/
htmlcov/
.coverage

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Temp files
temp-wheels/
ci-wheels/
*.log
```

**Validation:**
```bash
docker images nexus-ai:latest
# Expected: SIZE < 1.0GB
```

---

### Task 2.2: Create Docker Compose Configuration ⏱️ 1-2 hours

**Goal:** Orchestrate Nexus AI with supporting services (Redis, Postgres).

#### Subtask 2.2.1: Core Service Definition (30 min)

**File:** `docker-compose.yml` (create in project root)

```yaml
version: '3.8'

services:
  # ═══════════════════════════════════════════════════════════
  # Nexus AI Core (CEO System)
  # ═══════════════════════════════════════════════════════════
  nexus-core:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: nexus-ai-ceo
    hostname: nexus-core
    
    # Port mapping
    ports:
      - "8000:8000"  # FastMCP server
    
    # Volume mounts
    volumes:
      # Project workspaces (read-write)
      - ./workspaces:/app/workspaces
      
      # Persistent state
      - nexus-state:/app/.cde
      
      # GitHub CLI authentication (read-only)
      - ~/.config/gh:/home/nexus/.config/gh:ro
      
      # Logs
      - nexus-logs:/app/logs
    
    # Environment variables
    environment:
      - REDIS_URL=redis://redis:6379
      - DB_URL=postgresql://nexus:${DB_PASSWORD:-nexusdev}@postgres:5432/nexus
      - LOG_LEVEL=${LOG_LEVEL:-INFO}
      - WORKER_POOL_SIZE=${WORKER_POOL_SIZE:-3}
      - PYTHONUNBUFFERED=1
    
    # Dependencies
    depends_on:
      redis:
        condition: service_healthy
      postgres:
        condition: service_healthy
    
    # Restart policy
    restart: unless-stopped
    
    # Resource limits
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 2G
        reservations:
          cpus: '0.5'
          memory: 512M
    
    # Networks
    networks:
      - nexus-network
    
    # Health check
    healthcheck:
      test: ["CMD", "python", "-c", "import cde_rust_core"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 10s
```

**Validation:**
```bash
docker-compose config
# Should show no errors
```

#### Subtask 2.2.2: Supporting Services (30 min)

**File:** `docker-compose.yml` (append)

```yaml
  # ═══════════════════════════════════════════════════════════
  # Redis (Task Queue & Caching)
  # ═══════════════════════════════════════════════════════════
  redis:
    image: redis:7-alpine
    container_name: nexus-redis
    hostname: redis
    
    ports:
      - "6379:6379"
    
    volumes:
      - redis-data:/data
    
    command: redis-server --appendonly yes
    
    restart: unless-stopped
    
    networks:
      - nexus-network
    
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  # ═══════════════════════════════════════════════════════════
  # PostgreSQL (Persistent State)
  # ═══════════════════════════════════════════════════════════
  postgres:
    image: postgres:16-alpine
    container_name: nexus-postgres
    hostname: postgres
    
    ports:
      - "5432:5432"
    
    volumes:
      - postgres-data:/var/lib/postgresql/data
    
    environment:
      POSTGRES_DB: nexus
      POSTGRES_USER: nexus
      POSTGRES_PASSWORD: ${DB_PASSWORD:-nexusdev}
      POSTGRES_INITDB_ARGS: "--encoding=UTF8 --lc-collate=C --lc-ctype=C"
    
    restart: unless-stopped
    
    networks:
      - nexus-network
    
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U nexus"]
      interval: 10s
      timeout: 5s
      retries: 5

# ═══════════════════════════════════════════════════════════
# Volumes (Persistent Data)
# ═══════════════════════════════════════════════════════════
volumes:
  nexus-state:
    driver: local
    name: nexus-state
  
  nexus-logs:
    driver: local
    name: nexus-logs
  
  redis-data:
    driver: local
    name: nexus-redis-data
  
  postgres-data:
    driver: local
    name: nexus-postgres-data

# ═══════════════════════════════════════════════════════════
# Networks (Service Isolation)
# ═══════════════════════════════════════════════════════════
networks:
  nexus-network:
    driver: bridge
    name: nexus-network
```

**Validation:**
```bash
docker-compose config | grep -E "(services|volumes|networks)"
# Should list all services, volumes, networks
```

#### Subtask 2.2.3: Environment Configuration (30 min)

**File:** `.env.example` (create in project root)

```bash
# ═══════════════════════════════════════════════════════════
# Nexus AI Environment Configuration
# ═══════════════════════════════════════════════════════════

# ───────────────────────────────────────────────────────────
# Database Configuration
# ───────────────────────────────────────────────────────────
DB_PASSWORD=change_this_secure_password_in_production

# ───────────────────────────────────────────────────────────
# MCP Server Configuration
# ───────────────────────────────────────────────────────────
LOG_LEVEL=INFO
WORKER_POOL_SIZE=3

# ───────────────────────────────────────────────────────────
# GitHub CLI Authentication (Alternative to volume mount)
# ───────────────────────────────────────────────────────────
# GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# ───────────────────────────────────────────────────────────
# External Agent API Keys (If using API-based agents)
# ───────────────────────────────────────────────────────────
# JULIUS_API_KEY=your_julius_api_key_here
# GEMINI_API_KEY=your_gemini_api_key_here
# QWEN_API_KEY=your_qwen_api_key_here

# ───────────────────────────────────────────────────────────
# Resource Limits (Optional)
# ───────────────────────────────────────────────────────────
# MAX_WORKERS=5
# TASK_TIMEOUT=3600
# MAX_PARALLEL_AGENTS=10
```

**File:** `.env` (user creates from example)

```bash
cp .env.example .env
# User edits .env with their credentials
```

**Validation:**
```bash
docker-compose --env-file .env config | grep -A5 environment
# Should show environment variables loaded
```

---

### Task 2.3: Build and Deploy ⏱️ 30 min

**Goal:** Build images and start all services.

#### Step 1: Build Images

```bash
# Build all images
docker-compose build

# Expected output:
# [+] Building 120.5s (24/24) FINISHED
# => [rust-builder 1/4] FROM rust:1.75-slim
# => [python-runtime 1/8] FROM python:3.14-slim
# ...
# => => naming to docker.io/library/nexus-ai:latest
```

**Validation:**
```bash
docker images | grep nexus
# Expected:
# nexus-ai      latest    abc123def456   2 minutes ago   987MB
```

#### Step 2: Start Services

```bash
# Start all services in detached mode
docker-compose up -d

# Expected output:
# [+] Running 4/4
#  ✔ Network nexus-network       Created
#  ✔ Container nexus-redis       Started
#  ✔ Container nexus-postgres    Started
#  ✔ Container nexus-ai-ceo      Started
```

**Validation:**
```bash
docker-compose ps
# Expected:
# NAME              STATUS          PORTS
# nexus-ai-ceo      Up 10 seconds   0.0.0.0:8000->8000/tcp
# nexus-redis       Up 15 seconds   0.0.0.0:6379->6379/tcp
# nexus-postgres    Up 15 seconds   0.0.0.0:5432->5432/tcp
```

#### Step 3: Check Logs

```bash
# View logs from all services
docker-compose logs -f

# View logs from specific service
docker-compose logs -f nexus-core

# Expected output:
# nexus-core | INFO:     Started server process [1]
# nexus-core | INFO:     Waiting for application startup.
# nexus-core | INFO:     AgentManager started with 3 workers
# nexus-core | INFO:     Application startup complete.
```

---

### Task 2.4: Validation & Testing ⏱️ 1 hour

**Goal:** Verify all components work correctly in containerized environment.

#### Test 2.4.1: Container Health Checks

```bash
# Check health status
docker-compose ps --format json | jq -r '.[] | "\(.Name): \(.Health)"'

# Expected output:
# nexus-ai-ceo: healthy
# nexus-redis: healthy
# nexus-postgres: healthy
```

#### Test 2.4.2: Rust Module in Container

```bash
# Test Rust module loads correctly
docker exec nexus-ai-ceo python -c "
import cde_rust_core
print('Rust module functions:')
for name in dir(cde_rust_core):
    if not name.startswith('_'):
        print(f'  - {name}')
"

# Expected output:
# Rust module functions:
#   - kill_process
#   - monitor_process_health
#   - spawn_agent_async
#   - spawn_agents_parallel
```

#### Test 2.4.3: AgentManager Initialization

```bash
# Test AgentManager starts correctly
docker exec nexus-ai-ceo python -c "
from src.cde_orchestrator.domain.agent_manager import AgentManager
manager = AgentManager.get_instance()
print(f'Workers: {len(manager.workers)}')
print(f'Max workers: {manager.max_workers}')
"

# Expected output:
# Workers: 3
# Max workers: 3
```

#### Test 2.4.4: MCP Tools Accessible

```bash
# Test MCP server responds
curl -X POST http://localhost:8000/mcp/cde_getWorkerStats \
  -H "Content-Type: application/json" \
  -d '{}' | jq

# Expected output:
# {
#   "status": "success",
#   "max_workers": 3,
#   "active_workers": 0,
#   "total_tasks_queued": 0,
#   "total_tasks_processed": 0,
#   "workers": [...]
# }
```

#### Test 2.4.5: State Persistence

```bash
# Step 1: Create a task
docker exec nexus-ai-ceo python -c "
import asyncio
from src.mcp_tools.ceo_orchestration import cde_delegateTask

async def test():
    result = await cde_delegateTask(
        task_description='Test persistence',
        task_type='test'
    )
    print(result)

asyncio.run(test())
"

# Step 2: Restart container
docker-compose restart nexus-core
sleep 10

# Step 3: Check if task persists (if state management implemented)
docker exec nexus-ai-ceo python -c "
import asyncio
from src.mcp_tools.ceo_orchestration import cde_listActiveTasks

async def test():
    result = await cde_listActiveTasks()
    print(result)

asyncio.run(test())
"
```

#### Test 2.4.6: Run Validation Script in Container

```bash
# Copy validation script to container
docker cp scripts/validate_phase1.py nexus-ai-ceo:/tmp/

# Run validation script
docker exec nexus-ai-ceo python /tmp/validate_phase1.py

# Expected output:
# ✅ Rust module compiled and imported successfully
# ✅ AgentManager started with 3 workers
# ✅ Worker stats retrieved
# ✅ Delegated 3 tasks in 0.000s
# ✅ Spawned 3 processes in parallel
# ✅ AgentManager stopped gracefully
#
# Phase 1 Foundation: VALIDATED ✅
```

---

### Task 2.5: Documentation ⏱️ 30 min

**Goal:** Create comprehensive Docker deployment documentation.

#### File: `docs/docker-deployment.md`

**Outline:**
1. **Prerequisites**
   - Docker 20.10+
   - Docker Compose 2.0+
   - Git
   - 4GB RAM minimum

2. **Quick Start**
   ```bash
   git clone <repo>
   cd CDE-Orchestrator-MCP
   cp .env.example .env
   # Edit .env with your credentials
   docker-compose up -d
   ```

3. **Volume Mounting**
   - How to mount external projects
   - GitHub CLI authentication setup
   - Persistent state management

4. **Environment Variables**
   - Complete reference
   - Required vs optional
   - Default values

5. **Troubleshooting**
   - Common issues and solutions
   - Log inspection commands
   - How to rebuild images

#### Update: `README.md`

**Add section:**
```markdown
## 🐳 Docker Deployment

### Quick Start with Docker

```bash
# Clone repository
git clone https://github.com/yourusername/CDE-Orchestrator-MCP.git
cd CDE-Orchestrator-MCP

# Create environment file
cp .env.example .env
# Edit .env with your credentials

# Build and start services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f nexus-core
```

### Configuration

See [Docker Deployment Guide](docs/docker-deployment.md) for detailed configuration options.

### Accessing MCP Tools

```bash
# From host machine
curl http://localhost:8000/mcp/cde_getWorkerStats

# From another container
curl http://nexus-core:8000/mcp/cde_getWorkerStats
```
```

---

## ✅ Success Criteria

Phase 2 is complete when ALL of the following are true:

- [x] **Build Success**
  - [ ] `docker-compose build` completes without errors
  - [ ] Final image size < 1.5GB
  - [ ] Build time < 10 minutes

- [x] **Startup Success**
  - [ ] All 3 services start with `docker-compose up -d`
  - [ ] Health checks pass within 30 seconds
  - [ ] No errors in logs

- [x] **Functional Validation**
  - [ ] Rust module loads in container
  - [ ] AgentManager initializes with 3 workers
  - [ ] MCP tools accessible from host
  - [ ] Validation script passes inside container

- [x] **Persistence Validation**
  - [ ] State survives container restart
  - [ ] Volumes created correctly
  - [ ] Data persists in Redis and Postgres

- [x] **Documentation Complete**
  - [ ] `docs/docker-deployment.md` created
  - [ ] `README.md` updated with Docker instructions
  - [ ] `.env.example` documented
  - [ ] Troubleshooting guide written

---

## 🚨 Potential Issues & Mitigation

### Issue 1: Rust Compilation Timeout in Docker

**Symptom:** Build hangs or times out during Rust compilation

**Mitigation:**
```dockerfile
# Add in Dockerfile
ENV CARGO_NET_RETRY=10
ENV CARGO_HTTP_TIMEOUT=600
```

### Issue 2: Permission Denied on Volume Mounts

**Symptom:** Container can't write to mounted volumes

**Mitigation:**
```yaml
# In docker-compose.yml
volumes:
  - ./workspaces:/app/workspaces:rw
user: "${UID:-1000}:${GID:-1000}"
```

### Issue 3: GitHub CLI Auth Not Working

**Symptom:** Container can't authenticate with GitHub

**Mitigation:**
```bash
# Use token-based auth instead of volume mount
docker-compose up -d -e GITHUB_TOKEN=$(gh auth token)
```

### Issue 4: Large Image Size (> 2GB)

**Symptom:** Docker image too large

**Mitigation:**
- Use `.dockerignore` effectively
- Remove build artifacts in same layer
- Use `--no-cache-dir` for pip installs
- Consider Alpine-based images

---

## 📊 Metrics to Track

### Build Metrics
- Build time: Target < 10 minutes
- Image size: Target < 1.5GB
- Layer count: Target < 25 layers

### Runtime Metrics
- Startup time: Target < 30 seconds
- Memory usage: Target < 1GB idle
- CPU usage: Target < 20% idle

### Validation Metrics
- Health check success rate: 100%
- Validation script pass rate: 100%
- MCP tool response time: < 100ms

---

## 🔜 After Phase 2

Once Phase 2 is complete and validated:

1. **Phase 3:** Add async task queue (Celery/RQ)
2. **Phase 3:** Implement worker scaling
3. **Phase 4:** Multi-agent orchestration
4. **Phase 5:** Production deployment (K8s/VPS)

**See:** `specs/tasks/roadmap-ceo.md` for complete roadmap

---

**Prepared by:** Nexus AI System  
**Date:** 2025-11-23  
**Status:** Ready to Execute
