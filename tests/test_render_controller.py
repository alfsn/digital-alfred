import pytest
from unittest.mock import MagicMock
from pathlib import Path
from digital_alfred.application.render_controller import RenderController
from digital_alfred.core.ports.voice_provider import IVoiceProvider
from icontract import ViolationError

from digital_alfred.core.ports.avatar_provider import IAvatarProvider

def test_render_audio_success(tmp_path):
    mock_provider = MagicMock(spec=IVoiceProvider)
    mock_provider.generate_audio.return_value = tmp_path / "output.mp3"
    
    controller = RenderController(
        voice_provider=mock_provider, 
        voice_registry=["alfred_calm"]
    )
    text = "This is a valid text length."
    result = controller.render_audio(text, "alfred_calm", tmp_path)
    
    assert result == tmp_path / "output.mp3"
    mock_provider.generate_audio.assert_called_once()

def test_render_video_success(tmp_path):
    mock_provider = MagicMock(spec=IAvatarProvider)
    mock_provider.generate_video.return_value = tmp_path / "output.mp4"
    
    controller = RenderController(
        avatar_provider=mock_provider,
        voice_registry=["alfred_calm"],
        avatar_registry=["business_suit"]
    )
    text = "This is a valid text length."
    result = controller.render_video(text, "business_suit", "alfred_calm", tmp_path)
    
    assert result == tmp_path / "output.mp4"
    mock_provider.generate_video.assert_called_once()

def test_render_audio_too_short():
    mock_provider = MagicMock(spec=IVoiceProvider)
    controller = RenderController(
        voice_provider=mock_provider,
        voice_registry=["alfred_calm"]
    )
    
    with pytest.raises(ViolationError):
        controller.render_audio("too short", "alfred_calm", Path("/tmp"))

def test_render_audio_invalid_voice():
    mock_provider = MagicMock(spec=IVoiceProvider)
    controller = RenderController(
        voice_provider=mock_provider,
        voice_registry=["alfred_calm"]
    )
    
    with pytest.raises(ViolationError):
        controller.render_audio("This is valid text.", "unknown_voice", Path("/tmp"))

def test_render_audio_too_long():
    mock_provider = MagicMock(spec=IVoiceProvider)
    controller = RenderController(voice_provider=mock_provider)
    
    with pytest.raises(ViolationError):
        controller.render_audio("a" * 4001, "alfred_calm", Path("/tmp"))
