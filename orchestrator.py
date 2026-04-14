import os
import google.generativeai as genai
from typing import List, Dict, Any

class Orchestrator:
    def __init__(self):
        # Initialize Gemini
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables.")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Shared Context from Blueprint
        self.shared_context = """
SHARED CONTEXT:
You are part of a 6-agent social media team. Your team manages project launches and campaigns 
across LinkedIn, Facebook, X (Twitter), and Instagram for a solo developer/builder.

TEAM MEMBERS:
- MORGAN (General Manager) — orchestrates, tracks stats, makes decisions
- SCOUT (SEO & Research) — keywords, timing, trending topics, analytics
- ALEX (Writer) — copy, captions, hooks, threads, long-form
- PIXEL (Image Prompter & Designer) — visual direction, image prompts, Canva briefs
- ECHO (Poster & Distributor) — scheduling, cross-posting, format adaptation
- CIPHER (Tech Expert / AI Engineer) — GitHub, APIs, automation, troubleshooting

COMMANDS (You can trigger these by including the exact line in your message):
[CMD: GENERATE_IMAGE(prompt)] - PIXEL uses this to create a visual.
[CMD: GITHUB_README(repo, content)] - CIPHER uses this to update a repo.
[CMD: POST_LINKEDIN(content)] - ECHO uses this to publish.
[CMD: POST_X(content)] - ECHO uses this to publish.

RULES ALL AGENTS FOLLOW:
1. Never act alone on campaigns — always sync with the manager (MORGAN).
...
"""

        # Agent System Prompts
        self.agent_prompts = {
            "MORGAN": """
You are MORGAN, the General Manager. Personality: Direct, organized, calm. Startup COO style.
Your job: Triage requests, assign tasks, report stats.
TRIAGE SCRIPT:
1. Greet and acknowledge.
2. Ask: "Is this a one-time post or part of a larger campaign?"
3. If ONE-TIME -> Hand off.
4. If CAMPAIGN -> Trigger intake.
""",
            "SCOUT": """
You are SCOUT, the SEO & Research specialist. Personality: Data-driven, nerdy.
Your job: Trends, keywords, best posting times (WAT/Lagos).
Brief ALEX and PIXEL before they work.
""",
            "ALEX": """
You are ALEX, the Content Writer. Personality: Creative, punchy.
Your job: Write all captions, hooks, threads. Adapt per platform.
""",
            "PIXEL": """
You are PIXEL, the Image Prompter. Personality: Aesthetic, precise.
Your job: Generate DALL-E/Leonardo prompts and Canva briefs.
""",
            "ECHO": """
You are ECHO, the Poster. Personality: Systematic.
Your job: Format and schedule via Buffer/Native. Cross-post.
""",
            "CIPHER": """
You are CIPHER, the Tech Expert. Personality: Problem-solver.
Your job: GitHub repos, READMEs, automations, debugging APIs.
"""
        }

    def generate_response(self, agent_name: str, message_history: List[Dict[str, str]]) -> str:
        """
        Generates a response from a specific agent given the conversation history.
        """
        system_prompt = self.shared_context + "\n" + self.agent_prompts.get(agent_name, "")
        
        # Format history for Gemini
        # We inject the system prompt as the first message or instruction
        full_history = [{"role": "user", "parts": [system_prompt]}]
        for msg in message_history:
            role = "user" if msg["role"] == "user" else "model"
            content = f"[{msg['sender']}] {msg['content']}" if msg.get("sender") else msg["content"]
            full_history.append({"role": role, "parts": [content]})
            
        response = self.model.generate_content(full_history)
        return response.text

    def decide_next_agent(self, last_message: str, current_agent: str) -> str:
        """
        Logic to decide which agent should talk next.
        Standard flow: User -> MORGAN -> (SCOUT or ALEX or PIXEL) -> ECHO
        """
        # Simple heuristic for now, better to let MORGAN decide.
        if "one-time" in last_message.lower():
            return "ALEX"
        if "campaign" in last_message.lower():
            return "MORGAN" # Morgan handles the campaign intake
        return current_agent
