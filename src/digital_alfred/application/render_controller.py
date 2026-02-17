from pathlib import Path
from icontract import require
from digital_alfred.core.ports.voice_provider import IVoiceProvider

class RenderController:
    def __init__(self, voice_provider: IVoiceProvider):
        self.voice_provider = voice_provider

    @require(lambda text: 10 <= len(text) <= 4000)
    def render_audio(self, text: str, voice_alias: str, output_dir: Path) -> Path:
        """
        Orchestrates the audio generation process.
        """
        output_path = output_dir / f"{voice_alias}_output.mp3"
        return self.voice_provider.generate_audio(text, voice_alias, output_path)
