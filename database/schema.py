from supabase import create_client, Client
import os

class DatabaseManager:
    def __init__(self):
        url: str = os.getenv("SUPABASE_URL")
        key: str = os.getenv("SUPABASE_KEY")
        if not url or not key:
            print("Supabase URL/Key missing. Persistence disabled.")
            self.client = None
        else:
            self.client: Client = create_client(url, key)

    def log_message(self, sender: str, role: str, content: str, conversation_id: str = "default"):
        if not self.client: return
        self.client.table("messages").insert({
            "sender": sender,
            "role": role,
            "content": content,
            "conversation_id": conversation_id
        }).execute()

    def get_history(self, conversation_id: str = "default") -> list:
        if not self.client: return []
        response = self.client.table("messages") \
            .select("*") \
            .eq("conversation_id", conversation_id) \
            .order("created_at") \
            .execute()
        return response.data

    def create_campaign(self, name: str, details: dict):
        if not self.client: return
        self.client.table("campaigns").insert({
            "name": name,
            "details": details,
            "status": "intake"
        }).execute()
