import yaml
import os
from pathlib import Path
from dotenv import load_dotenv

class ConfigLoader:
    def __init__(self, config_path: str = "config.yaml"):
        self.config_path = Path(config_path)
        self.config = self._load_yaml()
        load_dotenv()

    def _load_yaml(self):
        if not self.config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
        with open(self.config_path, "r") as f:
            return yaml.safe_load(f)

    def get_voice_id(self, alias: str) -> str:
        voices = self.config.get("assets", {}).get("voices", {})
        if alias not in voices:
            raise ValueError(f"Voice alias '{alias}' not found in configuration.")
        return voices[alias]

    def get_available_voices(self) -> list:
        return list(self.config.get("assets", {}).get("voices", {}).keys())

    def get_api_key(self, provider: str) -> str:
        env_var = f"DIGITAL_ALFRED_{provider.upper()}_KEY"
        key = os.getenv(env_var)
        if not key:
            raise ValueError(f"API key for {provider} not found in environment (expected {env_var}).")
        return key

    def get_defaults(self):
        return self.config.get("defaults", {})
