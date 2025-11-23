---
title: "Roadmap: Nexus AI (CEO Transition)"
description: "Strategic roadmap to transform CDE Orchestrator into Nexus AI, a Dockerized, high-availability AI CEO."
type: task
status: active
created: "2025-11-23"
updated: "2025-11-23"
author: "Nexus AI Architect"
llm_summary: |
  Roadmap for transforming the project into Nexus AI.
  Phases: Local CEO Foundation -> Dockerization -> High Availability -> Multi-Agent Orchestration.
---

# Roadmap: Nexus AI (CEO Transition)

**Vision:** Transform the CDE Orchestrator into **Nexus AI**, a "Chief Executive Officer" system capable of managing software development like a company. It will orchestrate agents, manage high-availability tools, and run securely within a containerized environment.

## Phase 1: Foundation & Local CEO (Current)

**Goal:** Establish the "CEO" logic within the current local environment (`.venv`) ensuring full functionality on Windows without Docker.

- [ ] **Windows Local Compatibility:**
  - [ ] Ensure all paths and subprocess calls are Windows-compatible (PowerShell/CMD).
  - [ ] Verify `gh copilot` and other CLI tools work natively in the local `.venv`.
  - [ ] Implement local process management (instead of containers) for running agents.
- [ ] **Refactor Architecture:**
  - [ ] Define the "CEO" domain model (managing "Employees" vs just "Tools").
  - [ ] Implement `AgentManager` to handle CLI-based agents (Copilot, etc.) locally.
- [ ] **CLI Integration:**
  - [ ] Create robust wrappers for `gh copilot` and other CLIs using `subprocess`.
  - [ ] Ensure authentication state is preserved/shared safely.
- [ ] **Documentation Update:**
  - [x] Rename project to Nexus AI.
  - [x] Update governance and agent instructions.

## Phase 2: Containerization (Docker)

**Goal:** Deploy Nexus AI as a portable, self-contained service.

- [ ] **Docker Setup:**
  - [ ] Create `Dockerfile` based on `python:3.14-slim` (or `uv` based image).
  - [ ] Configure volume mounts for:
    - Project files (the workspace).
    - Authentication credentials (`~/.config/gh`, `.env`).
    - Persistent state (database/logs).
- [ ] **Service Orchestration:**
  - [ ] Create `docker-compose.yml`.
  - [ ] Include services: `nexus-core` (CEO), `redis` (Task Queue), `postgres` (State).

## Phase 3: High Availability & Async Tools

**Goal:** Ensure tools are non-blocking and scalable.

- [ ] **Async Task Queue:**
  - [ ] Implement **Celery** or **RQ** for long-running tool executions (e.g., "Scrape Documentation", "Run Full Test Suite").
  - [ ] Update MCP tools to return `task_id` immediately and allow polling/notification.
- [ ] **Worker Scaling:**
  - [ ] Separate "Heavy Tools" into distinct worker containers.
  - [ ] Configure Docker Compose/K8s to scale worker replicas based on load.

## Phase 4: Multi-Agent Orchestration (The "Company")

**Goal:** Run multiple specialized agents internally.

- [ ] **Internal Agent Runtime:**
  - [ ] Implement a secure sandbox (Docker-in-Docker or sibling containers) to run untrusted agent code.
  - [ ] Create "Department" abstractions:
    - `Engineering` (Coding agents).
    - `QA` (Testing agents).
    - `Product` (Planning agents).
- [ ] **Inter-Agent Communication:**
  - [ ] Implement an event bus (Redis Pub/Sub) for agents to communicate.
  - [ ] The CEO acts as the central message router.

## Phase 5: VPS/Cloud Deployment

**Goal:** Production deployment.

- [ ] **Infrastructure as Code:**
  - [ ] Terraform scripts for AWS/DigitalOcean.
  - [ ] Secure secret management (Vault or Cloud Secrets).
- [ ] **CI/CD Pipeline:**
  - [ ] Auto-build and push Docker images to registry.
  - [ ] Auto-deploy to VPS on merge to main.
