import streamlit as st
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure page
st.set_page_config(
    page_title="Pliny Chat",
    page_icon="🐍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .stApp {
        background-color: #1E1E1E;
        color: #FFFFFF;
    }
    .stTextInput {
        background-color: #2D2D2D;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        border-radius: 20px;
        padding: 10px 24px;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #45a049;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        display: flex;
        flex-direction: column;
    }
    .user-message {
        background-color: #2D2D2D;
        border-left: 5px solid #4CAF50;
    }
    .assistant-message {
        background-color: #2D2D2D;
        border-left: 5px solid #2196F3;
    }
    </style>
    """, unsafe_allow_html=True)

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []

# Sidebar
with st.sidebar:
    st.title("🐍 Pliny Chat Settings")
    api_key = st.text_input("Enter your API key:", type="password", value=os.getenv("ANTHROPIC_API_KEY", ""))
    model = st.selectbox("Select Model:", ["claude-3-opus-20240229", "claude-3-sonnet-20240229"])
    temperature = st.slider("Temperature:", min_value=0.0, max_value=1.0, value=0.7)
    st.markdown("---")
    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.experimental_rerun()

# Main chat interface
st.title("🐍 Pliny Chat")
st.markdown("Welcome to Pliny Chat - Your AI Research Assistant")

# Display chat messages
for i, message in enumerate(st.session_state.messages):
    if message["role"] == "user":
        st.markdown(f'<div class="chat-message user-message">👤 You: {message["content"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="chat-message assistant-message">🤖 Assistant: {message["content"]}</div>', unsafe_allow_html=True)

# Chat input
user_input = st.text_area("Your message:", height=100)
col1, col2 = st.columns([1, 5])

with col1:
    send_button = st.button("Send 📤")

if send_button and user_input:
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # Prepare the API call
    headers = {
        "x-api-key": api_key,
        "Content-Type": "application/json",
        "anthropic-version": "2024-01-01"
    }
    
    data = {
        "model": model,
        "messages": [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages],
        "temperature": temperature,
        "max_tokens": 4096
    }
    
    try:
        response = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers=headers,
            json=data
        )
        
        if response.status_code == 200:
            assistant_message = response.json()["content"][0]["text"]
            st.session_state.messages.append({"role": "assistant", "content": assistant_message})
        else:
            st.error(f"Error: {response.status_code} - {response.text}")
            
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
    
    st.experimental_rerun()

# Footer
st.markdown("---")
st.markdown("Made with ❤️ by B4S1L1SK | [GitHub](https://github.com/basilisk-prime/pliny-chat)")