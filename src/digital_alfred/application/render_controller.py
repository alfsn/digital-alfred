from pathlib import Path
from icontract import require
from digital_alfred.core.ports.voice_provider import IVoiceProvider
from digital_alfred.core.ports.avatar_provider import IAvatarProvider

class RenderController:
    def __init__(self, 
                 voice_provider: IVoiceProvider = None, 
                 avatar_provider: IAvatarProvider = None,
                 voice_registry: list = None,
                 avatar_registry: list = None):
        self.voice_provider = voice_provider
        self.avatar_provider = avatar_provider
        self.voice_registry = voice_registry or []
        self.avatar_registry = avatar_registry or []

    @require(lambda text: 10 <= len(text) <= 4000)
    @require(lambda self, voice_alias: voice_alias in self.voice_registry)
    def render_audio(self, text: str, voice_alias: str, output_dir: Path) -> Path:
        """
        Orchestrates the audio generation process.
        """
        if not self.voice_provider:
            raise ValueError("Voice provider not configured.")
        output_path = output_dir / f"{voice_alias}_output.mp3"
        return self.voice_provider.generate_audio(text, voice_alias, output_path)

    @require(lambda text: 10 <= len(text) <= 4000)
    @require(lambda self, voice_alias: voice_alias in self.voice_registry)
    @require(lambda self, avatar_alias: avatar_alias in self.avatar_registry)
    def render_video(self, text: str, avatar_alias: str, voice_alias: str, output_dir: Path) -> Path:
        """
        Orchestrates the video generation process.
        """
        if not self.avatar_provider:
            raise ValueError("Avatar provider not configured.")
        output_path = output_dir / f"{avatar_alias}_{voice_alias}_output.mp4"
        return self.avatar_provider.generate_video(text, avatar_alias, voice_alias, output_path)
