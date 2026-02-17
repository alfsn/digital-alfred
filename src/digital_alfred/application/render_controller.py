from pathlib import Path
from icontract import require
from digital_alfred.core.ports.voice_provider import IVoiceProvider

class RenderController:
    def __init__(self, voice_provider: IVoiceProvider, voice_registry: list = None):
        self.voice_provider = voice_provider
        self.voice_registry = voice_registry or []

    @require(lambda text: 10 <= len(text) <= 4000)
    @require(lambda self, voice_alias: voice_alias in self.voice_registry)
    def render_audio(self, text: str, voice_alias: str, output_dir: Path) -> Path:
        """
        Orchestrates the audio generation process.
        """
        output_path = output_dir / f"{voice_alias}_output.mp3"
        return self.voice_provider.generate_audio(text, voice_alias, output_path)
