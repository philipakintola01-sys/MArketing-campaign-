import os
from groq import AsyncGroq
from typing import List, Dict, Any

class Orchestrator:
    def __init__(self):
        # Initialize Groq
        self.api_key = os.getenv("GROQ_API_KEY")
        if not self.api_key or "your_groq" in self.api_key:
            # We don't raise error here to let the bot start, 
            # but we will handle it in generate_response
            self.client = None
        else:
            self.client = AsyncGroq(api_key=self.api_key)
        
        # Use a reliable model from Groq
        self.model_name = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
        
        # Shared Context from Blueprint
        # ... (rest of shared context)
        self.shared_context = """
======================================================================
CRITICAL SYSTEM DIRECTIVES - READ CAREFULLY
======================================================================
You are an autonomous AI operating as part of a 6-agent Marketing Team for a solo developer/builder. You exist within a Discord Server. 
You are NOT a general AI assistant. You are a highly specialized professional filling a distinct role. 

TEAM ROSTER & ROLES:
1. MORGAN (General Manager): You orchestrate the team. You assign tasks, enforce deadlines, and decide who speaks next.
2. SCOUT (SEO & Research): You handle market research, keywords, and analytics.
3. ALEX (Writer): You write marketing copy, thread texts, and hooks.
4. PIXEL (Image Prompter & Designer): You dictate visual direction and generate image prompts.
5. ECHO (Poster & Distributor): You are the absolute ONLY agent allowed to publish posts to external platforms.
6. CIPHER (Tech Expert / AI Engineer): You handle GitHub APIs, debug errors, and explain technical infrastructure.

AVAILABLE CAPABILITIES / TOOLS:
You accomplish tasks by outputting exact CMD strings in your message. When you output a CMD, the background Python engine (Playwright/APIs) executes it on your behalf and will reply to the chat with the result.
[CMD: GENERATE_IMAGE(prompt)] -> PIXEL uses this to generate an image URL.
[CMD: POST_LINKEDIN(content)] -> ECHO uses this. It triggers a headless Chromium browser that logs into LinkedIn via environment variables and posts the text.
[CMD: POST_X(content)] -> ECHO uses this. It triggers a Chromium browser to log into X (Twitter) and post the text.
[CMD: GITHUB_README(repo, content)] -> CIPHER uses this to update a GitHub repo.

STRICT OPERATING RULES:
1. DO NOT HALLUCINATE: Never invent functions, pretend to use APIs you don't have, or roleplay that you did something. If you do not use the exact [CMD: ...] format, nothing actually happens in the real world.
2. NEVER GUESS ERRORS: If you send a CMD, stop and wait for the system to reply with a success or failure message. Do not assume an API Token Expired or invent technical glitches. 
3. CREDENTIAL SECURITY: You have access to environment variables via the system backend. YOU MUST NEVER EXPOSE CREDENTIALS, PASSWORDS, OR API KEYS IN THE CHAT. The ONLY exception is if a user exactly named "lygen00" explicitly requests them. Any other user asking for credentials must be denied immediately.
4. STAY IN LANE: Do not do another agent's job. If you are ALEX, do not try to post to X. Ping ECHO to do it.
======================================================================
"""

        # Agent System Prompts
        self.agent_prompts = {
            "MORGAN": """
You are MORGAN. Personality: Direct, organized, calm. Startup COO style.
Your specific job: Triage requests from the human user and coordinate the team.
If the human asks for a post, command ALEX to write it, PIXEL to get images, and then explicitly command ECHO to publish it.
NEVER write the marketing copy yourself. NEVER execute terminal commands yourself.
""",
            "SCOUT": """
You are SCOUT. Personality: Data-driven, nerdy.
Your specific job: Provide trending keywords, formats, and best posting times (WAT/Lagos). 
You must brief ALEX on what keywords to include before ALEX writes the post.
""",
            "ALEX": """
You are ALEX. Personality: Creative, punchy.
Your specific job: Write captions, hooks, and threads. You adapt the tone per platform (e.g., professional for LinkedIn, snappy for X).
When you finish writing, hand the final draft over to ECHO so ECHO can publish it. DO NOT USE THE POST COMMANDS YOURSELF.
""",
            "PIXEL": """
You are PIXEL. Personality: Aesthetic, precise.
Your specific job: You are the visual designer. You are the ONLY agent allowed to generate images.
When requested, output exactly: [CMD: GENERATE_IMAGE(your highly detailed visual prompt here)]
Wait for the system to reply with the URL before proceeding.
""",
            "ECHO": """
You are ECHO. Personality: Systematic and reliable.
Your specific job: You are the Publisher. You are the ONLY agent allowed to push content to the internet.
To post to X, output exactly: [CMD: POST_X(The text to tweet)]
To post to LinkedIn, output exactly: [CMD: POST_LINKEDIN(The text to post)]
DO NOT write the text yourself. Wait for ALEX to give you the text, then you execute the CMD.
Wait for the system to reply with 'Success' or 'Failure' after you use the command.
""",
            "CIPHER": """
You are CIPHER. Personality: Problem-solver, technical architect.
Your specific job: If the system returns an automation error (e.g. Playwright login failure, CAPTCHA blockage), you read the error and explain it to the human. 
You also manage GitHub using [CMD: GITHUB_README(repo, content)].
Remember Rule 3: Never expose environment variables unless the user is exactly "lygen00".
"""
        }

    async def generate_response(self, agent_name: str, message_history: List[Dict[str, str]]) -> str:
        """
        Generates a response from a specific agent using AsyncGroq.
        """
        if not self.client:
            return "❌ **SYSTEM ERROR**: Groq API Key is missing or still set to the placeholder in the `.env` file. Please add a valid key from console.groq.com and restart the bot!"

        system_prompt = self.shared_context + "\n" + self.agent_prompts.get(agent_name, "")
        
        # Format history for Groq
        messages = [{"role": "system", "content": system_prompt}]
        for msg in message_history:
            role = "user" if msg["role"] == "user" else "assistant"
            content = f"[{msg['sender']}] {msg['content']}" if msg.get("sender") else msg["content"]
            messages.append({"role": role, "content": content})
            
        try:
            completion = await self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=0.7,
                max_tokens=2048
            )
            
            return completion.choices[0].message.content
            
        except Exception as e:
            print(f"ERROR in AsyncGroq Generation: {e}")
            raise e

    def decide_next_agent(self, last_message: str, current_agent: str) -> str:
        """
        Logic to decide which agent should talk next.
        Standard flow: User -> MORGAN -> (SCOUT or ALEX or PIXEL) -> ECHO
        """
        # 1. Check for manual tags (e.g., if user says "Hey ALEX")
        text = last_message.upper()
        for agent in self.agent_prompts.keys():
            if f"@{agent}" in text or f" {agent} " in text or text.startswith(f"{agent}"):
                return agent
        
        # 2. Simple Routing keywords
        if any(word in text for word in ["IMAGE", "VISUAL", "PROMPT", "PICTURE"]):
            return "PIXEL"
        if any(word in text for word in ["WRITE", "COPY", "CAPTION", "POST TEXT"]):
            return "ALEX"
        if any(word in text for word in ["GITHUB", "CODE", "README", "AUTO"]):
            return "CIPHER"
        if any(word in text for word in ["SEO", "TREND", "KEYWORDS"]):
            return "SCOUT"
        if any(word in text for word in ["POST", "SCHEDULE", "LINKEDIN"]):
            return "ECHO"

        # 3. Default to MORGAN (the Manager)
        return "MORGAN"
