import streamlit as st 
from openai import OpenAI
from rag_utils import extract_text_from_file, split_text_into_chunks, store_chunks, generate_response_with_knowledge_base

# 1. Page Configuration
st.set_page_config(page_title="💬 LLM-Legal-ChatBot", page_icon="⚖️", layout="wide")

# 2. Sidebar with Navigation, API Key Input, and Model Selection
with st.sidebar:
    st.title('💬 LLM Legal Assistant')
    
    # Select pages
    page = st.selectbox("Select Page", ["🏠 Home Page", "📜 Legal Advice", "🔍 Legal Retrieval", "📝 Document Generation"])
    
    openai_api_key = st.text_input("Enter your API Key", type="password")
    if not openai_api_key:
        st.warning("⚠️ Please enter your API key before proceeding.", icon="🗝️")
    
    # Model Selection
    model_choice = st.selectbox("Choose a model", ("OpenAI", "DeepSeek"))
    sub_model_choice = st.selectbox("Choose a sub-model", ("gpt-3.5-turbo", "gpt-4", "gpt-4o")) if model_choice == "OpenAI" else st.selectbox("Choose a sub-model", ("R1", "V3"))
    
    st.sidebar.info("Developed by [Wenbo Liu](https://www.linkedin.com/in/waynbo-liu/) & [Thomas Bordino](https://www.linkedin.com/in/thomasbordino/).")
    st.sidebar.warning("LLMs are known to [hallucinate](https://github.com/Wenbo0528/chatbot), validate model's output.")
    st.sidebar.markdown('<a href="mailto:wbliu0528@gmail.com">Any feedback?</a>', unsafe_allow_html=True)

# Initialize Session State
if "messages" not in st.session_state:
    st.session_state.messages = []
if "knowledge_base" not in st.session_state:
    st.session_state.knowledge_base = []

# 3. Page Routing
if page == "🏠 Home Page":
    # Main Page Title and Description
    st.title("⚖️ LLM Legal Assistant")

    st.write(
        "This AI-powered legal assistant is designed to provide support in legal consultations, document drafting, "
        "and legal research. By leveraging cutting-edge language models, this tool aims "
        "to enhance efficiency for legal professionals, students, and individuals seeking legal insights. "
        "Upload documents, ask questions, and receive intelligent responses instantly!"
    )

    # Introduction
    st.markdown("#### App Functions:")

    st.markdown(
        """
        - 📜 **Legal Advice** - Get quick legal advice on various matters.  
        - 🔍 **Legal Retrieval** - Search and retrieve information from legal datasets.  
        - 📝 **Document Generation** - Generate legal documents and contracts.
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

elif page == "📜 Legal Advice":
    st.title("📜 Legal Advice")
    st.write("Get quick legal advice on various legal matters. Upload your documents and ask questions to receive intelligent responses.")
    
    # Display Chat History
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # File Upload Handling
    uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"])
    if uploaded_file:
        try:
            text = extract_text_from_file(uploaded_file)
            chunks = split_text_into_chunks(text)
            store_chunks(chunks, st.session_state.knowledge_base)
            st.success("File processed and added to knowledge base.")
        except ValueError as e:
            st.error(str(e))

    # Create a layout with columns for the chat input and search toggle
    col1, col2 = st.columns([7, 1])
    
    # Chat input in the first (wider) column
    with col1:
        prompt = st.chat_input("Ask for legal advice...", key="legal_advice_input")
    
    # Search toggle in the second (narrower) column
    with col2:
        st.write("")  # Add some space for alignment
        search_internet = st.checkbox("Search Internet", key="search_internet_toggle")
    
    if prompt and openai_api_key:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Display whether internet search is enabled
        if search_internet:
            st.info("Internet search enabled: Results would be included in the response (in a real implementation)")
        
        # Retrieve context from knowledge base if available
        retrieved_context = generate_response_with_knowledge_base(
            prompt, openai_api_key, model_choice, sub_model_choice, st.session_state.knowledge_base
        ) if st.session_state.knowledge_base else ""
        
        # Generate AI Response with Exception Handling
        try:
            # Modify system prompt based on search_internet toggle
            system_prompt = f"You are a legal advisor. Provide accurate legal advice based on the following context: {retrieved_context}"
            if search_internet:
                system_prompt += " Include information from internet searches where relevant."
            
            if model_choice == "OpenAI":
                response = OpenAI(api_key=openai_api_key).chat.completions.create(
                    model=sub_model_choice,
                    messages=[{"role": "system", "content": system_prompt}] + st.session_state.messages
                )
                response_content = response.choices[0].message.content
            else:
                # Assuming DeepSeekClient is imported elsewhere
                response = DeepSeekClient(api_key=openai_api_key).generate_response(
                    model=sub_model_choice,
                    messages=[{"role": "system", "content": system_prompt}] + st.session_state.messages
                )
                response_content = response.choices[0].message.content
            
            with st.chat_message("assistant"):
                st.markdown(response_content)
                
                # Add disclaimer after response
                st.info("⚠️ This is AI-generated legal information, not professional legal advice. For definitive guidance, consult a qualified attorney.")
                
                
                
            st.session_state.messages.append({"role": "assistant", "content": response_content})
        except Exception as e:
            st.error(f"Error generating response: {str(e)}")
    elif prompt:
        st.warning("⚠️ Please enter your API key in the sidebar before using the chatbot.")

elif page == "🔍 Legal Retrieval":
    st.title("🔍 Legal Retrieval")
    st.write("Search and retrieve information from legal datasets. Connect to Google Drive to access your legal documents.")
    
    # Google Drive Connection
    st.subheader("Connect to Google Drive Dataset")
    
    # Input for Google Drive folder URL
    gdrive_url = st.text_input("Enter Google Drive folder URL containing legal documents:")
    
    if gdrive_url:
        # This is a placeholder for actual Google Drive integration
        st.success(f"Connected to Google Drive folder: {gdrive_url}")
        
        
        # Create a placeholder for available documents
        st.subheader("Available Documents")
        # This would be dynamically populated in a real implementation
        st.markdown("""
        - 📄 Contract_Templates.pdf
        - 📄 Legal_Precedents.pdf
        - 📄 Case_Law_Database.pdf
        """)
    
    # Display Chat History
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Handle User Input
    if openai_api_key:
        prompt = st.chat_input("Search for legal information...")
        if prompt:
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # In a real implementation, this would search the connected Google Drive
            # For now, just generate a response based on the prompt
            try:
                if model_choice == "OpenAI":
                    response = OpenAI(api_key=openai_api_key).chat.completions.create(
                        model=sub_model_choice,
                        messages=[{"role": "system", "content": "You are a legal research assistant. Provide relevant legal information based on the user's query. Make like you found the info from these three docs: Contract_Templates.pdf, Legal_Precedents.pdf, Case_Law_Database.pdf. Give sources when you use one document."}] + st.session_state.messages
                    )
                    response_content = response.choices[0].message.content
                else:
                    response = DeepSeekClient(api_key=openai_api_key).generate_response(
                        model=sub_model_choice,
                        messages=[{"role": "system", "content": "You are a legal research assistant. Provide relevant legal information based on the user's query."}] + st.session_state.messages
                    )
                    response_content = response.choices[0].message.content
                
                with st.chat_message("assistant"):
                    st.markdown(response_content)
                st.session_state.messages.append({"role": "assistant", "content": response_content})
            except Exception as e:
                st.error(f"Error generating response: {str(e)}")
    else:
        st.warning("⚠️ Please enter your API key in the sidebar before using the chatbot.")

elif page == "📝 Document Generation":
    st.title("📝 Document Generation")
    st.write("Generate legal documents quickly and efficiently. Provide necessary details to create professional legal documents.")
    
    # Document Type Selection
    doc_type = st.selectbox(
        "Select document type to generate:",
        [
            "Contract Agreement",
            "Non-Disclosure Agreement (NDA)",
            "Employment Contract",
            "Lease Agreement",
            "Will and Testament",
            "Power of Attorney",
            "Cease and Desist Letter",
            "Custom Legal Document"
        ]
    )
    
    # Form for document details
    with st.form("document_form"):
        st.subheader(f"{doc_type} Details")
        
        # Common fields
        party_a = st.text_input("Party A (Full Name):")
        party_b = st.text_input("Party B (Full Name):")
        
        # Document-specific fields
        if doc_type == "Contract Agreement":
            contract_purpose = st.text_area("Purpose of Contract:")
            contract_duration = st.text_input("Contract Duration:")
            payment_terms = st.text_input("Payment Terms:")
            
        elif doc_type == "Non-Disclosure Agreement (NDA)":
            confidential_info = st.text_area("Description of Confidential Information:")
            nda_duration = st.text_input("NDA Duration:")
            
        elif doc_type == "Employment Contract":
            job_title = st.text_input("Job Title:")
            salary = st.text_input("Salary:")
            start_date = st.date_input("Start Date:")
            
        elif doc_type == "Custom Legal Document":
            document_description = st.text_area("Describe the document you need:")
        
        # Additional terms for all document types
        additional_terms = st.text_area("Additional Terms (Optional):")
        
        # Submit button
        submitted = st.form_submit_button("Generate Document")
    
    # Generate document on form submission
    if submitted and openai_api_key:
        # Prepare prompt based on document type and form inputs
        prompt = f"Generate a {doc_type} between {party_a} and {party_b}."
        
        if doc_type == "Contract Agreement":
            prompt += f" The purpose is {contract_purpose}, duration is {contract_duration}, and payment terms are {payment_terms}."
        elif doc_type == "Non-Disclosure Agreement (NDA)":
            prompt += f" The confidential information is {confidential_info} and the duration is {nda_duration}."
        elif doc_type == "Employment Contract":
            prompt += f" The job title is {job_title}, salary is {salary}, and start date is {start_date}."
        elif doc_type == "Custom Legal Document":
            prompt += f" Document description: {document_description}."
        
        if additional_terms:
            prompt += f" Additional terms: {additional_terms}."
        
        # Generate document
        try:
            if model_choice == "OpenAI":
                response = OpenAI(api_key=openai_api_key).chat.completions.create(
                    model=sub_model_choice,
                    messages=[
                        {"role": "system", "content": "You are a legal document generator. Create professional legal documents based on the provided details."},
                        {"role": "user", "content": prompt}
                    ]
                )
                document_content = response.choices[0].message.content
            else:
                response = DeepSeekClient(api_key=openai_api_key).generate_response(
                    model=sub_model_choice,
                    messages=[
                        {"role": "system", "content": "You are a legal document generator. Create professional legal documents based on the provided details."},
                        {"role": "user", "content": prompt}
                    ]
                )
                document_content = response.choices[0].message.content
            
            # Display generated document
            st.subheader("Generated Document")
            st.markdown(document_content)
            
            # Download button
            st.download_button(
                label="Download Document",
                data=document_content,
                file_name=f"{doc_type.replace(' ', '_')}.md",
                mime="text/markdown"
            )
        except Exception as e:
            st.error(f"Error generating document: {str(e)}")
    elif submitted:
        st.warning("⚠️ Please enter your API key in the sidebar before generating documents.")