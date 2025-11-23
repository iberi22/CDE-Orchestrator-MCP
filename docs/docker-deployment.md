---
title: "Docker Deployment Guide"
description: "Complete guide for deploying Nexus AI using Docker and Docker Compose"
type: guide
status: active
created: "2025-11-23"
updated: "2025-11-23"
author: "Nexus AI Team"
tags:
  - docker
  - deployment
  - containerization
  - devops
llm_summary: |
  Comprehensive Docker deployment guide for Nexus AI.
  Includes prerequisites, quick start, configuration, troubleshooting.
  Supports Windows, Linux, and macOS deployments.
---

# Docker Deployment Guide - Nexus AI

**Version:** 1.0.0
**Last Updated:** 2025-11-23
**Target:** Phase 2 - Docker Containerization

---

## 📋 Prerequisites

### System Requirements

| Requirement | Minimum | Recommended |
|-------------|---------|-------------|
| **Docker** | 20.10+ | 24.0+ |
| **Docker Compose** | 2.0+ | 2.20+ |
| **RAM** | 4GB | 8GB+ |
| **Disk Space** | 10GB | 20GB+ |
| **CPU** | 2 cores | 4+ cores |

### Software Installation

#### Windows

1. **Install Docker Desktop:**
   - Download from: https://www.docker.com/products/docker-desktop/
   - Run installer and follow prompts
   - Restart computer if required

2. **Verify Installation:**
   ```powershell
   docker --version
   # Expected: Docker version 24.0.0+

   docker-compose --version
   # Expected: Docker Compose version v2.20.0+
   ```

#### Linux

```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker

# Install Docker Compose
sudo apt-get update
sudo apt-get install docker-compose-plugin

# Verify
docker --version
docker compose version
```

#### macOS

1. Install Docker Desktop for Mac from: https://www.docker.com/products/docker-desktop/
2. Verify installation same as Windows

---

## 🚀 Quick Start

### 1. Clone Repository

```bash
git clone https://github.com/yourusername/CDE-Orchestrator-MCP.git
cd CDE-Orchestrator-MCP
git checkout CEO  # Use CEO branch for Phase 2
```

### 2. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit with your settings
# Windows:
notepad .env

# Linux/Mac:
nano .env
```

**Minimum Configuration:**
```bash
# Change this password!
DB_PASSWORD=your_secure_password_here
```

### 3. Build and Start Services

```bash
# Build images (first time only, ~5-10 minutes)
docker-compose build

# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f nexus-core
```

### 4. Verify Installation

```bash
# Test Rust module
docker exec nexus-ai-ceo python -c "import cde_rust_core; print('✅ OK')"

# Test MCP server
curl http://localhost:8000/health
```

**Expected Output:**
```json
{
  "status": "healthy",
  "version": "2.0.0",
  "workers": 3
}
```

---

## 🔧 Configuration

### Environment Variables

Complete reference of available environment variables:

#### Database Configuration

```bash
# PostgreSQL password (REQUIRED)
DB_PASSWORD=your_secure_password

# Full connection string (optional, overrides other settings)
DB_URL=postgresql://nexus:password@postgres:5432/nexus

# Connection pool settings
DB_POOL_SIZE=10
DB_MAX_OVERFLOW=20
```

#### MCP Server Configuration

```bash
# Logging level
LOG_LEVEL=INFO  # DEBUG|INFO|WARNING|ERROR|CRITICAL

# Worker pool size (concurrent agents)
WORKER_POOL_SIZE=3  # Recommended: 3-10

# Task timeout (seconds)
TASK_TIMEOUT=3600  # Default: 1 hour

# Max parallel agents
MAX_PARALLEL_AGENTS=10
```

#### Agent Authentication

```bash
# GitHub CLI token (alternative to volume mount)
GITHUB_TOKEN=ghp_xxxxxxxxxxxxx

# External agent API keys
JULIUS_API_KEY=your_julius_key
GEMINI_API_KEY=your_gemini_key
QWEN_API_KEY=your_qwen_key
```

### Volume Mounts

#### Project Workspaces

Mount external projects for Nexus AI to work on:

```yaml
# In docker-compose.yml
volumes:
  - /path/to/your/projects:/app/workspaces
```

**Example:**
```bash
# Windows
- E:\MyProjects:/app/workspaces

# Linux/Mac
- ~/projects:/app/workspaces
```

#### GitHub CLI Authentication

**Option 1: Volume Mount (Recommended)**
```yaml
volumes:
  - ~/.config/gh:/home/nexus/.config/gh:ro
```

**Option 2: Environment Variable**
```bash
# Get token
gh auth token

# Add to .env
GITHUB_TOKEN=ghp_xxxxxxxxxxxxx
```

---

## 🔍 Operations

### Starting Services

```bash
# Start all services
docker-compose up -d

# Start specific service
docker-compose up -d nexus-core

# Start with rebuild
docker-compose up -d --build
```

### Stopping Services

```bash
# Stop all services
docker-compose stop

# Stop and remove containers
docker-compose down

# Stop and remove volumes (⚠️ deletes data)
docker-compose down -v
```

### Viewing Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f nexus-core

# Last N lines
docker-compose logs --tail=100 nexus-core

# Since timestamp
docker-compose logs --since=10m nexus-core
```

### Executing Commands

```bash
# Run command in container
docker exec nexus-ai-ceo <command>

# Interactive shell
docker exec -it nexus-ai-ceo /bin/bash

# Run as specific user
docker exec -u nexus nexus-ai-ceo python --version
```

### Updating

```bash
# Pull latest code
git pull origin CEO

# Rebuild images
docker-compose build --no-cache

# Restart services
docker-compose up -d
```

---

## 🔧 Troubleshooting

### Issue: Build Fails with "Rust Compilation Timeout"

**Symptoms:**
```
error: build failed
ERROR: failed to solve: process "/bin/sh -c cargo build --release"
did not complete successfully: exit code: 101
```

**Solution:**
```bash
# Increase Docker build memory
# Docker Desktop → Settings → Resources → Memory: 4GB+

# Or use BuildKit cache
DOCKER_BUILDKIT=1 docker-compose build
```

### Issue: "Permission Denied" on Volume Mounts

**Symptoms:**
```
Error: EACCES: permission denied, open '/app/workspaces/...'
```

**Solution (Linux/Mac):**
```bash
# Fix ownership
sudo chown -R 1000:1000 ./workspaces

# Or run as current user
docker-compose run --user $(id -u):$(id -g) nexus-core
```

**Solution (Windows):**
- Ensure Docker Desktop has access to the drive
- Settings → Resources → File Sharing → Add drive

### Issue: Container Exits Immediately

**Symptoms:**
```
nexus-ai-ceo | Exited (1)
```

**Diagnosis:**
```bash
# View exit logs
docker-compose logs nexus-core

# Check health status
docker inspect nexus-ai-ceo | grep -A10 Health
```

**Common Causes:**
1. **Missing Rust module:** Rebuild with `--no-cache`
2. **Database not ready:** Check postgres health
3. **Invalid environment:** Verify .env file

### Issue: "Module not found: cde_rust_core"

**Symptoms:**
```
ModuleNotFoundError: No module named 'cde_rust_core'
```

**Solution:**
```bash
# Rebuild Rust module in container
docker-compose build --no-cache nexus-core

# Verify installation
docker exec nexus-ai-ceo python -c "import cde_rust_core"
```

### Issue: High Memory Usage

**Symptoms:**
- Container uses > 2GB RAM
- System becomes slow

**Solution:**
```bash
# Check memory usage
docker stats nexus-ai-ceo

# Reduce worker pool
# In .env:
WORKER_POOL_SIZE=2

# Restart
docker-compose restart nexus-core
```

### Issue: Cannot Connect to MCP Server

**Symptoms:**
```
curl: (7) Failed to connect to localhost port 8000
```

**Diagnosis:**
```bash
# Check if container is running
docker ps | grep nexus-ai-ceo

# Check port mapping
docker port nexus-ai-ceo

# Check firewall (Windows)
netsh advfirewall firewall show rule name=all | findstr 8000
```

**Solution:**
```bash
# Test from inside container
docker exec nexus-ai-ceo curl localhost:8000/health

# If works, it's a network issue
# Check docker-compose.yml ports section
```

---

## 📊 Monitoring

### Health Checks

```bash
# Check all services
docker-compose ps

# Detailed health status
docker inspect nexus-ai-ceo --format='{{.State.Health.Status}}'

# Health check logs
docker inspect nexus-ai-ceo --format='{{json .State.Health}}' | jq
```

### Resource Usage

```bash
# Real-time stats
docker stats

# Specific container
docker stats nexus-ai-ceo

# One-time snapshot
docker stats --no-stream
```

### Database Access

```bash
# Connect to PostgreSQL
docker exec -it nexus-postgres psql -U nexus -d nexus

# Run query
docker exec nexus-postgres psql -U nexus -d nexus -c "SELECT version();"

# Backup database
docker exec nexus-postgres pg_dump -U nexus nexus > backup.sql
```

### Redis Monitoring

```bash
# Connect to Redis CLI
docker exec -it nexus-redis redis-cli

# Check stats
docker exec nexus-redis redis-cli INFO stats

# Monitor commands
docker exec nexus-redis redis-cli MONITOR
```

---

## 🔒 Security Best Practices

### 1. Change Default Passwords

```bash
# Generate secure password
openssl rand -base64 32

# Update .env
DB_PASSWORD=<generated_password>
```

### 2. Use Secrets for Production

```yaml
# docker-compose.prod.yml
secrets:
  db_password:
    external: true
```

### 3. Enable TLS

```yaml
# For production
environment:
  - ENABLE_TLS=true
  - TLS_CERT_PATH=/certs/cert.pem
  - TLS_KEY_PATH=/certs/key.pem
```

### 4. Limit Network Exposure

```yaml
# Only expose to localhost
ports:
  - "127.0.0.1:8000:8000"
```

### 5. Regular Updates

```bash
# Update base images
docker-compose pull

# Rebuild with updated dependencies
docker-compose build --pull
```

---

## 📚 Additional Resources

### Official Documentation
- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Reference](https://docs.docker.com/compose/compose-file/)
- [Nexus AI Architecture](../../specs/design/ceo-agent-manager.md)

### Related Guides
- [Phase 2 Action Plan](../../agent-docs/tasks/phase2-action-plan.md)
- [Phase 1 Completion Report](../../agent-docs/tasks/phase1-completion-report.md)
- [Project Roadmap](../../specs/tasks/roadmap-ceo.md)

### Getting Help
- GitHub Issues: https://github.com/yourusername/CDE-Orchestrator-MCP/issues
- Discussions: https://github.com/yourusername/CDE-Orchestrator-MCP/discussions

---

## ✅ Validation Checklist

After deployment, verify everything works:

- [ ] All 3 services running (`docker-compose ps`)
- [ ] Health checks passing (all services "healthy")
- [ ] Rust module loads (`docker exec ... python -c "import cde_rust_core"`)
- [ ] MCP server responds (`curl http://localhost:8000/health`)
- [ ] AgentManager initializes (check logs for "3 workers")
- [ ] Task delegation works (run validation script in container)
- [ ] State persists after restart (`docker-compose restart`)
- [ ] Logs accessible (`docker-compose logs`)

**Run Full Validation:**
```bash
# Copy validation script
docker cp scripts/validate_phase1.py nexus-ai-ceo:/tmp/

# Run validation
docker exec nexus-ai-ceo python /tmp/validate_phase1.py
```

---

**Document Version:** 1.0.0
**Last Updated:** 2025-11-23
**Maintained By:** Nexus AI Team
