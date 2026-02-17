from pathlib import Path
from elevenlabs.client import ElevenLabs
from digital_alfred.core.ports.voice_provider import IVoiceProvider
from digital_alfred.infrastructure.config_loader import ConfigLoader

class ElevenLabsAdapter(IVoiceProvider):
    def __init__(self, config_loader: ConfigLoader):
        self.config_loader = config_loader
        self.api_key = config_loader.get_api_key("elevenlabs")
        self.client = ElevenLabs(api_key=self.api_key)

    def generate_audio(self, text: str, voice_alias: str, output_path: Path) -> Path:
        voice_id = self.config_loader.get_voice_id(voice_alias)
        
        audio = self.client.generate(
            text=text,
            voice=voice_id,
            model="eleven_multilingual_v2"
        )
        
        # elevenlabs client returns a generator of bytes or bytes
        with open(output_path, "wb") as f:
            if isinstance(audio, bytes):
                f.write(audio)
            else:
                for chunk in audio:
                    f.write(chunk)
                    
        return output_path
