import time
import httpx
from pathlib import Path
from digital_alfred.core.ports.avatar_provider import IAvatarProvider
from digital_alfred.infrastructure.config_loader import ConfigLoader
from tenacity import retry, stop_after_attempt, wait_exponential

class HeyGenAdapter(IAvatarProvider):
    def __init__(self, config_loader: ConfigLoader):
        self.config_loader = config_loader
        self.api_key = config_loader.get_api_key("heygen")
        self.base_url = "https://api.heygen.com/v2"
        self.headers = {
            "X-Api-Key": self.api_key,
            "Content-Type": "application/json"
        }

    def generate_video(self, text: str, avatar_alias: str, voice_alias: str, output_path: Path) -> Path:
        avatar_id = self.config_loader.get_avatar_id(avatar_alias)
        voice_id = self.config_loader.get_voice_id(voice_alias)

        video_id = self._submit_video_request(text, avatar_id, voice_id)
        video_url = self._poll_for_video_completion(video_id)
        return self._download_video(video_url, output_path)

    def _submit_video_request(self, text: str, avatar_id: str, voice_id: str) -> str:
        url = f"{self.base_url}/video_generate"
        payload = {
            "video_inputs": [
                {
                    "character": {
                        "type": "avatar",
                        "avatar_id": avatar_id
                    },
                    "voice": {
                        "type": "text",
                        "input_text": text,
                        "voice_id": voice_id
                    }
                }
            ],
            "dimension": "vertical"
        }
        
        response = httpx.post(url, headers=self.headers, json=payload)
        response.raise_for_status()
        return response.json()["data"]["video_id"]

    def _poll_for_video_completion(self, video_id: str) -> str:
        url = f"{self.base_url}/video_status?video_id={video_id}"
        
        # Initial delay
        time.sleep(30)
        
        max_time = 600  # 10 minutes
        start_time = time.time()
        
        while time.time() - start_time < max_time:
            response = httpx.get(url, headers=self.headers)
            response.raise_for_status()
            data = response.json()["data"]
            status = data["status"]
            
            if status == "completed":
                return data["video_url"]
            elif status == "failed":
                raise Exception(f"HeyGen video generation failed: {data.get('error')}")
            
            time.sleep(10)
            
        raise TimeoutError("HeyGen video generation timed out after 10 minutes.")

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def _download_video(self, url: str, output_path: Path) -> Path:
        with httpx.stream("GET", url) as response:
            response.raise_for_status()
            with open(output_path, "wb") as f:
                for chunk in response.iter_bytes():
                    f.write(chunk)
        return output_path
