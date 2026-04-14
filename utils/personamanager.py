import aiohttp
from discord import Webhook
import os

class PersonaManager:
    def __init__(self):
        # Map agent names to Webhook URLs (to be set in .env)
        self.webhooks = {
            "MORGAN": os.getenv("WEBHOOK_MORGAN"),
            "SCOUT": os.getenv("WEBHOOK_SCOUT"),
            "ALEX": os.getenv("WEBHOOK_ALEX"),
            "PIXEL": os.getenv("WEBHOOK_PIXEL"),
            "ECHO": os.getenv("WEBHOOK_ECHO"),
            "CIPHER": os.getenv("WEBHOOK_CIPHER")
        }
        
        # Default avatars (optional)
        self.avatars = {
            "MORGAN": "https://i.imgur.com/WpP8J7y.png",
            "SCOUT": "https://i.imgur.com/9v6N1E4.png",
            "ALEX": "https://i.imgur.com/3p82k5I.png",
            "PIXEL": "https://i.imgur.com/7p8E3kL.png",
            "ECHO": "https://i.imgur.com/8p9K2mL.png",
            "CIPHER": "https://i.imgur.com/4p1M3kN.png"
        }

    async def send_as_agent(self, agent_name: str, content: str, channel):
        webhook_url = self.webhooks.get(agent_name)
        
        if webhook_url:
            async with aiohttp.ClientSession() as session:
                webhook = Webhook.from_url(webhook_url, session=session)
                await webhook.send(content=content, username=agent_name, avatar_url=self.avatars.get(agent_name))
        else:
            # Fallback if no webhook is provided
            await channel.send(f"**{agent_name}**: {content}")
