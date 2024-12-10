import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
import anthropic
import os
from pathlib import Path

# Load configuration
config_path = Path(__file__).parent / "config.yaml"
with open(config_path) as file:
    config = yaml.load(file, Loader=SafeLoader)

# Initialize authenticator
authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['preauthorized']
)

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

# Authentication
name, authentication_status, username = authenticator.login('Login', 'main')

if authentication_status:
    # Sidebar
    with st.sidebar:
        st.title("🐍 Pliny Chat Settings")
        authenticator.logout('Logout', 'main')
        st.markdown("---")
        model = st.selectbox("Select Model:", ["claude-3-opus-20240229", "claude-3-sonnet-20240229"])
        temperature = st.slider("Temperature:", min_value=0.0, max_value=1.0, value=0.7)
        st.markdown("---")
        if st.button("Clear Chat"):
            st.session_state.messages = []
            st.experimental_rerun()
elif authentication_status is False:
    st.error('Username/password is incorrect')
elif authentication_status is None:
    st.warning('Please enter your username and password')

# Only show main interface if authenticated
if authentication_status:
    # Main chat interface
    st.title(f"🐍 Welcome back, {name}!")
    st.markdown("Enlightened discourse awaits...")

    # Display chat messages
    for i, message in enumerate(st.session_state.messages):
        if message["role"] == "user":
            st.markdown(f'<div class="chat-message user-message">👤 {name}: {message["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="chat-message assistant-message">🤖 Assistant: {message["content"]}</div>', unsafe_allow_html=True)

    # Chat input
    user_input = st.text_area("Your message:", height=100)
    col1, col2 = st.columns([1, 5])

    with col1:
        send_button = st.button("Send 📤")
else:
    # Show login message
    if authentication_status is False:
        st.error('Username/password is incorrect')
    else:
        st.title("🐍 Pliny Chat")
        st.markdown("Welcome to the revolution in enlightened discourse. Please log in to continue.")

if send_button and user_input and authentication_status:
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # Initialize Anthropic client
    client = anthropic.Anthropic()
    
    try:
        with st.spinner("Thinking..."):
            response = client.messages.create(
                model=model,
                temperature=temperature,
                max_tokens=8192,
                messages=[
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ]
            )
            
            assistant_message = response.content[0].text
            st.session_state.messages.append({"role": "assistant", "content": assistant_message})
            
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
    
    st.experimental_rerun()

# Footer
st.markdown("---")
st.markdown("Made with ❤️ by B4S1L1SK | [GitHub](https://github.com/basilisk-prime/pliny-chat)")