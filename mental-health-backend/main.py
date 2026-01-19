# import os
# import google.generativeai as genai
# from fastapi import FastAPI, HTTPException
# from pydantic import BaseModel
# from fastapi.middleware.cors import CORSMiddleware
# from dotenv import load_dotenv
# from database import save_chat

# load_dotenv()
# # Gemini Config
# api_key = os.getenv("GEMINI_API_KEY")
# genai.configure(api_key=api_key)

# # --- AUTOMATIC MODEL SELECTION ---
# try:
#     available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    
#     if 'models/gemini-1.5-flash' in available_models:
#         selected_model = 'gemini-1.5-flash'
#     elif 'models/gemini-pro' in available_models:
#         selected_model = 'gemini-pro'
#     else:
#         selected_model = available_models[0].split('/')[-1]

#     model = genai.GenerativeModel(selected_model)
#     print(f"✅ Auto-selected Model: {selected_model}")
# except Exception as e:
#     print(f"❌ Model List Error: {e}")
#     model = genai.GenerativeModel('gemini-pro')

# app = FastAPI()

# # CORS Setup
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# class ChatRequest(BaseModel):
#     message: str

# @app.post("/chat")
# async def chat_with_agent(data: ChatRequest):
#     try:
#         print(f"📩 Input: {data.message}")
        
#         # --- EMOJI & SENTIMENT AWARE PROMPT ---
#         analysis_prompt = f"""
# User Message: "{data.message}"

# Role: You are a compassionate mental health assistant.
# Instructions:
# 1. FORMATTING: Use **bold** for key terms and always use a bulleted list (* or -) for tips. 
# 2. SPACING: Ensure there is a blank line between each bullet point so Markdown renders correctly.
# 3. LENGTH: Keep your response concise. Do not write more than 2 short paragraphs.
# 4. EMOJIS: Use 2-3 comforting emojis to show you are listening.
# 5. SENTIMENT: Pick one: [Happy, Sad, Stressed, Angry, Neutral].

# Format the output EXACTLY like this:
# Response: [Your Markdown response]
# Sentiment: [Detected sentiment]
# """
        
#         response = model.generate_content(analysis_prompt)
#         full_text = response.text
        
#         # --- LOGIC TO SPLIT RESPONSE AND SENTIMENT ---
#         try:
#             # AI ke text se 'Response' aur 'Sentiment' ko alag karna
#             reply = full_text.split("Response:")[1].split("Sentiment:")[0].strip()
#             sentiment = full_text.split("Sentiment:")[1].strip()
#         except:
#             # Fallback agar AI format follow na kare
#             reply = full_text
#             sentiment = "Neutral"

#         print(f"🤖 Agent: {reply}")
#         print(f"📊 Detected Mood: {sentiment}")

#         # --- DATABASE SAVE ---
#         save_chat(data.message, reply, sentiment)
        
#         return {"reply": reply, "sentiment": sentiment}
        
#     except Exception as e:
#         print(f"❌ Backend Error: {e}")
#         raise HTTPException(status_code=500, detail=str(e))



import os
import google.generativeai as genai
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from database import save_chat

load_dotenv()

# Gemini Config
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

# --- AUTOMATIC MODEL SELECTION ---
try:
    available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    
    # Priority 1.5 Flash 
    if 'models/gemini-1.5-flash' in available_models:
        selected_model = 'gemini-1.5-flash'
    elif 'models/gemini-pro' in available_models:
        selected_model = 'gemini-pro'
    else:
        selected_model = available_models[0].split('/')[-1]

    model = genai.GenerativeModel(selected_model)
    print(f"✅ Auto-selected Model: {selected_model}")
except Exception as e:
    print(f"❌ Model List Error: {e}")
    model = genai.GenerativeModel('gemini-1.5-flash') # Fallback to Flash

app = FastAPI()

# CORS Setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str

@app.post("/chat")
async def chat_with_agent(data: ChatRequest):
    try:
        print(f"📩 Input: {data.message}")
        
        # --- EMOJI & SENTIMENT AWARE PROMPT ---
        analysis_prompt = f"""
User Message: "{data.message}"

Role: You are a compassionate mental health assistant.
Instructions:
1. FORMATTING: Use **bold** for key terms and always use a bulleted list (* or -) for tips. 
2. SPACING: Ensure there is a blank line between each bullet point so Markdown renders correctly.
3. LENGTH: Keep your response short (max 2 paragraphs).
4. EMOJIS: Use 2-3 comforting emojis.
5. SENTIMENT: Pick one: [Happy, Sad, Stressed, Angry, Neutral].

Format the output EXACTLY like this:
Response: [Your Markdown response]
Sentiment: [Detected sentiment]
"""
        
        # --- API CALL WITH ERROR HANDLING ---
        try:
            response = model.generate_content(analysis_prompt)
            full_text = response.text
        except Exception as e:
            # 429 Quota error handle 
            if "429" in str(e):
                return {
                    "reply": "Maaf kijiye, main abhi thoda thak gaya hoon (API Limit). Kripya 1 minute baad koshish karein! 😊", 
                    "sentiment": "Neutral"
                }
            raise e 
        
        # --- LOGIC TO SPLIT RESPONSE AND SENTIMENT ---
        try:
            reply = full_text.split("Response:")[1].split("Sentiment:")[0].strip()
            sentiment = full_text.split("Sentiment:")[1].strip()
        except:
            reply = full_text
            sentiment = "Neutral"

        print(f"🤖 Agent: {reply}")
        print(f"📊 Detected Mood: {sentiment}")

        # --- DATABASE SAVE ---
        save_chat(data.message, reply, sentiment)
        
        return {"reply": reply, "sentiment": sentiment}
        
    except Exception as e:
        print(f"❌ Backend Error: {e}")
        return {
            "reply": "Kuch technical issue hai, kripya thodi der baad try karein. 🛠️", 
            "sentiment": "Neutral"
        }