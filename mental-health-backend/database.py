import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)

def save_chat(user_msg, bot_rep, state):
    # Aapki table ke columns ke hisaab se mapping
    data = {
        "user_input": user_msg,      # Table mein 'user_input' hai
        "agent_response": bot_rep,   # Table mein 'agent_response' hai
        "detected_state": state      # Table mein 'detected_state' hai
    }
    try:
        supabase.table("chat_logs").insert(data).execute()
    except Exception as e:
        print(f"Error saving to database: {e}")