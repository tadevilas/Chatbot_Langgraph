import streamlit as st
from langchain_backend import chatbot
from langchain_core.messages import HumanMessage


LANGCHAIN_TRACING_V2="true"
LANGCHAIN_ENDPOINT='https://api.smith.langchain.com'
LANGCHAIN_API_KEY='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'
LANGCHAIN_PROJECT="ChatBot_Project"


# Optional config for checkpointing/thread tracking
CONFIG = {'configurable': {'thread_id': 'thread1'}}

# Initialize message history
if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []

# Display previous messages
for message in st.session_state['message_history']:
    with st.chat_message(message['role']):
        st.text(message['content'])

# Chat input
user_input = st.chat_input('Type Here')

if user_input:
    # Add user message to session state
    st.session_state['message_history'].append({'role': 'user', 'content': user_input})
    with st.chat_message('user'):
        st.text(user_input)

    # Get AI response from LangGraph chatbot
    # response = chatbot.invoke({'messages': [HumanMessage(content=user_input)]}, config=CONFIG)
    # ai_message = response['messages'][-1].content

    # Add AI message to session state
    # st.session_state['message_history'].append({'role': 'assistant', 'content': ai_message})
    with st.chat_message('assistant'):
        #st.text(ai_message)
        ai_message = st.write_stream(
            message_chunk.content for message_chunk, metadata in chatbot.stream(
                {'messages' : [HumanMessage(content=user_input)]},
                config=CONFIG,
                stream_mode= 'messages'
            )
        )
    st.session_state['message_history'].append({'role': 'assistant', 'content': ai_message})
