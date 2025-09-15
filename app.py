import streamlit as st
from langchain_backend import chatbot  # Importing your chatbot object from backend
from langchain_core.messages import HumanMessage  # Message wrapper for human input
from dotenv import load_dotenv
import os
import uuid

# Load environment variables from .env file
load_dotenv()

# Fetch config values from environment variables
LANGCHAIN_TRACING_V2 = os.getenv("LANGCHAIN_TRACING_V2")
LANGCHAIN_ENDPOINT = os.getenv("LANGCHAIN_ENDPOINT")
LANGCHAIN_API_KEY = os.getenv("LANGCHAIN_API_KEY")
LANGCHAIN_PROJECT = os.getenv("LANGCHAIN_PROJECT")

# ------------------- Utility Functions -----------------------

def generate_thread_id():
    thread_id = uuid.uuid4()
    return thread_id

def reset_chat():
    thread_id = generate_thread_id()
    st.session_state['thread_id'] = thread_id
    add_thread(st.session_state['thread_id'])
    st.session_state['message_history'] = []

def add_thread(thread_id):
    if thread_id not in st.session_state['chat_threads']:
        st.session_state['chat_threads'].append(thread_id)

def load_conversation(thread_id):
    return chatbot.get_state(config={'configurable': {'thread_id': st.session_state['thread_id']}}).values['messages']
# ------------------- Session Setup -----------------------

# Initialize chat message history in Streamlit session state if not already present
if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []

if 'thread_id' not in st.session_state:
    st.session_state['thread_id'] = generate_thread_id()

if 'chat_threads' not in st.session_state:
    st.session_state['chat_threads'] = []

add_thread(st.session_state['thread_id'])




# ------------------- Sidebar UI -----------------------
st.sidebar.title('LangGraph Chatbot')

if st.sidebar.button('New Chat'):
    reset_chat()

st.sidebar.header('My Conversation')

for threads in st.session_state['chat_threads'][::-1]:

    if st.sidebar.button(str(threads)):
        st.session_state['thread_id'] = threads
        messages = load_conversation(threads)

        temp_messages =[]
        for msg in messages:
            if isinstance(msg, HumanMessage):
                role = 'user'
            else:
                role = 'assistant'

            temp_messages.append({'role': role, 'content': msg.content})

        st.session_state['message_history'] = temp_messages
# ------------------- Main UI ---------------------------
# Configuration dictionary to enable features like checkpointing or thread tracking
CONFIG = {'configurable': {'thread_id': st.session_state['thread_id']}}

# Display previous chat messages in the Streamlit app UI
for message in st.session_state['message_history']:
    with st.chat_message(message['role']):  # 'user' or 'assistant'
        st.text(message['content'])  # Show message text

# Input widget where user can type their message
user_input = st.chat_input('Type Here')

if user_input:
    # Save user's message into session state to keep chat history
    st.session_state['message_history'].append({'role': 'user', 'content': user_input})

    # Display the user message immediately in the chat interface
    with st.chat_message('user'):
        st.text(user_input)

    # Instead of calling invoke (commented out), you stream response chunks from chatbot
    with st.chat_message('assistant'):
        # Stream response from the chatbot and write it chunk by chunk in the UI
        ai_message = st.write_stream(
            message_chunk.content for message_chunk, metadata in chatbot.stream(
                {'messages': [HumanMessage(content=user_input)]},  # Pass user input as messages list
                config=CONFIG,                                     # Pass config dict (e.g., for threading)
                stream_mode='messages'                             # Streaming mode for incremental updates
            )
        )
    
    # Append the full assistant response to chat history (ai_message here holds the final text)
    st.session_state['message_history'].append({'role': 'assistant', 'content': ai_message})
