# Python 3.14 Migration

This document details the migration of the CDE Orchestrator MCP to Python 3.14.

## Summary

The project has been successfully migrated to Python 3.14. All tests pass, and the CI/CD pipelines have been updated to include Python 3.14 in the build matrix.

## Performance Improvements

The migration to Python 3.14 is expected to bring a 10-20% performance improvement in `asyncio` operations.

## Known Issues

There are a number of `RuntimeWarning`s that are generated when running the test suite. These warnings are related to the use of `async` methods in the tests and will be addressed in Sprint 2, which is dedicated to `async` refactoring.

## CI/CD Updates

The following CI/CD files have been updated to include Python 3.14:

- `.github/workflows/ci.yml`
- `.github/workflows/build-wheels.yml`
- `.github/workflows/test-mcp-server.yml`

The `Dockerfile` has also been updated to use the `python:3.14-slim` base image.
