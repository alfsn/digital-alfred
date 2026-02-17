# Technical Design Document: DigitalAlfred (Worker B)
**Project Name:** digital-alfred  
**Version:** 1.2  
**Author:** Principal Software Architect / Gemini Agent  
**Date:** February 17, 2026  
**Status:** Under Revision  

---

## 1. Executive Summary
DigitalAlfred is a standalone, CLI-driven microservice responsible for the **Productization Layer** of the Alfred Invierte content pipeline. Functioning as "Worker B", it accepts structured text and customization parameters to output high-fidelity media assets (MP3/MP4) featuring the "Alfred" persona.

The system emphasizes **SOLID principles**, **Hexagonal Architecture**, and **Design by Contract (DbC)** to ensure reliability in an environment dependent on expensive third-party generative APIs.

### 1.1 Goals
- **Provider Agnostic:** Swap audio/video providers via configuration without code changes.
- **Fail-Fast Validation:** Use DbC to prevent costly API calls for invalid inputs.
- **High Fidelity:** Standardized output (1080x1920, 9:16 vertical) for social media.
- **CLI-First:** Optimized for headless orchestration by a parent system.

### 1.2 Non-Goals
- **Content Generation:** This tool does not write scripts; it only renders provided text.
- **Video Editing:** Complex multi-scene editing or overlaying text is out of scope for the MVP.
- **Storage Management:** Long-term asset hosting is handled by the caller; this tool only ensures local file creation.

---

## 2. System Architecture
The system follows a **Hexagonal Architecture (Ports and Adapters)** to decouple core business logic from external API volatilities.

### 2.1 Architectural Layers
1.  **Interface Layer (Primary Adapter):** CLI built with `Typer`.
2.  **Application Layer (Core):** `RenderController` orchestrates the workflow.
3.  **Domain Layer (Ports):** `IAvatarProvider` and `IVoiceProvider` abstract interfaces.
4.  **Infrastructure Layer (Secondary Adapters):** `HeyGenAdapter`, `ElevenLabsAdapter`, `ConfigLoader`.

---

## 3. Reliability & Safety (Design by Contract)
We use `icontract` to enforce rigorous runtime checks, categorized as "Wallet Protectors" and "Pipeline Assurance".

### 3.1 Wallet Protectors (Preconditions)
- **Text Length:** Must be between 10 and 4000 characters.
- **Asset Validation:** `avatar_id` and `voice_id` must exist in the local `config.yaml` registry.
- **Resource Check:** Verify internet connectivity and API key presence before execution.

### 3.2 Pipeline Assurance (Postconditions)
- **File Integrity:** Output file must exist and meet a minimum size threshold (e.g., >50KB for video).
- **Format Match:** File extension must match requested mode (.mp3 vs .mp4).

---

## 4. Configuration & Asset Mapping
To reduce API errors, we use a **Preset Strategy** that maps human-readable aliases to provider-specific UUIDs.

### 4.1 config.yaml Structure
```yaml
defaults:
  voice_provider: "elevenlabs"
  video_provider: "heygen"

assets:
  voices:
    alfred_calm: "eleven_uuid_1"
    alfred_hype: "eleven_uuid_2"
  avatars:
    business_suit: "heygen_uuid_1"
    tan_suit: "heygen_uuid_2"
```

---

## 5. Implementation Details

### 5.1 Error Handling & Retries
- **Transient Errors:** 5xx status codes or timeouts will trigger an exponential backoff retry (using `tenacity`).
- **Fatal Errors:** 4xx codes (auth failure, credit exhaustion) will terminate immediately with a non-zero exit code.
- **Contract Violations:** `icontract.ViolationError` will be caught and transformed into human-readable CLI errors.

### 5.2 Observability
- **Structured Logging:** All logs emitted in JSON format for easier parsing by the parent orchestrator.
- **Tracing:** Every request can accept a `--trace-id` flag to link logs across the pipeline.
- **Cost Tracking:** Adapters will log estimated credit usage per successful job.

### 5.3 Asynchronous Polling
Video providers (HeyGen) are asynchronous. The adapter will implement a blocking poll with:
- Initial delay: 30 seconds.
- Interval: 10 seconds.
- Max timeout: 10 minutes.

---

## 6. Security & Secret Management
To prevent accidental exposure of sensitive credentials:
- **Environment Variables:** API keys are loaded via `python-dotenv`.
- **.env Support:** The application will search for a `.env` file in the root directory on startup.
- **Required Keys:**
  - `DIGITAL_ALFRED_HEYGEN_KEY`
  - `DIGITAL_ALFRED_ELEVENLABS_KEY`
- **Exclusion:** `.env` and `*.log` files are strictly added to `.gitignore`.
- **Sanitization:** Text inputs are stripped of control characters before transmission to external APIs.

---

## 7. Testing Strategy
Given the cost of external APIs, testing is divided into three tiers:

### 7.1 Unit Tests (Offline)
- Test `ConfigLoader` with various YAML structures.
- Test `RenderController` logic using mock adapters.
- Validate `icontract` preconditions trigger correctly for invalid inputs.

### 7.2 Integration Tests (Mocked API)
- Use `pytest-recording` or `vcrpy` to capture and replay API responses.
- Verify that adapters correctly parse provider-specific JSON responses into domain objects.

### 7.3 Smoke Tests (Live API)
- Limited execution against live "Sandbox" or "Free-tier" endpoints to verify end-to-end connectivity.
- These tests are skipped by default in CI/CD and only run manually or on specific release branches.

---

## 8. Alternatives Considered
- **Monolithic Scripting:** Rejected in favor of Hexagonal Architecture to allow easy testing of adapters with mocks.
- **SDK vs Raw API:** Chose raw `requests`/`httpx` calls for HeyGen to maintain full control over the polling logic, while using ElevenLabs' official SDK for stability.
- **Python:** Chosen for its rich ecosystem of generative AI libraries and `icontract` support.

---

## 9. Development Roadmap
1.  **Phase 1:** Core scaffolding, `.env` loading, `ConfigLoader`, and `ElevenLabsAdapter`.
2.  **Phase 2:** DbC integration and CLI refinement.
3.  **Phase 3:** `HeyGenAdapter` with polling and asset mapping.
4.  **Phase 4:** Dockerization and JSON logging for production.
