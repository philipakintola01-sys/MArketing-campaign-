import discord
import os
from dotenv import load_dotenv
from orchestrator import Orchestrator
from database.schema import DatabaseManager
from web.app import keep_alive

load_dotenv()

from utils.personamanager import PersonaManager

class MediaTeamBot(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.orchestrator = Orchestrator()
        self.db = DatabaseManager()
        self.personas = PersonaManager()
        self.current_agent = "MORGAN"

    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')

    async def on_message(self, message):
        if message.author == self.user or message.webhook_id:
            return

        print(f"[{message.author}] {message.content}")

        # 1. Log user message
        self.db.log_message(sender=message.author.name, role="user", content=message.content)

        # 2. Get history
        history = self.db.get_history()
        
        # 3. Decision Logic
        self.current_agent = self.orchestrator.decide_next_agent(message.content, self.current_agent)

        # 4. Generate Response
        async with message.channel.typing():
            response_text = self.orchestrator.generate_response(self.current_agent, history)

        # 5. Send Response as the specific agent
        await self.personas.send_as_agent(self.current_agent, response_text, message.channel)

        # 6. Command Execution Logic (Autonomous Task handling)
        if "[CMD:" in response_text:
            await self.handle_commands(response_text, message.channel)

        # 7. Log bot message
        self.db.log_message(sender=self.current_agent, role="assistant", content=response_text)

    async def handle_commands(self, text, channel):
        import re
        from automation.image_gen import ImageGenerator
        from automation.github_utils import GithubManager
        
        # Regex to find commands like [CMD: NAME(args)]
        cmds = re.findall(r"\[CMD:\s*(\w+)\((.*?)\)\]", text)
        
        for cmd_name, args in cmds:
            print(f"Executing {cmd_name} with args: {args}")
            
            if cmd_name == "GENERATE_IMAGE":
                gen = ImageGenerator()
                url = gen.generate_image(args)
                await self.personas.send_as_agent("PIXEL", f"I've generated the visual: {url}", channel)
            
            elif cmd_name == "GITHUB_README":
                gh = GithubManager()
                # Split repo and content if possible, or just treat args as repo
                res = gh.update_readme("your-repo-name", args) # Simple placeholder logic
                await self.personas.send_as_agent("CIPHER", res, channel)
            
            elif cmd_name == "POST_LINKED_IN":
                await self.personas.send_as_agent("ECHO", "Initiating LinkedIn browser automation...", channel)
                # Call automation/browser.py logic here

if __name__ == "__main__":
    # Start the web server for Render
    keep_alive()
    
    # Start the bot
    token = os.getenv("DISCORD_TOKEN")
    if token:
        client = MediaTeamBot(intents=discord.Intents.all())
        client.run(token)
    else:
        print("DISCORD_TOKEN not found. Bot cannot start.")
