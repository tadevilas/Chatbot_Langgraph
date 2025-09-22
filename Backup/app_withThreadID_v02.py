import streamlit as st
from langchain_backend import chatbot  # Import your chatbot object from backend
from langchain_core.messages import HumanMessage  # Message wrapper for user messages
from dotenv import load_dotenv
import os
import uuid

# ------------------- Load Environment -----------------------
load_dotenv()

LANGCHAIN_TRACING_V2 = os.getenv("LANGCHAIN_TRACING_V2")
LANGCHAIN_ENDPOINT = os.getenv("LANGCHAIN_ENDPOINT")
LANGCHAIN_API_KEY = os.getenv("LANGCHAIN_API_KEY")
LANGCHAIN_PROJECT = os.getenv("LANGCHAIN_PROJECT")

# ------------------- Utility Functions -----------------------

def generate_thread_id():
    """Generate a new UUID thread ID."""
    return str(uuid.uuid4())

def reset_chat(thread_name):
    """Reset current chat, assign new thread ID and name, and clear message history."""
    thread_id = generate_thread_id()
    st.session_state['thread_id'] = thread_id
    add_thread(thread_id, thread_name)
    st.session_state['message_history'] = []

def add_thread(thread_id, thread_name):
    """Add a new thread to session state if it doesn't exist."""
    if not any(thread['id'] == thread_id for thread in st.session_state['chat_threads']):
        st.session_state['chat_threads'].append({'id': thread_id, 'name': thread_name})

def load_conversation(thread_id):
    """Load messages from backend state for a given thread."""
    state = chatbot.get_state(config={'configurable': {'thread_id': thread_id}})
    return state.values['messages']

# ------------------- Session Initialization -----------------------

if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []

if 'thread_id' not in st.session_state:
    st.session_state['thread_id'] = generate_thread_id()

if 'chat_threads' not in st.session_state:
    st.session_state['chat_threads'] = []  # [{id, name}]

# ------------------- Sidebar UI -----------------------

st.sidebar.title('🧠 LangGraph Chatbot')

# Start a new chat
with st.sidebar.form('New_chat_form', clear_on_submit=True):
    thread_name = st.text_input("Enter a name for this chat", key='new_chat_name')
    submitted = st.form_submit_button("Start New Chat")
    if submitted and thread_name:
        reset_chat(thread_name)

# List saved chats
st.sidebar.header('📁 My Conversations')

for thread in st.session_state['chat_threads'][::-1]:
    if st.sidebar.button(thread['name']):
        st.session_state['thread_id'] = thread['id']
        messages = load_conversation(thread['id'])

        temp_messages = []
        for msg in messages:
            role = 'user' if isinstance(msg, HumanMessage) else 'assistant'
            temp_messages.append({'role': role, 'content': msg.content})

        st.session_state['message_history'] = temp_messages

# ------------------- Main Chat UI -----------------------

# Show current thread name
current_thread = next((t for t in st.session_state['chat_threads'] if t['id'] == st.session_state['thread_id']), None)
if current_thread:
    st.subheader(f"💬 Chat: {current_thread['name']}")

# Display previous messages
for message in st.session_state['message_history']:
    with st.chat_message(message['role']):
        st.text(message['content'])

# Chat configuration for LangGraph
CONFIG = {'configurable': {'thread_id': st.session_state['thread_id']}}

# Input and Response
user_input = st.chat_input('Type your message here...')

if user_input:
    # Show user message
    st.session_state['message_history'].append({'role': 'user', 'content': user_input})
    with st.chat_message('user'):
        st.text(user_input)

    # Show assistant response with streaming
    with st.chat_message('assistant'):
        ai_message = st.write_stream(
            message_chunk.content for message_chunk, metadata in chatbot.stream(
                {'messages': [HumanMessage(content=user_input)]},
                config=CONFIG,
                stream_mode='messages'
            )
        )

    # Save assistant message
    st.session_state['message_history'].append({'role': 'assistant', 'content': ai_message})
