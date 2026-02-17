Technical Design Document for DigitalAlfred (Worker B).
Repository Name: digital-alfred
Technical Design Document: DigitalAlfred v1.0

Author: Principal Software Architect
Date: February 16, 2026
Status: Approved for Implementation
1. Executive Summary

DigitalAlfred is a standalone, CLI-driven microservice responsible for the Productization Layer of the Alfred Invierte content pipeline. It functions as "Worker B" in the broader architecture.

Its single responsibility is to accept a script (text) and a customization configuration, and output a high-fidelity media asset (MP3 audio or MP4 video) featuring the "Alfred" persona.

It adheres to SOLID principles, specifically the Strategy Pattern, to allow hot-swapping of underlying generative providers (e.g., switching from HeyGen to Synthesia, or ElevenLabs to OpenAI Audio) without changing the core business logic.
2. System Architecture

The system follows a Hexagonal Architecture (Ports and Adapters) to decouple the CLI entry point and external APIs from the core rendering logic.
2.1 Architectural Layers

    Interface Layer (Primary Adapter):

        CLI (Click/Typer): Handles user input, flags (--mode), and config loading.

    Application Layer (Core):

        RenderController: Orchestrates the validation, rendering, and file saving.

        DTOs: RenderRequest, RenderResult.

    Domain Layer (Ports):

        IAvatarProvider: Interface for video generation.

        IVoiceProvider: Interface for audio generation.

    Infrastructure Layer (Secondary Adapters):

        HeyGenAdapter: Concrete implementation of IAvatarProvider.

        ElevenLabsAdapter: Concrete implementation of IVoiceProvider.

        ConfigLoader: Handles YAML parsing and environment variable injection.

2.2 Class Diagram
Code snippet

classDiagram
    class RenderRequest {
        +str text
        +str output_path
        +str mode (AUDIO|VIDEO)
        +dict customization (outfit, background)
    }

    class RenderController {
        -IVoiceProvider voice_engine
        -IAvatarProvider video_engine
        +execute(request: RenderRequest)
    }

    %% Ports (Interfaces)
    class IVoiceProvider {
        <<interface>>
        +generate_audio(text, voice_id) Bytes
    }
    class IAvatarProvider {
        <<interface>>
        +generate_video(text, avatar_id, background_url) JobID
        +check_status(job_id) URL
    }

    %% Adapters (Infrastructure)
    class ElevenLabsAdapter {
        +api_key
        +generate_audio()
    }
    class HeyGenAdapter {
        +api_key
        +generate_video()
    }

    %% Dependency Injection
    RenderController --> IVoiceProvider
    RenderController --> IAvatarProvider
    IVoiceProvider <|-- ElevenLabsAdapter
    IAvatarProvider <|-- HeyGenAdapter

2.3 Reliability & Safety (Design by Contract)

We will strictly enforce constraints using the icontract library (standard for Python DbC).
Why DbC here?

    Fail Fast (Preconditions): Prevent calling the expensive API if the input is invalid (e.g., text is too long or empty). Saves money.

    Verify Success (Postconditions): Ensure the file actually exists and has content before the CLI exits. Saves debugging time.

    State Sanity (Invariants): Ensure the RenderController never operates without loaded API keys.

Refined Architecture with DbC

We add a "Contract Layer" that wraps our Domain Logic.
Updated Class Design (Snippet)
Python

import icontract
from pathlib import Path

class IAvatarProvider(ABC):
    
    @icontract.require(lambda text: len(text) > 0, "Text cannot be empty")
    @icontract.require(lambda text: len(text) < 4096, "Text exceeds API limit")
    @icontract.require(lambda output_path: output_path.suffix == ".mp4", "Output must be .mp4")
    @icontract.ensure(lambda output_path: output_path.exists(), "Output file must exist after execution")
    @icontract.ensure(lambda output_path: output_path.stat().st_size > 1024, "Output file cannot be empty (<1KB)")
    @abstractmethod
    def generate_video(self, text: str, avatar_id: str, output_path: Path) -> None:
        """
        Generates a video and saves it to output_path.
        """
        pass

Implementation Strategy

Here is how the specific contracts map to your business risks:
1. The "Wallet Protector" (Preconditions)

These clauses prevent you from sending garbage to the API and getting charged for it.

    Constraint: len(text) > 5

        Reason: Generating a video for "Hi" is a waste of a credit.

    Constraint: avatar_id in VALID_AVATAR_IDS

        Reason: HeyGen API might silently default to a generic avatar if the ID is wrong. We want to crash instead.

    Constraint: customization.background_url is a valid URL.

        Reason: Don't start a 5-minute render job if the background image 404s.

2. The "Pipeline Assurance" (Postconditions)

These clauses ensure the Orchestrator (User) gets exactly what they asked for.

    Constraint: result.duration > 0

        Reason: A video with 0 duration breaks the editor (CapCut/Premiere).

    Constraint: output_file.exists() AND output_file.size > 50kb

        Reason: Sometimes APIs return a "Success" 200 OK but send a corrupt or empty binary stream. We must catch this immediately.

Example: Applying it to the CLI Controller

This ensures that even if you mess up the CLI arguments, the internal logic refuses to execute.
Python

# In RenderController.py

@icontract.invariant(lambda self: self.api_key is not None)
class RenderController:
    
    def __init__(self, config):
        self.config = config
        self.api_key = os.getenv("HEYGEN_KEY")

    @icontract.require(lambda request: request.mode in ["audio", "video"])
    def execute(self, request: RenderRequest):
        # Logic...
        pass

3. Configuration Design (.yaml)

We use a Mapping Strategy for customization. Instead of sending raw prompts like "tan suit" to the API (which is risky/hallucinatory), we map human-readable keys to specific, pre-validated asset IDs in the config.
3.1 config.yaml (Static)

defaults:
  voice_provider: "elevenlabs"
  video_provider: "heygen"
  output_dir: "./output"

providers:
  elevenlabs:
    model_id: "eleven_multilingual_v2"
    stability: 0.5
    similarity_boost: 0.75

  heygen:
    video_dimension: { width: 1080, height: 1920 } # 9:16 Vertical
    mode: "fast"

# The "Preset Strategy" - Maps readable names to provider IDs
assets:
  voices:
    alfred_calm: "VoiceID_Alpha_123"
    alfred_hype: "VoiceID_Beta_456"

  avatars:
    business_suit: "AvatarID_BlueSuit_v2"
    tan_suit: "AvatarID_TanSuit_Summer_v1" # <--- Specific ID for "Tan Suit"
    casual_friday: "AvatarID_Hoodie_v3"

  backgrounds:
    sunset_skyline: "https://assets.alfredinvierte.com/bg/sunset_ba.jpg"
    office_blur: "https://assets.alfredinvierte.com/bg/office_depth.jpg"

4. CLI Interface Design

The CLI is designed to be script-friendly for the orchestrator.
4.1 Command Structure

# Audio Only (Fast, cheap)
python -m digital_alfred render \
  --mode audio \
  --text "Hola, soy Alfred. La inflación te está comiendo." \
  --voice alfred_calm \
  --output ./scene_01.mp3

# Video + Audio (Production)
python -m digital_alfred render \
  --mode video \
  --text "Hola, soy Alfred..." \
  --voice alfred_calm \
  --avatar tan_suit \
  --background sunset_skyline \
  --output ./scene_01.mp4

4.2 Argument Parsing Logic

    Load Config: Read config.yaml.

    Resolve Assets:

        Input --avatar tan_suit -> Lookup assets.avatars.tan_suit -> Result: AvatarID_TanSuit_Summer_v1.

        Error Handling: If key not found, default to business_suit and log warning.

    Dispatch:

        If mode == audio: Call IVoiceProvider.

        If mode == video: Call IAvatarProvider (which may internally call IVoiceProvider if using an external audio source, or use the video provider's TTS).

5. Implementation Details
5.1 The "Polling" Problem (Video)

Video generation is asynchronous. The HeyGenAdapter must implement a smart polling mechanism.

# pseudo-code for HeyGenAdapter
def generate_video(self, text, avatar_id, bg_url):
    # 1. Submit Job
    response = requests.post(..., json={
        "video_inputs": [{
            "character": {"type": "avatar", "avatar_id": avatar_id},
            "voice": {"type": "text", "input_text": text}
        }],
        "dimension": {"width": 1080, "height": 1920}
    })
    job_id = response.json()["data"]["video_id"]
    
    # 2. Poll Status (Block until done)
    while True:
        status = self.check_status(job_id)
        if status == "completed":
            return download_url
        elif status == "failed":
            raise RenderingError("HeyGen failed")
        time.sleep(5) # Rate limit friendly

5.2 Dependency Injection Setup

Using a lightweight container or simple factory pattern in main.py:

def get_provider(config, mode):
    if mode == "audio":
        return ElevenLabsAdapter(api_key=os.getenv("ELEVEN_API_KEY"))
    elif mode == "video":
        return HeyGenAdapter(api_key=os.getenv("HEYGEN_API_KEY"))

        6. Development Roadmap
Phase 1: Setup & Audio (Day 1)

    Initialize Poetry project.

    Define config.yaml structure.

    Implement ElevenLabsAdapter.

    Build CLI for --mode audio.

Phase 2: 

    Dependency: Add icontract to pyproject.toml.

    Implementation:
        Define PreconditionError (Client fault - e.g., bad CLI args).
        Define PostconditionError (Server/Provider fault - e.g., API sent empty file).

    Benefit: The CLI will output clean, actionable errors:

        Bad: KeyError: 'data'

        Good: PreconditionError: Avatar ID 'tan_suit_v2' is not in the allowed configuration.

Phase 3: Video Integration (Day 2)

    Implement HeyGenAdapter.

    Implement Polling Logic.

    Add asset resolution logic (mapping tan_suit -> ID).

Phase 4: Orchestration Readiness (Day 3)

    Add JSON logging (for the Orchestrator to parse).

    Create Dockerfile (ensuring environment reproducibility).

7. Future Proofing (The "Open/Closed" Principle)

If you decide to clone your voice using OpenAI's new engine later:

    Create OpenAIAudioAdapter implementing IVoiceProvider.

    Update config.yaml to set voice_provider: "openai".

    No other code changes required.

8. Relevant Resources

    HeyGen API Docs - Create Video - For checking avatar_id and background parameters.

    ElevenLabs Python SDK - For audio generation.