import pytest
import os
from digital_alfred.infrastructure.config_loader import ConfigLoader

def test_config_loader_get_voice_id(tmp_path):
    config_content = """
assets:
  voices:
    test_voice: "uuid_123"
"""
    config_file = tmp_path / "config.yaml"
    config_file.write_text(config_content)
    
    loader = ConfigLoader(config_path=str(config_file))
    assert loader.get_voice_id("test_voice") == "uuid_123"

def test_config_loader_voice_not_found(tmp_path):
    config_content = "assets: {voices: {}}"
    config_file = tmp_path / "config.yaml"
    config_file.write_text(config_content)
    
    loader = ConfigLoader(config_path=str(config_file))
    with pytest.raises(ValueError, match="Voice alias 'unknown' not found"):
        loader.get_voice_id("unknown")

def test_config_loader_get_api_key(tmp_path, monkeypatch):
    config_file = tmp_path / "config.yaml"
    config_file.write_text("defaults: {}")
    
    monkeypatch.setenv("DIGITAL_ALFRED_TEST_KEY", "secret_key")
    loader = ConfigLoader(config_path=str(config_file))
    assert loader.get_api_key("test") == "secret_key"

def test_config_loader_api_key_not_found(tmp_path, monkeypatch):
    config_file = tmp_path / "config.yaml"
    config_file.write_text("defaults: {}")
    
    monkeypatch.delenv("DIGITAL_ALFRED_TEST_KEY", raising=False)
    loader = ConfigLoader(config_path=str(config_file))
    with pytest.raises(ValueError, match="API key for test not found"):
        loader.get_api_key("test")
