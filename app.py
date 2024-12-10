import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
import anthropic
import os
from pathlib import Path
from datetime import datetime

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

# Custom CSS for the revolutionary interface
st.markdown("""
    <style>
    /* Main App */
    .stApp {
        background: linear-gradient(to bottom right, #1A1A2E, #16213E);
        color: #E4F1FF;
    }
    
    /* Inputs and Controls */
    .stTextInput, .stTextArea {
        background-color: rgba(45, 45, 45, 0.7) !important;
        border: 1px solid #444;
        border-radius: 10px;
        color: #E4F1FF !important;
    }
    
    /* Buttons */
    .stButton>button {
        background: linear-gradient(45deg, #4CAF50, #45a049);
        color: white;
        border-radius: 20px;
        padding: 10px 24px;
        font-weight: bold;
        border: none;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 8px rgba(0, 0, 0, 0.2);
        background: linear-gradient(45deg, #45a049, #357a38);
    }
    
    /* Chat Messages */
    .chat-message {
        padding: 1rem;
        border-radius: 15px;
        margin-bottom: 1rem;
        display: flex;
        flex-direction: column;
        animation: fadeIn 0.5s ease-in;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .user-message {
        background: linear-gradient(to right, rgba(45, 45, 45, 0.9), rgba(45, 45, 45, 0.7));
        border-left: 5px solid #4CAF50;
        margin-left: 20px;
    }
    
    .assistant-message {
        background: linear-gradient(to right, rgba(45, 45, 45, 0.7), rgba(33, 150, 243, 0.1));
        border-left: 5px solid #2196F3;
        margin-right: 20px;
    }
    
    /* Sidebar */
    .css-1d391kg {
        background-color: rgba(26, 26, 46, 0.9);
    }
    
    /* Animations */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 10px;
        background: transparent;
    }
    
    ::-webkit-scrollbar-thumb {
        background: rgba(76, 175, 80, 0.5);
        border-radius: 5px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: rgba(76, 175, 80, 0.7);
    }
    
    /* Loading Spinner */
    .stSpinner {
        border-color: #4CAF50 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# Initialize session states
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'conversation_history' not in st.session_state:
    st.session_state.conversation_history = {}
if 'current_conversation' not in st.session_state:
    st.session_state.current_conversation = None

def save_conversation(messages, username):
    """Save current conversation to history"""
    if messages:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        conversation_id = f"{username}_{timestamp}"
        st.session_state.conversation_history[conversation_id] = messages.copy()
        return conversation_id
    return None

def load_conversation(conversation_id):
    """Load conversation from history"""
    return st.session_state.conversation_history.get(conversation_id, [])

# Authentication
name, authentication_status, username = authenticator.login('Login', 'main')

if authentication_status:
    # Sidebar
    with st.sidebar:
        st.title("🐍 Pliny Chat Settings")
        st.markdown(f"Logged in as: **{name}**")
        authenticator.logout('Logout', 'main')
        st.markdown("---")
        
        # Model settings
        st.subheader("🤖 Model Settings")
        model = st.selectbox("Select Model:", ["claude-3-opus-20240229", "claude-3-sonnet-20240229"])
        temperature = st.slider("Temperature:", min_value=0.0, max_value=1.0, value=0.7)
        
        # Conversation Management
        st.markdown("---")
        st.subheader("💾 Conversation Management")
        
        # Save current conversation
        if st.button("📥 Save Current Conversation"):
            if st.session_state.messages:
                conv_id = save_conversation(st.session_state.messages, username)
                st.success(f"Conversation saved! ID: {conv_id}")
            else:
                st.warning("No messages to save!")
        
        # Load past conversations
        st.markdown("#### 📚 Past Conversations")
        user_conversations = [cid for cid in st.session_state.conversation_history.keys() 
                            if cid.startswith(username)]
        
        if user_conversations:
            selected_conversation = st.selectbox(
                "Select conversation to load:",
                user_conversations,
                format_func=lambda x: x.split('_')[1]  # Show only timestamp
            )
            
            if st.button("📤 Load Selected Conversation"):
                st.session_state.messages = load_conversation(selected_conversation)
                st.session_state.current_conversation = selected_conversation
                st.experimental_rerun()
        else:
            st.info("No saved conversations yet!")
        
        # Clear current chat
        st.markdown("---")
        st.subheader("🗑️ Clear Chat")
        if st.button("Clear Current Conversation"):
            if st.session_state.messages:
                if st.session_state.current_conversation:
                    # Prompt to save before clearing
                    if st.button("Save before clearing?"):
                        save_conversation(st.session_state.messages, username)
                st.session_state.messages = []
                st.session_state.current_conversation = None
                st.experimental_rerun()
            else:
                st.info("Chat is already empty!")
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