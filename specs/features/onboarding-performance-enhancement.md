---
title: "Onboarding Performance Enhancement"
description: "A feature to refactor the cde_onboardingProject tool for high performance by adopting an async, iterator-based, and lazy-loading architecture."
type: "feature"
status: "draft"
created: "2025-11-02"
updated: "2025-11-02"
author: "Gemini"
tags:
  - "performance"
  - "onboarding"
  - "async"
  - "refactor"
llm_summary: |
  This document specifies a performance-focused refactoring of the project onboarding tool. It replaces the current slow, file-intensive analysis with a modern, asynchronous architecture inspired by best-in-class open-source tools like PyDriller. The goal is to drastically reduce latency and memory usage for a better user experience.
---

# Onboarding Performance Enhancement

## 1. Problem Statement

The current implementation of the `cde_onboardingProject` tool is slow and consumes significant memory, especially on large repositories. This is caused by several factors:
- **Full Repository Scans:** The tool walks the entire file system tree multiple times.
- **Eager File Loading:** The `RepoIngestor` reads the entire content of every text file into memory.
- **Blocking I/O:** All file system and Git operations are synchronous, blocking the main application thread.
- **Redundant Operations:** The analysis logic performs duplicate work.

This results in a poor user experience, with long wait times when onboarding a new project.

## 2. Proposed Solution

To address these performance issues, this feature proposes a complete refactoring of the onboarding analysis logic. The new architecture will be asynchronous, iterator-based, and will use lazy loading to minimize I/O and memory usage. The principles are inspired by high-performance tools like **PyDriller**.

The core of the solution involves the following components:

### 2.1. Smart `GitAdapter`

A new adapter dedicated to all Git operations, built with modern practices.

- **Async Subprocesses:** It will use `asyncio.create_subprocess_exec` to run `git` commands asynchronously, preventing the event loop from blocking.
- **Streaming Output:** It will process the output of `git log` and other commands as a stream, rather than loading it all into memory.
- **Commit Iterator:** It will expose an `async def traverse_commits()` generator, allowing the application to process the commit history one commit at a time.

### 2.2. Rich Domain Models

Clean, decoupled `dataclasses` will represent Git concepts.

- **`Commit`:** A model representing a single commit's metadata (hash, author, date, message).
- **`Modification`:** A model representing a single file change within a commit.

### 2.3. Lazy Loading of Content

The system will avoid reading file content until it is absolutely necessary.

- The `Commit` model will have an `async def get_modifications()` method that only runs `git show` for that specific commit when called.
- The `Modification` model will have an `async def get_source_code()` method that only runs `git show <hash>:<path>` when called.
- This eliminates the need for the current `RepoIngestor` and its "read everything" approach.

### 2.4. Refactored `OnboardingUseCase`

The use case will be simplified to orchestrate the analysis, relying on the new adapter and domain models.

- It will use the `GitAdapter`'s commit iterator to get project history.
- It will analyze file paths and modifications from the Git history to determine tech stack and structure, avoiding full file system scans.
- The logic will be streamlined to remove redundant operations.

## 3. Acceptance Criteria

- The refactored `cde_onboardingProject` tool must complete its analysis on a repository with 10,000+ files and a 5,000+ commit history in **under 15 seconds**.
- The memory usage of the tool during analysis must not grow proportionally with the size of the repository.
- The new implementation must be fully asynchronous and non-blocking.
- All existing functionality of the onboarding tool (structure detection, plan generation) must be preserved.
- The new code must follow the project's hexagonal architecture and include comprehensive unit and integration tests.

## 4. High-Level Plan

1.  **Create Specification & Task Plan:** Formalize the feature and create a granular task list (this document and the corresponding task document).
2.  **Implement `GitAdapter`:** Build the new adapter for efficient, async Git operations.
3.  **Define Domain Models:** Create the `Commit` and `Modification` domain models.
4.  **Refactor `OnboardingUseCase`:** Update the use case to use the new adapter and models.
5.  **Write Tests:** Add unit tests for the new domain models and integration tests for the `GitAdapter`.
6.  **Remove Old Code:** Deprecate and remove the old `RepoIngestor` and the slow analysis methods in the use case.

---
