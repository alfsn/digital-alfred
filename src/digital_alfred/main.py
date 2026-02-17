import typer
from pathlib import Path
from digital_alfred.infrastructure.config_loader import ConfigLoader
from digital_alfred.infrastructure.eleven_labs_adapter import ElevenLabsAdapter
from digital_alfred.application.render_controller import RenderController
from icontract import ViolationError
import sys

from digital_alfred.infrastructure.hey_gen_adapter import HeyGenAdapter
from digital_alfred.core.ports.avatar_provider import IAvatarProvider

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

@app.command()
def video(
    text: str = typer.Option(..., help="Text to render as video"),
    avatar: str = typer.Option("business_suit", help="Avatar alias from config.yaml"),
    voice: str = typer.Option("alfred_calm", help="Voice alias from config.yaml"),
    output_dir: Path = typer.Option(Path("./output"), help="Directory to save the output")
):
    """
    Renders text into an MP4 file using the configured avatar and voice providers.
    """
    try:
        config_loader = ConfigLoader()
        available_voices = config_loader.get_available_voices()
        available_avatars = config_loader.get_available_avatars()
        
        avatar_adapter = HeyGenAdapter(config_loader)
        
        controller = RenderController(
            avatar_provider=avatar_adapter,
            voice_registry=available_voices,
            avatar_registry=available_avatars
        )
        
        if not output_dir.exists():
            output_dir.mkdir(parents=True)
            
        typer.echo(f"Rendering video for avatar: {avatar} and voice: {voice}...")
        result_path = controller.render_video(text, avatar, voice, output_dir)
        typer.echo(f"Success! Video saved to: {result_path}")
        
    except ViolationError as e:
        typer.secho(f"Contract Violation: {e}", fg=typer.colors.RED, err=True)
        sys.exit(1)
    except Exception as e:
        typer.secho(f"Error: {e}", fg=typer.colors.RED, err=True)
        sys.exit(1)

if __name__ == "__main__":
    app()
