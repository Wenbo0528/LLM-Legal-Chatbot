import streamlit as st
from openai import OpenAI
<<<<<<< HEAD
from rag_utils import extract_text_from_file, split_text_into_chunks, store_chunks, generate_response_with_knowledge_base

# Show title and description.
st.title("💬 Chatbot with RAG")
=======

# Show title and description.
st.title("💬 Chatbot")
>>>>>>> 222df72d3149820518644cb55a3b379f74c93c77
st.write(
    "This is a simple chatbot that uses OpenAI's GPT-3.5 model to generate responses. "
    "To use this app, you need to provide an OpenAI API key, which you can get [here](https://platform.openai.com/account/api-keys). "
    "You can also learn how to build this app step by step by [following our tutorial](https://docs.streamlit.io/develop/tutorials/llms/build-conversational-apps)."
)

# Ask user for their OpenAI API key via `st.text_input`.
# Alternatively, you can store the API key in `./.streamlit/secrets.toml` and access it
# via `st.secrets`, see https://docs.streamlit.io/develop/concepts/connections/secrets-management
openai_api_key = st.text_input("OpenAI API Key", type="password")
<<<<<<< HEAD

# Add a model selection option
model_choice = st.selectbox("Choose a model", ("OpenAI", "DeepSeek"))

# Add sub-model selection based on the main model choice
if model_choice == "OpenAI":
    sub_model_choice = st.selectbox("Choose a sub-model", ("gpt-3.5-turbo", "gpt-4", "gpt-4o"))
elif model_choice == "DeepSeek":
    sub_model_choice = st.selectbox("Choose a sub-model", ("R1", "V3"))

# Check if the API key is provided
if not openai_api_key:
    st.info("Please add your OpenAI API key to continue.", icon="🗝️")
else:
    # Create a client based on the selected model
    if model_choice == "OpenAI":
        client = OpenAI(api_key=openai_api_key)
    elif model_choice == "DeepSeek":
        # Assuming DeepSeekClient is a placeholder for the actual DeepSeek client
        client = DeepSeekClient(api_key=openai_api_key)
=======
if not openai_api_key:
    st.info("Please add your OpenAI API key to continue.", icon="🗝️")
else:

    # Create an OpenAI client.
    client = OpenAI(api_key=openai_api_key)
>>>>>>> 222df72d3149820518644cb55a3b379f74c93c77

    # Create a session state variable to store the chat messages. This ensures that the
    # messages persist across reruns.
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display the existing chat messages via `st.chat_message`.
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Create a chat input field to allow the user to enter a message. This will display
    # automatically at the bottom of the page.
    if prompt := st.chat_input("What is up?"):

        # Store and display the current prompt.
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

<<<<<<< HEAD
        # Generate a response using the selected API and sub-model
        if model_choice == "OpenAI":
            stream = client.chat.completions.create(
                model=sub_model_choice,
                messages=[
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ],
                stream=True,
            )
        elif model_choice == "DeepSeek":
            # Assuming DeepSeek has a similar method for generating responses
            stream = client.generate_response(
                model=sub_model_choice,
                messages=[
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ],
                stream=True,
            )
=======
        # Generate a response using the OpenAI API.
        stream = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ],
            stream=True,
        )
>>>>>>> 222df72d3149820518644cb55a3b379f74c93c77

        # Stream the response to the chat using `st.write_stream`, then store it in 
        # session state.
        with st.chat_message("assistant"):
            response = st.write_stream(stream)
        st.session_state.messages.append({"role": "assistant", "content": response})
<<<<<<< HEAD

# Initialize session state for knowledge base
if 'knowledge_base' not in st.session_state:
    st.session_state.knowledge_base = []

# uploaded_file = st.file_uploader("Upload a file", type=["csv", "pdf", "txt", "docx"])

if st.session_state.knowledge_base:
    if prompt := st.chat_input("What is up?", key="chat_input_key"):
        response = generate_response_with_knowledge_base(prompt, client, model_choice, sub_model_choice, st.session_state.knowledge_base)
        st.write(response)
=======
>>>>>>> 222df72d3149820518644cb55a3b379f74c93c77
