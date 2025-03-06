import streamlit as st 
from openai import OpenAI
from rag_utils import extract_text_from_file, split_text_into_chunks, store_chunks, generate_response_with_knowledge_base

# 1. Page Configuration
st.set_page_config(page_title="💬 LLM-Legal-ChatBot", page_icon="⚖️", layout="wide")

# 2. Sidebar with Navigation, API Key Input, and Model Selection
with st.sidebar:
    st.title('💬 LLM Legal Assistant')
    
    # Select pages
    page = st.selectbox("Select Page", ["🏠Home Page", "📜 Legal Consultation", "📝 Document Drafting", "🔍 Case & Law Search", "⚖️ Legal Process Guidance"])
    
    openai_api_key = st.text_input("Enter your API Key", type="password")
    if not openai_api_key:
        st.warning("⚠️ Please enter your API key before proceeding.", icon="🗝️")
    
    # Model Selection
    model_choice = st.selectbox("Choose a model", ("OpenAI", "DeepSeek"))
    sub_model_choice = st.selectbox("Choose a sub-model", ("gpt-3.5-turbo", "gpt-4", "gpt-4o")) if model_choice == "OpenAI" else st.selectbox("Choose a sub-model", ("R1", "V3"))
    
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

    # Introduction
    st.markdown("#### App Functions:")

    st.markdown(
        """
        - 📜 **Legal Consultation** - Get quick legal advice.  
        - 📝 **Document Drafting** - Generate legal documents.  
        - 🔍 **Case & Law Search** - Find relevant legal cases.  
        - ⚖️ **Legal Process Guidance** - Understand legal procedures.
        """
    )

    st.info(
        "📺 **Watch the app demo**: Learn how to use this legal assistant effectively. "
        "[Click here](https://www.youtube.com/watch?v=sGUjmyfof4Q) to watch."
    )

    st.info(
        """
        **🔑 API Key Required (You need an API key to use this app.)**
        
        - **Get API Key Required – OpenAI or Deepseek provides API Key.**
        - **Billing Setup Required  – Once the free credit runs out, charges apply. Set up billing to avoid authentication errors.**
        - **Monitor Your Usage  – Keep track of your account to prevent unexpected charges.**
        """
    )

    st.image("UIphoto.jpg", caption='Legal Assistant', use_container_width=True)


else:
    st.title(f"{page}")
    
    if page == "📜 Legal Consultation":
        st.write("Get quick legal advice on various legal matters. Upload your documents and ask questions to receive intelligent responses.")
    elif page == "📝 Document Drafting":
        st.write("Generate legal documents quickly and efficiently. Upload your documents and provide necessary details to draft legal documents.")
    elif page == "🔍 Case & Law Search":
        st.write("Find relevant legal cases and laws. Upload your documents and search for specific cases or laws to get detailed information.")
    elif page == "⚖️ Legal Process Guidance":
        st.write("Understand legal procedures and processes. Upload your documents and ask questions to get guidance on legal processes.")

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
    uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"])  # 修改提示信息
    if uploaded_file:
        try:
            text = extract_text_from_file(uploaded_file)
            chunks = split_text_into_chunks(text)
            store_chunks(chunks, st.session_state.knowledge_base)
            st.success("File processed and added to knowledge base.")
        except ValueError as e:
            st.error(str(e))

    # Handle User Input
    if openai_api_key:
        prompt = st.chat_input("Enter your message here...")
        if prompt:
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # Retrieve context from knowledge base if available
            retrieved_context = generate_response_with_knowledge_base(
                prompt, openai_api_key, model_choice, sub_model_choice, st.session_state.knowledge_base
            ) if st.session_state.knowledge_base else ""
            
            # Generate AI Response with Exception Handling
            try:
                if model_choice == "OpenAI":
                    response = OpenAI(api_key=openai_api_key).chat.completions.create(
                        model=sub_model_choice,
                        messages=[{"role": "system", "content": retrieved_context}] + st.session_state.messages
                    )
                    response_content = response.choices[0].message.content
                else:
                    response = DeepSeekClient(api_key=openai_api_key).generate_response(
                        model=sub_model_choice,
                        messages=[{"role": "system", "content": retrieved_context}] + st.session_state.messages
                    )
                    response_content = response.choices[0].message.content
                
                with st.chat_message("assistant"):
                    st.markdown(response_content)
                st.session_state.messages.append({"role": "assistant", "content": response_content})
            except Exception as e:
                st.error(f"Error generating response: {str(e)}")
    else:
        st.warning("⚠️ Please enter your API key in the sidebar before using the chatbot.")
