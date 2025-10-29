import streamlit as st
import os
import tempfile
import shutil
from typing import List, Tuple

# --- 1. Import Dependencies ---
try:
    from openai import OpenAI
    from langchain_openai import ChatOpenAI, OpenAIEmbeddings
    from langchain_community.document_loaders import TextLoader, PyPDFLoader
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    from langchain_chroma import Chroma
    from langchain_core.prompts import PromptTemplate
    from langchain_core.documents import Document
except Exception as e:
    st.error(f"❌ Dependency import failed: {e}")
    st.error("Please ensure all required libraries are installed by running: pip install --upgrade streamlit openai langchain-openai langchain-community langchain-chroma pypdf")
    st.stop()

# --- 2. Page Config & Initialization ---
st.set_page_config(page_title="AI Document Assistant", page_icon="💡", layout="wide")

st.title("💡 AI Document Assistant")
st.markdown("Upload your documents, and the AI will answer questions based on their content.")

# Check for API key
api_key = os.environ.get("API_KEY", "")
if not api_key:
    st.error("❌ API_KEY environment variable not found! Please set it in your terminal: export API_KEY='your_key'")
    st.stop()

# Initialize clients
try:
    client = OpenAI(api_key=api_key, base_url="https://api.ai.it.cornell.edu")
    llm = ChatOpenAI(model="openai.gpt-4o", temperature=0.2, api_key=api_key, base_url="https://api.ai.it.cornell.edu")
except Exception as e:
    st.error(f"❌ OpenAI client initialization failed: {e}")
    st.stop()

# Initialize Session State
if "messages" not in st.session_state:
    st.session_state.messages = []
if "vectorstore" not in st.session_state:
    st.session_state.vectorstore = None
if "uploaded_files_names" not in st.session_state:
    st.session_state.uploaded_files_names = []
if "temp_dir" not in st.session_state:
    st.session_state.temp_dir = None
if "processing_summary" not in st.session_state:
    st.session_state.processing_summary = None
if "document_texts" not in st.session_state:
    st.session_state.document_texts = {}

# --- 3. Backend Core Functions ---

def load_and_extract_text(file_path: str, file_type: str, file_name: str) -> Tuple[List[Document], str]:
    """Loads a document and returns both LangChain Document objects and a plain text string."""
    full_text = ""
    docs = []
    try:
        if file_type == "txt":
            encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
            content = None
            for encoding in encodings:
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        content = f.read()
                    break
                except (UnicodeDecodeError, Exception):
                    continue
            if content is None:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
            full_text = content
            docs = [Document(page_content=content, metadata={"source": file_name})]
        
        elif file_type == "pdf":
            loader = PyPDFLoader(file_path)
            docs = loader.load()
            full_text = "\n\n".join([page.page_content for page in docs])

    except Exception as e:
        st.error(f"Error loading {file_name}: {e}")
    return docs, full_text

def process_documents(uploaded_files, chunk_size: int, chunk_overlap: int):
    """Processes uploaded documents and generates a summary."""
    if st.session_state.temp_dir is None or not os.path.exists(st.session_state.temp_dir):
        st.session_state.temp_dir = tempfile.mkdtemp()

    all_docs = []
    st.session_state.document_texts = {}  # Reset
    
    for uploaded_file in uploaded_files:
        temp_file_path = os.path.join(st.session_state.temp_dir, uploaded_file.name)
        with open(temp_file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        file_extension = uploaded_file.name.split('.')[-1].lower()
        docs, full_text = load_and_extract_text(temp_file_path, file_extension, uploaded_file.name)
        
        if docs:
            all_docs.extend(docs)
            st.session_state.document_texts[uploaded_file.name] = full_text

    if not all_docs:
        st.error("All files failed to load.")
        return
        
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    chunks = text_splitter.split_documents(all_docs)
    
    embeddings = OpenAIEmbeddings(model="openai.text-embedding-3-large", api_key=api_key, base_url="https://api.ai.it.cornell.edu")
    
    vectorstore = Chroma.from_documents(documents=chunks, embedding=embeddings)
    
    st.session_state.vectorstore = vectorstore
    st.session_state.uploaded_files_names = list(st.session_state.document_texts.keys())
    
    st.session_state.processing_summary = {
        "file_count": len(st.session_state.uploaded_files_names),
        "total_docs": len(all_docs),
        "total_chunks": len(chunks)
    }

def retrieve_and_generate(question: str) -> dict:
    """Retrieves context and generates an answer (stateless)."""
    if st.session_state.vectorstore is None:
        return {"answer": "Please process documents first.", "sources": []}

    retriever = st.session_state.vectorstore.as_retriever()
    retrieved_docs = retriever.invoke(question)

    context = "\n\n".join([doc.page_content for doc in retrieved_docs])
    sources = sorted(list(set([doc.metadata.get('source', 'Unknown') for doc in retrieved_docs])))

    template = """You are an assistant for question-answering tasks. 
    Use the following pieces of retrieved context to answer the question. 
    If you don't know the answer, just say that you don't know. 
    Keep the answer concise.

    Context:
    {context}

    Question: {question}

    Answer:"""
    prompt = PromptTemplate.from_template(template)

    chain = prompt | llm
    response = chain.invoke({"context": context, "question": question})

    return {"answer": response.content, "sources": sources}


# --- 4. User Interface (UI) ---

with st.sidebar:
    st.header("⚙️ Global Controls")
    if st.button("🗑️ Clear Chat History"):
        st.session_state.messages = []
        st.success("Chat history cleared!")
    if st.button("🔄 Reset System"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        if os.path.exists("temp_dir"): shutil.rmtree("temp_dir")
        st.success("System has been reset! Please refresh the page.")
        st.rerun()
    st.divider()
    if st.session_state.uploaded_files_names:
        st.subheader("✅ Loaded Documents")
        for filename in st.session_state.uploaded_files_names:
            st.info(f"📄 {filename}")

tab1, tab2, tab3 = st.tabs(["**① Configure & Upload**", "**② Chat with Documents**", "**③ Document Viewer**"])

with tab1:
    st.header("1. Configure Parameters")
    col1, col2 = st.columns(2)
    with col1:
        chunk_size = st.slider("Chunk Size", 200, 2000, 1000, 100, help="Max characters per knowledge chunk.")
    with col2:
        chunk_overlap = st.slider("Chunk Overlap", 0, 500, 200, 50, help="Overlapping characters between chunks.")
    
    st.divider()
    st.header("2. Upload Documents")
    uploaded_files = st.file_uploader("Choose TXT or PDF files", type=["txt", "pdf"], accept_multiple_files=True)

    if st.button("🚀 Process Documents", type="primary", disabled=not uploaded_files):
        with st.spinner("Processing documents, please wait..."):
            process_documents(uploaded_files, chunk_size, chunk_overlap)
    
    if st.session_state.processing_summary:
        summary = st.session_state.processing_summary
        st.success("Document processing complete!")
        st.markdown(f"""
        - **Files Processed:** `{summary['file_count']}`
        - **Total Pages/Docs:** `{summary['total_docs']}`
        - **Knowledge Chunks Created:** `{summary['total_chunks']}`
        """)
        st.info("You can now switch to the 'Chat with Documents' tab to ask questions.")

with tab2:
    if not st.session_state.vectorstore:
        st.info("👈 Please upload and process your documents in the 'Configure & Upload' tab first.")
    else:
        st.header("💬 Start Chatting!")
        
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])
                if "sources" in msg and msg["sources"]:
                     st.caption(f"📚 Sources: " + ", ".join(msg["sources"]))

        if prompt := st.chat_input("Ask your question here..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.write(prompt)

            with st.chat_message("assistant"):
                with st.spinner("🧠 AI is thinking..."):
                    result = retrieve_and_generate(prompt)
                    st.write(result["answer"])
                    if result["sources"]:
                        st.caption(f"📚 Sources: " + ", ".join(result["sources"]))
            
            st.session_state.messages.append({
                "role": "assistant", 
                "content": result["answer"], 
                "sources": result["sources"]
            })

with tab3:
    st.header("📄 Document Viewer")
    if not st.session_state.document_texts:
        st.info("👈 Please upload and process documents in the 'Configure & Upload' tab first.")
    else:
        selected_file = st.selectbox("Choose a file to preview:", options=st.session_state.uploaded_files_names)
        if selected_file:
            st.text_area(
                label=f"**Content of: {selected_file}**",
                value=st.session_state.document_texts[selected_file],
                height=500,
                disabled=True
            )