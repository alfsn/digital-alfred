# How to Operate DigitalAlfred (Worker B)

DigitalAlfred is a CLI-driven microservice for rendering high-fidelity media assets (MP3/MP4). This guide provides instructions on how to configure and run the tool.

## 1. Prerequisites

- **Python 3.11+** (if running locally)
- **Poetry** (for dependency management)
- **Docker** (optional, for containerized execution)
- **API Keys**: You will need keys for ElevenLabs and HeyGen.

## 2. Configuration

### 2.1 Environment Variables
Create a `.env` file in the root directory:
```env
DIGITAL_ALFRED_ELEVENLABS_KEY=your_elevenlabs_key_here
DIGITAL_ALFRED_HEYGEN_KEY=your_heygen_key_here
```

### 2.2 Asset Mapping (`config.yaml`)
Define your human-readable aliases and their provider UUIDs:
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

## 3. Local Execution

First, install dependencies:
```bash
poetry install
```

### 3.1 Generate Audio (MP3)
```bash
PYTHONPATH=src poetry run python -m digital_alfred.main audio 
    --text "Hello, I am Alfred. This is a test of the emergency broadcast system." 
    --voice "alfred_calm" 
    --output-dir "./output" 
    --trace-id "req-123"
```

### 3.2 Generate Video (MP4)
*Note: This command polls HeyGen and may take several minutes.*
```bash
PYTHONPATH=src poetry run python -m digital_alfred.main video 
    --text "Welcome to the future of automated content creation." 
    --avatar "business_suit" 
    --voice "alfred_calm" 
    --output-dir "./output" 
    --trace-id "req-456"
```

## 4. Docker Execution

### 4.1 Build the Image
```bash
docker build -t digital-alfred .
```

### 4.2 Run Audio Generation
```bash
docker run --env-file .env -v $(pwd)/output:/app/output digital-alfred audio 
    --text "This is running inside a container." 
    --output-dir "/app/output"
```

### 4.3 Run Video Generation
```bash
docker run --env-file .env -v $(pwd)/output:/app/output digital-alfred video 
    --text "This video was generated via a Dockerized worker." 
    --avatar "business_suit" 
    --output-dir "/app/output"
```

## 5. Understanding the Output

### 5.1 Logs
All logs are emitted in JSON format to `stdout`. Example:
```json
{"asctime": "2026-02-17 14:00:00,000", "levelname": "INFO", "name": "digital_alfred.main", "message": "Starting audio rendering task", "voice": "alfred_calm", "text_length": 35, "trace_id": "req-123"}
```

### 5.2 Files
Generated assets are saved to the specified `--output-dir`:
- Audio: `{voice_alias}_output.mp3`
- Video: `{avatar_alias}_{voice_alias}_output.mp4`

## 6. Error Handling
- **Exit Code 1**: Business logic error or Contract Violation (e.g., text too short).
- **Exit Code 2**: CLI usage error (missing required arguments).
- **Contract Violations**: If you provide text < 10 characters or an invalid alias, the tool will fail-fast before calling any paid APIs.
