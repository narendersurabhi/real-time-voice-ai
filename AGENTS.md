# Repository Status Log

## Purpose
This repository contains a starter implementation of a real-time voice AI pipeline with streaming STT, LLM, and TTS components exposed through FastAPI and WebSocket interfaces.

## Current Status
- Initial project scaffold created.
- FastAPI application exposes health and WebSocket endpoints when FastAPI is installed.
- Async pipeline coordinates mocked STT, LLM, and TTS providers for local development.
- Core models use standard-library dataclasses so the pipeline can be exercised without Pydantic.
- Basic tests validate pipeline event flow; API coverage is present and auto-skips if FastAPI is unavailable.

## Change Log
- 2026-03-19: Initialized repository documentation and Python project structure.
- 2026-03-19: Added async voice pipeline orchestration with provider interfaces and mock implementations.
- 2026-03-19: Added FastAPI app, WebSocket endpoint, and tests.
- 2026-03-19: Switched shared models to dataclasses and made API tests resilient to missing optional dependencies.

## Agent Notes
- Read this file before making changes.
- Update both `Current Status` and `Change Log` whenever repository contents change.
- Keep implementation details high level here so future agents can quickly understand repository state.
