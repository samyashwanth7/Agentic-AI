# Patch missing xml.dom.NodeFilter in some Windows Python 3.12 environments
import sys
if "xml.dom.NodeFilter" not in sys.modules:
    from types import ModuleType
    m = ModuleType("xml.dom.NodeFilter")
    m.NodeFilter = type("NodeFilter", (), {
        "FILTER_ACCEPT": 1,
        "FILTER_REJECT": 2,
        "FILTER_SKIP": 3,
        "SHOW_ALL": 0xFFFFFFFF,
        "SHOW_ELEMENT": 0x00000001,
        "SHOW_ATTRIBUTE": 0x00000002,
        "SHOW_TEXT": 0x00000004,
        "SHOW_CDATA_SECTION": 0x00000008,
        "SHOW_ENTITY_REFERENCE": 0x00000010,
        "SHOW_ENTITY": 0x00000020,
        "SHOW_PROCESSING_INSTRUCTION": 0x00000040,
        "SHOW_COMMENT": 0x00000080,
        "SHOW_DOCUMENT": 0x00000100,
        "SHOW_DOCUMENT_TYPE": 0x00000200,
        "SHOW_DOCUMENT_FRAGMENT": 0x00000400,
        "SHOW_NOTATION": 0x00000800,
    })
    sys.modules["xml.dom.NodeFilter"] = m

from dotenv import load_dotenv
import os
import streamlit as st

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()

st.set_page_config(page_title="RAG Chatbot", page_icon="📚")
st.title("📚 Chat with The Courage To Be Disliked")


@st.cache_resource
def build_vectorstore():
    from pathlib import Path

    BASE_DIR = Path(__file__).parent
    PDF_PATH = BASE_DIR / "The-Courage-To-Be-Disliked.pdf"

    st.write("Looking for PDF at:", PDF_PATH)

    if not PDF_PATH.exists():
        st.error(f"PDF not found: {PDF_PATH}")
        st.stop()

    loader = PyPDFLoader(str(PDF_PATH))
    documents = loader.load()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    chunks = splitter.split_documents(documents)

    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    vectorstore = FAISS.from_documents(chunks, embeddings)
    return vectorstore


@st.cache_resource
def load_llm():
    return ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=0.3,
        api_key=os.getenv("GROQ_API_KEY")
    )


vectorstore = build_vectorstore()
retriever = vectorstore.as_retriever(search_kwargs={"k": 4})
llm = load_llm()

prompt = ChatPromptTemplate.from_template(
    """You are a helpful assistant answering questions about the book "The Courage To Be Disliked".

Use the context below to answer the question.
If the answer is not in the context, say you could not find it in the book context provided.

Context:
{context}

Question:
{question}
"""
)

if "messages" not in st.session_state:
    st.session_state.messages = []

if st.button("🗑️ Clear Chat"):
    st.session_state.messages = []
    st.rerun()

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

if user_input := st.chat_input("Ask anything about the book..."):
    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("user"):
        st.write(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Searching the book..."):
            docs = retriever.invoke(user_input)
            context = "\n\n".join([doc.page_content for doc in docs])

            messages = prompt.format_messages(
                context=context,
                question=user_input
            )

            response = llm.invoke(messages)
            reply = response.content

        st.write(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})