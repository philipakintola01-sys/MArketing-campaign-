import requests
import urllib.parse
import os

class ImageGenerator:
    def __init__(self):
        self.base_url = "https://image.pollinations.ai/prompt/"

    def generate_image(self, prompt: str, width: int = 1024, height: int = 1024) -> str:
        """
        Generates an image URL from Pollinations.ai based on a prompt.
        """
        encoded_prompt = urllib.parse.quote(prompt)
        url = f"{self.base_url}{encoded_prompt}?width={width}&height={height}&nologo=true"
        return url

    def save_image(self, url: str, filename: str):
        response = requests.get(url)
        if response.status_code == 200:
            with open(filename, 'wb') as f:
                f.write(response.content)
            return filename
        return None
