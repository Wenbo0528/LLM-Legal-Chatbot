import streamlit as st 
from openai import OpenAI
from rag_utils import extract_text_from_file, split_text_into_chunks, store_chunks, generate_response_with_knowledge_base

# Set up the page title
st.title("💬 Chatbot with RAG")

# Provide a flexible description
st.write(
    "Welcome to the AI-powered chatbot! This application allows you to interact with OpenAI's models "
    "or DeepSeek models to generate intelligent responses. "
    "Ensure you have a valid API key before proceeding."
)

# API Key input moved to the bottom
openai_api_key = st.text_input("Enter your API Key", type="password")

# Allow users to choose a model
model_choice = st.selectbox("Choose a model", ("OpenAI", "DeepSeek"))

# Allow sub-model selection based on the main model choice
if model_choice == "OpenAI":
    sub_model_choice = st.selectbox("Choose a sub-model", ("gpt-3.5-turbo", "gpt-4", "gpt-4o"))
elif model_choice == "DeepSeek":
    sub_model_choice = st.selectbox("Choose a sub-model", ("R1", "V3"))

# Initialize session state for messages
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display existing chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Create a chat input field
if prompt := st.chat_input("Enter your message here..."):
    # Store and display user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate response using selected model
    if model_choice == "OpenAI":
        stream = OpenAI(api_key=openai_api_key).chat.completions.create(
            model=sub_model_choice,
            messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages],
            stream=True,
        )
    elif model_choice == "DeepSeek":
        # Assuming DeepSeekClient is a placeholder for the actual DeepSeek client
        stream = DeepSeekClient(api_key=deepseek_api_key).generate_response(
            model=sub_model_choice,
            messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages],
            stream=True,
        )
    
    # Display response
    with st.chat_message("assistant"):
        response = st.write_stream(stream)
    st.session_state.messages.append({"role": "assistant", "content": response})

# Initialize session state for knowledge base
if 'knowledge_base' not in st.session_state:
    st.session_state.knowledge_base = []


if not openai_api_key:
    st.info("Please enter your API key to continue.", icon="🗝️")
