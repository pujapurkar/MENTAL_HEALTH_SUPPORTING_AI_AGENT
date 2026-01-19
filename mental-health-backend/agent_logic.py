def get_agent_response(user_text):
    text = user_text.lower()
    
    # Reasoning & Decision Module
    # 'for' aur 'word' ke beech space hona chahiye
    if any(word in text for word in ["marna", "suicide", "hurt"]):
        state = "High-Risk"
        reply = "I'm concerned. Please call a crisis hotline (988) immediately."
    elif any(word in text for word in ["stress", "tension", "tired"]):
        state = "Stressed"
        reply = "It sounds like you're overwhelmed. Let's try a breathing exercise."
    else:
        state = "Normal"
        reply = "I am here to listen. How are you feeling today?"
        
    return reply, state