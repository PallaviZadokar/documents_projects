import os
import hashlib
import streamlit as st
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain_ollama import OllamaLLM
from collections import defaultdict
import uuid

# Function to compute hash of the uploaded file
def compute_file_hash(file_path):
    hasher = hashlib.md5()
    with open(file_path, "rb") as f:
        hasher.update(f.read())
    return hasher.hexdigest()

# Function to initialize or load the FAISS index
def load_or_create_faiss_index(temp_file_path):
    file_hash = compute_file_hash(temp_file_path)
    faiss_index_path = os.path.join(FAISS_DIR, f"{file_hash}.faiss")

    if os.path.exists(faiss_index_path):
        # Load existing FAISS index with deserialization enabled
        vectorstore = FAISS.load_local(
            faiss_index_path,
            HuggingFaceEmbeddings(),
            allow_dangerous_deserialization=True
        )
    else:
        # Load the PDF file using PyPDFLoader
        loader = PyPDFLoader(temp_file_path)
        pdf_documents = loader.load()

        # Ensure the document contains text
        documents = [doc for doc in pdf_documents if isinstance(doc.page_content, str) and doc.page_content.strip()]
        if not documents:
            st.error("No valid text found in the uploaded PDF.")
            st.stop()

        # Split the document into chunks
        text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=50, separator="\n")
        docs = text_splitter.split_documents(documents)

        # Set up embeddings using HuggingFace on CPU
        embedding_model_name = "sentence-transformers/all-mpnet-base-v2"
        model_kwargs = {"device": "cpu"}  # Use CPU instead of GPU
        embeddings = HuggingFaceEmbeddings(
            model_name=embedding_model_name,
            model_kwargs=model_kwargs
        )

        # Create and save a FAISS vector store
        vectorstore = FAISS.from_documents(docs, embeddings)
        vectorstore.save_local(faiss_index_path)
    return vectorstore

# Set up directory for storing FAISS indexes
FAISS_DIR = "faiss_store"
os.makedirs(FAISS_DIR, exist_ok=True)

# Initialize session state for user conversations
if "conversations" not in st.session_state:
    st.session_state["conversations"] = {}

# Initialize session state for vectorstore
if "vectorstore" not in st.session_state:
    st.session_state["vectorstore"] = None

# Function to clear conversation
def clear_conversation():
    st.session_state["conversations"] = {}
    st.session_state["vectorstore"] = None

# Streamlit Chatbot UI
st.title("Chatbot for Q&A")
st.write("Upload a PDF file and ask questions.")

# File uploader widget for a single PDF file
uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

# Handle file upload and create FAISS index if needed
if uploaded_file:
    try:
        # Save uploaded file temporarily
        temp_file_path = "uploaded_file.pdf"
        with open(temp_file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        # Load or create FAISS index
        st.session_state["vectorstore"] = load_or_create_faiss_index(temp_file_path)
        
        # Set up LLM and RetrievalQA
        llm = OllamaLLM(model="llama3.2:3b", timeout=30, device="cpu")  # Explicitly set to CPU
        retriever = st.session_state["vectorstore"].as_retriever()
        qa = RetrievalQA.from_chain_type(llm=llm, chain_type="stuff", retriever=retriever)

        # Initialize user session if it doesn't exist
        if "user_id" not in st.session_state:
            st.session_state["user_id"] = str(uuid.uuid4())  # Unique user session ID

        user_id = st.session_state["user_id"]

        # Display previous conversation if it exists
        if user_id in st.session_state["conversations"]:
            for message in st.session_state["conversations"][user_id]:
                if message["role"] == "user":
                    st.chat_message("user").markdown(message["content"])
                else:
                    st.chat_message("assistant").markdown(message["content"])

        # Input box for user query with unique key
        query_key = f"query_{len(st.session_state['conversations'].get(user_id, []))}"
        query = st.text_input("Type your query:", key=query_key)

        if query:
            # Add user query to conversation history
            if user_id not in st.session_state["conversations"]:
                st.session_state["conversations"][user_id] = []

            st.session_state["conversations"][user_id].append({"role": "user", "content": query})

            # Prepare the context for the LLM (combining previous conversation history)
            conversation_context = "\n".join([msg["content"] for msg in st.session_state["conversations"][user_id]])

            # Run query through the QA system with the accumulated conversation context
            result = qa.run(query + "\nContext: " + conversation_context)

            # Add chatbot response to conversation history
            st.session_state["conversations"][user_id].append({"role": "assistant", "content": result})

            # Display the answer
            st.write("Answer:", result)

            # Provide new input box for next query (this is part of the default Streamlit interaction)
            query_key = f"query_{len(st.session_state['conversations'].get(user_id, []))}"
            st.text_input("Type your query:", key=query_key)

        else:
            st.write("No query entered.")

        # Option to clear conversation and start fresh
        if st.button("Start a New Conversation"):
            clear_conversation()
            st.experimental_rerun()

    except Exception as e:
        st.error(f"An error occurred: {e}")
    finally:
        # Clean up temporary file
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
else:
    st.warning("Please upload a PDF file to start.")
