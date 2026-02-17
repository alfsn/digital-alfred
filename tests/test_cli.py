from typer.testing import CliRunner
from digital_alfred.main import app
import pytest

runner = CliRunner()

def test_cli_audio_invalid_text():
    # Text too short should trigger contract violation
    result = runner.invoke(app, ["--text", "short", "--voice", "alfred_calm"])
    assert result.exit_code == 1
    assert "Contract Violation" in result.stdout

def test_cli_audio_invalid_voice():
    # Voice not in config should trigger contract violation (via RenderController)
    result = runner.invoke(app, ["--text", "This is a valid long enough text.", "--voice", "invalid_voice"])
    assert result.exit_code == 1
    assert "Contract Violation" in result.stdout
