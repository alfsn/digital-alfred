from abc import ABC, abstractmethod
from pathlib import Path
from icontract import require

class IVoiceProvider(ABC):
    @abstractmethod
    @require(lambda text: 10 <= len(text) <= 4000)
    def generate_audio(self, text: str, voice_alias: str, output_path: Path) -> Path:
        """
        Generates audio from text using a specific voice alias.
        Returns the path to the generated audio file.
        """
        pass
