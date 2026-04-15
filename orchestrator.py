import os
from groq import Groq
from typing import List, Dict, Any

class Orchestrator:
    def __init__(self):
        # Initialize Groq
        self.api_key = os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables.")
        
        self.client = Groq(api_key=self.api_key)
        # Use a reliable model from Groq
        self.model_name = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
        
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
        Generates a response from a specific agent given the conversation history using Groq.
        """
        system_prompt = self.shared_context + "\n" + self.agent_prompts.get(agent_name, "")
        
        # Format history for Groq
        messages = [{"role": "system", "content": system_prompt}]
        for msg in message_history:
            role = "user" if msg["role"] == "user" else "assistant"
            # Add [AgentName] prefix if available for context
            content = f"[{msg['sender']}] {msg['content']}" if msg.get("sender") else msg["content"]
            messages.append({"role": role, "content": content})
            
        try:
            completion = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=0.7,
                max_tokens=2048,
                top_p=1,
                stream=False,
                stop=None,
            )
            
            return completion.choices[0].message.content
            
        except Exception as e:
            print(f"ERROR in Groq Generation: {e}")
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
