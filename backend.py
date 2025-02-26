import os
import shutil
import hashlib
import json
from langchain.chains import RetrievalQA
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
#from langchain.llms import Ollama
#from langchain.embeddings.ollama import OllamaEmbeddings
#from langchain.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
#from langchain.document_loaders import PyPDFLoader
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
import streamlit as st

#from langchain_community.llms import Ollama
#from langchain_community.embeddings import OllamaEmbeddings
#from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import PyPDFLoader

from langchain_ollama import OllamaLLM
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma



# Create directories
os.makedirs('files', exist_ok=True)
os.makedirs('data', exist_ok=True)

# Initialize session states
def initialize_chatbot():
    if 'template' not in st.session_state:
        st.session_state.template = """You are a knowledgeable chatbot, here to help with questions of the user. 
        Your tone should be professional and informative. 
        You will give response within 5 sentences. 
        You will always give response in bullet points.

        Context: {context}
        History: {history}

        User: {question}
        Chatbot:"""

    if 'prompt' not in st.session_state:
        st.session_state.prompt = PromptTemplate(
            input_variables=["history", "context", "question"],
            template=st.session_state.template,
        )

    if 'memory' not in st.session_state:
        st.session_state.memory = ConversationBufferMemory(
            memory_key="history",
            return_messages=True,
            input_key="question"
        )

    if 'vectorstore' not in st.session_state:
        st.session_state.vectorstore = None

    if 'llm' not in st.session_state:
        st.session_state.llm = OllamaLLM(
            base_url="http://localhost:11434",
            model="llama2:7b",
            verbose=True,
            callback_manager=CallbackManager([StreamingStdOutCallbackHandler()])
        )

    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []

    check_and_update_vectorstore()

# Hash function to track file changes
def get_file_hash(filepath):
    hasher = hashlib.md5()
    with open(filepath, 'rb') as file:
        hasher.update(file.read())
    return hasher.hexdigest()

# Function to load PDFs and process them
def load_and_analyze_pdfs(directory="files", hash_file="file_hashes.json"):
    documents = []
    if os.path.exists(hash_file):
        with open(hash_file, 'r') as f:
            processed_hashes = json.load(f)
    else:
        processed_hashes = {}

    new_files = False
    for file in os.listdir(directory):
        if file.endswith(".pdf"):
            pdf_path = os.path.join(directory, file)
            current_hash = get_file_hash(pdf_path)
            if file not in processed_hashes or processed_hashes[file] != current_hash:
                new_files = True
                loader = PyPDFLoader(pdf_path)
                pdf_data = loader.load()
                documents.extend(pdf_data)
                processed_hashes[file] = current_hash

    with open(hash_file, 'w') as f:
        json.dump(processed_hashes, f)
    
    return documents, new_files

# Function to manage vectorstore
def load_or_create_vectorstore(documents):
    if os.path.exists("data"):
        try:
            vectorstore = Chroma(
                persist_directory="data",
                embedding_function=OllamaEmbeddings(model="llama2:7b")
            )
            return vectorstore
        except Exception as e:
            clear_chroma_store()

    if documents:
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1500,
            chunk_overlap=200,
            length_function=len
        )
        all_splits = text_splitter.split_documents(documents)

        try:
            vectorstore = Chroma.from_documents(
                documents=all_splits,
                embedding=OllamaEmbeddings(model="llama2"),
                persist_directory="data"
            )
            vectorstore.persist()
            return vectorstore
        except Exception as e:
            if "InvalidDimensionException" in str(e):
                clear_chroma_store()
                st.error(f"Dimension mismatch detected: {str(e)}. Vectorstore cleared. Please try reloading.")
            else:
                raise e
    else:
        st.error("No documents available to create vectorstore.")

    return None

# Function to clear Chroma vectorstore
def clear_chroma_store(directory="data"):
    if os.path.exists(directory):
        shutil.rmtree(directory)
        os.mkdir(directory)

# Function to check and update vectorstore
def check_and_update_vectorstore():
    documents, new_files = load_and_analyze_pdfs()
    
    if new_files or st.session_state.vectorstore is None:
        st.session_state.vectorstore = load_or_create_vectorstore(documents)
        return True
    elif not new_files and st.session_state.vectorstore is not None:
        return False

    if not documents and not st.session_state.vectorstore:
        st.error("No PDFs found. Please upload some PDFs.")
    return False

# Function to process uploaded files
def process_uploaded_files(uploaded_files):
    for uploaded_file in uploaded_files:
        file_path = os.path.join("files", uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
    check_and_update_vectorstore()

# Function to get chatbot response
def get_response(user_input):
    if st.session_state.vectorstore is not None:
        st.session_state.retriever = st.session_state.vectorstore.as_retriever()

        if 'qa_chain' not in st.session_state:
            st.session_state.qa_chain = RetrievalQA.from_chain_type(
                llm=st.session_state.llm,
                chain_type='stuff',
                retriever=st.session_state.retriever,
                verbose=True,
                chain_type_kwargs={
                    "verbose": True,
                    "prompt": st.session_state.prompt,
                    "memory": st.session_state.memory,
                }
            )

        try:
            response = st.session_state.qa_chain.invoke(user_input)
            if response is None:
                return "Sorry, I couldn't generate a response."
        except Exception as e:
            return f"Error: {str(e)}"  # Ensure a fallback response

        
        #st.markdown(response, unsafe_allow_html=True)
        #st.write("")
        return response  # Return response properly


        #response = st.session_state.qa_chain(user_input)
        #return response['result']
    else:
        return "Please upload PDFs to start the chat."