import typer
from pathlib import Path
from digital_alfred.infrastructure.config_loader import ConfigLoader
from digital_alfred.infrastructure.eleven_labs_adapter import ElevenLabsAdapter
from digital_alfred.application.render_controller import RenderController
from icontract import ViolationError
import sys

app = typer.Typer(help="DigitalAlfred: Productization Layer CLI")

@app.command()
def audio(
    text: str = typer.Option(..., help="Text to render as audio"),
    voice: str = typer.Option("alfred_calm", help="Voice alias from config.yaml"),
    output_dir: Path = typer.Option(Path("./output"), help="Directory to save the output")
):
    """
    Renders text into an MP3 file using the configured voice provider.
    """
    try:
        config_loader = ConfigLoader()
        available_voices = config_loader.get_available_voices()
        
        # Determine provider (defaulting to elevenlabs for now as per phase 1)
        # In a more advanced version, we could get this from config defaults
        voice_adapter = ElevenLabsAdapter(config_loader)
        
        controller = RenderController(
            voice_provider=voice_adapter,
            voice_registry=available_voices
        )
        
        if not output_dir.exists():
            output_dir.mkdir(parents=True)
            
        typer.echo(f"Rendering audio for voice: {voice}...")
        result_path = controller.render_audio(text, voice, output_dir)
        typer.echo(f"Success! Audio saved to: {result_path}")
        
    except ViolationError as e:
        typer.secho(f"Contract Violation: {e}", fg=typer.colors.RED, err=True)
        sys.exit(1)
    except Exception as e:
        typer.secho(f"Error: {e}", fg=typer.colors.RED, err=True)
        sys.exit(1)

if __name__ == "__main__":
    app()
