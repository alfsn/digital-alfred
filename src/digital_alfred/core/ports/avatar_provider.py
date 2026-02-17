from abc import ABC, abstractmethod
from pathlib import Path
from icontract import require, ensure

class IAvatarProvider(ABC):
    @abstractmethod
    @require(lambda text: 10 <= len(text) <= 4000)
    @ensure(lambda result: result.exists())
    @ensure(lambda result: result.stat().st_size > 50 * 1024)  # Minimum 50KB for video as per doc
    def generate_video(self, text: str, avatar_alias: str, voice_alias: str, output_path: Path) -> Path:
        """
        Generates video from text using a specific avatar and voice alias.
        Returns the path to the generated video file.
        """
        pass
