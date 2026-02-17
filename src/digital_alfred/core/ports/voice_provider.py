from abc import ABC, abstractmethod
from pathlib import Path
from icontract import require, ensure

class IVoiceProvider(ABC):
    @abstractmethod
    @require(lambda text: 10 <= len(text) <= 4000)
    @ensure(lambda result: result.exists())
    @ensure(lambda result: result.stat().st_size > 0)
    def generate_audio(self, text: str, voice_alias: str, output_path: Path) -> Path:
        """
        Generates audio from text using a specific voice alias.
        Returns the path to the generated audio file.
        """
        pass
