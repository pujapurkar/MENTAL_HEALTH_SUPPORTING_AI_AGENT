import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import EmojiPicker from 'emoji-picker-react'; 
import ReactMarkdown from 'react-markdown';
import './App.css';

// --- VOICE LOGIC  ---
/* const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
const recognition = SpeechRecognition ? new SpeechRecognition() : null;
*/

function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [showPicker, setShowPicker] = useState(false);
  const [isLoading, setIsLoading] = useState(false); 
  const [theme, setTheme] = useState('light'); 
  // const [isListening, setIsListening] = useState(false); 
  // const [isSpeaking, setIsSpeaking] = useState(false); 
  const chatEndRef = useRef(null);

  useEffect(() => {
    // window.speechSynthesis.getVoices(); 
    document.documentElement.setAttribute('data-theme', theme);
  }, [theme]);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // --- Voice-to-Text Logic ---
  /*
  useEffect(() => {
    if (!recognition) return;

    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      setInput(transcript);
      setIsListening(false);
    };

    recognition.onerror = () => setIsListening(false);
    recognition.onend = () => setIsListening(false);
  }, []);

  const startListening = () => {
    if (!recognition) return alert("Your browser does not support voice input.");
    setIsListening(true);
    recognition.lang = 'hi-IN, mr-IN, en-US';
    recognition.start();
  };
  */

  // --- Text-to-Speech Logic  ---
  /*
  const speak = (text) => {
    const cleanText = text.replace(/[#*`_]/g, '');
    const utterance = new SpeechSynthesisUtterance(cleanText);
    const voices = window.speechSynthesis.getVoices();
    
    const hindiVoice = voices.find(voice => 
      voice.lang.includes('hi-IN') && (voice.name.includes('Female') || voice.name.includes('Google'))
    );

    if (hindiVoice) utterance.voice = hindiVoice;
    utterance.lang = 'hi-IN';
    utterance.pitch = 1.1;
    utterance.rate = 0.95;
    utterance.onstart = () => setIsSpeaking(true);
    utterance.onend = () => setIsSpeaking(false);
    window.speechSynthesis.speak(utterance);
  };
  */

  const toggleTheme = () => {
    const themes = ['light', 'dark', 'sunset'];
    const nextTheme = themes[(themes.indexOf(theme) + 1) % themes.length];
    setTheme(nextTheme);
  };

  const onEmojiClick = (emojiData) => {
    setInput((prev) => prev + emojiData.emoji);
  };

  const sendMessage = async () => {
    if (!input.trim() || isLoading) return;

    const userMsg = { text: input, sender: 'user' };
    setMessages(prev => [...prev, userMsg]);
    const currentInput = input; 
    setInput('');
    setShowPicker(false);
    setIsLoading(true); 

    try {
      const response = await axios.post('http://127.0.0.1:8000/chat', { message: currentInput });
      const botMsg = { text: response.data.reply, sender: 'bot' };
      setMessages(prev => [...prev, botMsg]);
      
      // speak(response.data.reply); 
      
    } catch (error) {
      const errorMsg = error.response?.data?.reply || "Server error! Please check Backend.";
      setMessages(prev => [...prev, { text: errorMsg, sender: 'bot' }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="chat-container">
      <header className="chat-header">
        <div className="header-left">
           <button className="theme-btn" onClick={toggleTheme}>
            {theme === 'light' ? '🌙' : theme === 'dark' ? '🌅' : '☀️'}
           </button>
        </div>
        <div className="header-center">
          <h2>🌸 AI Sahayak</h2>
          <p className="status-text">
            {/* Status simplified */}
            <span className="online-dot"></span> Active now
          </p>
        </div>
        <div className="header-right"></div>
      </header>
      
      <div className="chat-box">
        {messages.map((msg, index) => (
          <div key={index} className={`message-wrapper ${msg.sender}`}>
            <div className="message-bubble">
              <ReactMarkdown>{msg.text}</ReactMarkdown>
            </div>
          </div>
        ))}
        
        {isLoading && (
          <div className="message-wrapper bot">
            <div className="message-bubble loading">AI Sahayak is thinking....</div>
          </div>
        )}
        <div ref={chatEndRef} />
      </div>

      <div className="input-area">
        <button className="emoji-toggle-btn" onClick={() => setShowPicker(!showPicker)}>😊</button>
        
        {/*  
        <button 
          className={`mic-btn ${isListening ? 'listening' : ''}`} 
          onClick={startListening}
        >
          {isListening ? '🛑' : '🎙️'}
        </button>
        */}

        {showPicker && (
          <div className="emoji-picker-wrapper">
            <EmojiPicker onEmojiClick={onEmojiClick} width={280} height={350} />
          </div>
        )}

        <input 
          value={input} 
          onChange={(e) => setInput(e.target.value)}
          placeholder="What's on your mind?...."
          onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
          disabled={isLoading} 
        />
        <button 
          className="send-btn" 
          onClick={sendMessage} 
          disabled={isLoading || !input.trim()}
        >
          {isLoading ? "..." : "Send"}
        </button>
      </div>
    </div>
  );
}

export default App;