import streamlit as st 
from openai import OpenAI
from rag_utils import extract_text_from_file, split_text_into_chunks, store_chunks, generate_response_with_knowledge_base

st.set_page_config(page_title="💬 Legal-RAGChatBot")

with st.sidebar:
    st.title('💬 Chatbot with RAG')

# Set up the page title
st.title("💬 Chatbot with RAG")

# Provide a flexible description
st.write(
    "Welcome to the AI-powered chatbot! This application allows you to interact with OpenAI's models "
    "or DeepSeek models to generate intelligent responses. "
    "Ensure you have a valid API key before proceeding."
)

# API Key input
openai_api_key = st.text_input("Enter your API Key", type="password")

# Allow users to choose a model
model_choice = st.selectbox("Choose a model", ("OpenAI", "DeepSeek"))

# Allow sub-model selection based on the main model choice
if model_choice == "OpenAI":
    sub_model_choice = st.selectbox("Choose a sub-model", ("gpt-3.5-turbo", "gpt-4", "gpt-4o"))
elif model_choice == "DeepSeek":
    sub_model_choice = st.selectbox("Choose a sub-model", ("R1", "V3"))

# Initialize session state for chat messages
if "messages" not in st.session_state:
    st.session_state.messages = []

# Initialize session state for knowledge base
if "knowledge_base" not in st.session_state:
    st.session_state.knowledge_base = []

# Display existing chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# File uploader for knowledge base
uploaded_file = st.file_uploader("Upload a file", type=["csv", "pdf", "txt", "docx"])

if uploaded_file is not None:
    text = extract_text_from_file(uploaded_file)  # Extract text from file
    chunks = split_text_into_chunks(text)  # Split text into chunks
    store_chunks(chunks, st.session_state.knowledge_base)  # Store chunks in session state
    st.success("File processed and added to knowledge base.")

# Create a chat input field
if prompt := st.chat_input("Enter your message here..."):
    # Store and display user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Check if knowledge base exists and retrieve relevant context
    if st.session_state.knowledge_base:
        retrieved_context = generate_response_with_knowledge_base(
            prompt, None, model_choice, sub_model_choice, st.session_state.knowledge_base
        )
    else:
        retrieved_context = ""

    # Generate response using the selected model
    if model_choice == "OpenAI":
        stream = OpenAI(api_key=openai_api_key).chat.completions.create(
            model=sub_model_choice,
            messages=[{"role": "system", "content": retrieved_context}] + [
                {"role": m["role"], "content": m["content"]} for m in st.session_state.messages
            ],
            stream=True,
        )
    elif model_choice == "DeepSeek":
        stream = DeepSeekClient(api_key=openai_api_key).generate_response(
            model=sub_model_choice,
            messages=[{"role": "system", "content": retrieved_context}] + [
                {"role": m["role"], "content": m["content"]} for m in st.session_state.messages
            ],
            stream=True,
        )

    
    # Display response
    with st.chat_message("assistant"):
        response = st.write_stream(stream)
    st.session_state.messages.append({"role": "assistant", "content": response})

# Prompt for API key if missing
if not openai_api_key:
    st.info("Please enter your API key to continue.", icon="🗝️")
