from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage
import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph.message import add_messages
from langchain_core.messages import HumanMessage

load_dotenv()

# Fetch the Groq API key from environment variables
groq_api_key = os.getenv('GROQ_API_KEY')

# Define prompt template with a placeholder
#prompt = PromptTemplate.from_template("{question}")

# Initialize the Groq chat model with the API key and model name
model = ChatGroq(groq_api_key=groq_api_key, model_name='openai/gpt-oss-20b')

#results = model.invoke('What is AI?')
#print(results.content)

class ChatState(TypedDict):
    messages : Annotated[list[BaseMessage], add_messages]

def chat_node(state: ChatState):
    messages = state['messages']
    response = model.invoke(messages)
    return {'messages': [response]}


checkpointer = InMemorySaver()

graph = StateGraph(ChatState)
graph.add_node('chat_node', chat_node)
graph.add_edge(START,'chat_node')
graph.add_edge('chat_node', END)


chatbot = graph.compile(checkpointer=checkpointer)
#chatbot.invoke()
#initial_state = {'messages': [HumanMessage(content="What is AI?")]}
#result = chatbot.invoke(initial_state)
#print(result)

#responce = chatbot.invoke({'message': [HumanMessage(content=user_input)]},config=CONFIG)