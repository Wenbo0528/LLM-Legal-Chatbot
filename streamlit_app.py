import streamlit as st
from openai import OpenAI
from rag_utils import extract_text_from_file, split_text_into_chunks, store_chunks, generate_response_with_knowledge_base

# 1. Page Configuration
st.set_page_config(page_title="💬 LLM-Legal-ChatBot", page_icon="⚖️", layout="wide")

# 2. Sidebar with Navigation and API Key Input
with st.sidebar:
    st.title('💬 LLM Legal Assistant')
    
    # Select pages
    page = st.selectbox("Select Page", ["🏠Home Page", "📜 Legal Consultation", "📝 Document Drafting", "🔍 Case & Law Search", "⚖️ Legal Process Guidance"])
    
    openai_api_key = st.text_input("Enter your API Key", type="password")
    if not openai_api_key:
        st.warning("⚠️ Please enter your API key before proceeding.", icon="🗝️")

    st.sidebar.info("Developed by [Wenbo Liu](https://www.linkedin.com/in/waynbo-liu/).")
    st.sidebar.warning("LLMs are known to [hallucinate](https://github.com/Wenbo0528/chatbot), validate model's output.")
    st.sidebar.markdown('<a href="mailto:wbliu0528@gmail.com">Any feedback?</a>', unsafe_allow_html=True)

# 3. Page Routing
if page == "🏠Home Page":
    # Main Page Title and Description
    st.title("⚖️ LLM Legal Assistant")

    st.write(
        "This AI-powered legal assistant is designed to provide support in legal consultations, document drafting, "
        "case and law research, and legal process guidance. By leveraging cutting-edge language models, this tool aims "
        "to enhance efficiency for legal professionals, students, and individuals seeking legal insights. "
        "Upload documents, ask questions, and receive intelligent responses instantly!"
    )


    st.info(
        "Watch app [demo](https://www.youtube.com/watch?v=sGUjmyfof4Q)."
    )

    # Introduction
    st.markdown("#### App Functions:")

    st.markdown("📜 **Legal Consultation** - Get quick legal advice.  ")
    st.markdown("📝 **Document Drafting** - Generate legal documents.  ")
    st.markdown("🔍 **Case & Law Search** - Find relevant legal cases.  ")
    st.markdown("⚖️ **Legal Process Guidance** - Understand legal procedures.")
    


    # Model Selection
    model_choice = st.selectbox("Choose a model", ("OpenAI", "DeepSeek"))
    sub_model_choice = st.selectbox("Choose a sub-model", ("gpt-3.5-turbo", "gpt-4", "gpt-4o")) if model_choice == "OpenAI" else st.selectbox("Choose a sub-model", ("R1", "V3"))
    
    # Initialize Session State
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "knowledge_base" not in st.session_state:
        st.session_state.knowledge_base = []

    # Display Chat History
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # File Upload Handling
    uploaded_file = st.file_uploader("Upload a file", type=["csv", "pdf", "txt", "docx"])
    if uploaded_file:
        text = extract_text_from_file(uploaded_file)
        chunks = split_text_into_chunks(text)
        store_chunks(chunks, st.session_state.knowledge_base)
        st.success("File processed and added to knowledge base.")

    # Handle User Input
    if openai_api_key:
        prompt = st.chat_input("Enter your message here...")
        if prompt:
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # Retrieve context from knowledge base if available
            retrieved_context = generate_response_with_knowledge_base(
                prompt, None, model_choice, sub_model_choice, st.session_state.knowledge_base
            ) if st.session_state.knowledge_base else ""
            
            # Generate AI Response with Exception Handling
            try:
                if model_choice == "OpenAI":
                    stream = OpenAI(api_key=openai_api_key).chat.completions.create(
                        model=sub_model_choice,
                        messages=[{"role": "system", "content": retrieved_context}] + st.session_state.messages,
                        stream=True,
                    )
                else:
                    stream = DeepSeekClient(api_key=openai_api_key).generate_response(
                        model=sub_model_choice,
                        messages=[{"role": "system", "content": retrieved_context}] + st.session_state.messages,
                        stream=True,
                    )
                
                with st.chat_message("assistant"):
                    response = st.write_stream(stream)
                st.session_state.messages.append({"role": "assistant", "content": response})
            except Exception as e:
                st.error(f"Error generating response: {str(e)}")
    else:
        st.warning("⚠️ Please enter your API key in the sidebar before using the chatbot.")

else:
    # Blank Pages for Navigation
    st.title(f"{page}")
    st.write("This is a blank page.")
