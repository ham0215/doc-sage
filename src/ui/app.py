"""Streamlit application for Doc Sage."""
import streamlit as st
import os
import uuid
from pathlib import Path
from datetime import datetime

# Import application modules
from ..config import Config
from ..database.init_db import get_session
from ..database import crud
from ..loaders.pdf_loader import PDFDocumentLoader
from ..processing.vectorstore import VectorStoreManager
from ..chains.qa_chain import QAChainManager

# Page configuration
st.set_page_config(
    page_title="Doc Sage - ɭ����n�",
    page_icon="=�",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .upload-section {
        background-color: #f0f2f6;
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
    }
    .user-message {
        background-color: #e3f2fd;
    }
    .assistant-message {
        background-color: #f5f5f5;
    }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize Streamlit session state."""
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())

    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "current_document_id" not in st.session_state:
        st.session_state.current_document_id = None

    if "vectorstore_manager" not in st.session_state:
        st.session_state.vectorstore_manager = None

    if "qa_manager" not in st.session_state:
        st.session_state.qa_manager = None


def save_uploaded_file(uploaded_file) -> str:
    """
    Save uploaded file to disk.

    Args:
        uploaded_file: Streamlit UploadedFile object

    Returns:
        Path to saved file
    """
    upload_dir = Path("/app/data/documents")
    upload_dir.mkdir(parents=True, exist_ok=True)

    file_path = upload_dir / uploaded_file.name
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    return str(file_path)


def process_document(file_path: str, filename: str, file_size: int) -> int:
    """
    Process uploaded document.

    Args:
        file_path: Path to the file
        filename: Name of the file
        file_size: Size of the file in bytes

    Returns:
        Document ID
    """
    db = get_session()

    try:
        # Create document record
        document = crud.create_document(
            db=db,
            filename=filename,
            file_path=file_path,
            file_type="pdf",
            file_size=file_size,
            status="processing"
        )

        # Load and split PDF
        with st.spinner("PDF����gD~Y..."):
            loader = PDFDocumentLoader()
            chunks = loader.load_and_split(file_path)
            st.success(f" {len(chunks)}n���krW~W_")

        # Create vector store
        with st.spinner("ٯ��Ȣ�\WfD~Y..."):
            vectorstore_manager = VectorStoreManager()
            vectorstore = vectorstore_manager.create_vectorstore(chunks)
            st.success(" ٯ��Ȣ�\W~W_")

        # Update document status
        crud.update_document_status(db, document.id, "completed")

        # Store in session state
        st.session_state.vectorstore_manager = vectorstore_manager
        st.session_state.current_document_id = document.id

        # Initialize QA manager
        st.session_state.qa_manager = QAChainManager(vectorstore)

        return document.id

    except Exception as e:
        st.error(f"���LzW~W_: {e}")
        if 'document' in locals():
            crud.update_document_status(db, document.id, "failed")
        raise
    finally:
        db.close()


def display_chat_interface():
    """Display chat interface."""
    st.markdown("### =� ����")

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if "sources" in message:
                with st.expander("=� �gC�h:"):
                    for i, source in enumerate(message["sources"], 1):
                        st.markdown(f"**{i}. ��� {source['metadata'].get('page', 'N/A')}**")
                        st.text(source["content"])
                        st.divider()

    # Chat input
    if prompt := st.chat_input("�O�e�WfO`UD..."):
        if not st.session_state.qa_manager:
            st.error("~ZPDFա�뒢�����WfO`UD")
            return

        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Get AI response
        with st.chat_message("assistant"):
            with st.spinner("�T�WfD~Y..."):
                try:
                    result = st.session_state.qa_manager.ask_with_sources(prompt)
                    answer = result["answer"]
                    sources = result.get("sources", [])

                    st.markdown(answer)

                    # Display sources
                    if sources:
                        with st.expander("=� �gC�h:"):
                            for i, source in enumerate(sources, 1):
                                st.markdown(f"**{i}. ��� {source['metadata'].get('page', 'N/A')}**")
                                st.text(source["content"])
                                st.divider()

                    # Add to messages
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": answer,
                        "sources": sources
                    })

                    # Save to database
                    db = get_session()
                    try:
                        crud.create_conversation(
                            db=db,
                            session_id=st.session_state.session_id,
                            user_message=prompt,
                            assistant_message=answer,
                            document_id=st.session_state.current_document_id
                        )
                    finally:
                        db.close()

                except Exception as e:
                    st.error(f"���LzW~W_: {e}")


def main():
    """Main application."""
    initialize_session_state()

    # Validate configuration
    try:
        Config.validate()
    except ValueError as e:
        st.error(f"-����: {e}")
        st.info("��	p `OPENAI_API_KEY` �-�WfO`UD")
        st.stop()

    # Header
    st.markdown('<div class="main-header">=� Doc Sage</div>', unsafe_allow_html=True)
    st.markdown("##### ɭ����n� - PDFɭ����k�OgM�AI�������")

    # Sidebar
    with st.sidebar:
        st.markdown("## =� ɭ���Ȣ�����")

        uploaded_file = st.file_uploader(
            "PDFա��x�",
            type=["pdf"],
            help="�OW_DPDFա�뒢�����WfO`UD"
        )

        if uploaded_file is not None:
            if st.button("=� ������Wf�", type="primary", use_container_width=True):
                try:
                    # Save file
                    file_path = save_uploaded_file(uploaded_file)

                    # Process document
                    document_id = process_document(
                        file_path=file_path,
                        filename=uploaded_file.name,
                        file_size=uploaded_file.size
                    )

                    st.success(f" ɭ����n�L��W~W_")
                    st.info("����g�O�e�WfO`UD")

                except Exception as e:
                    st.error(f"�-k���LzW~W_: {e}")

        st.divider()

        # Document info
        if st.session_state.current_document_id:
            st.markdown("## =� �(nɭ����")
            db = get_session()
            try:
                doc = crud.get_document(db, st.session_state.current_document_id)
                if doc:
                    st.markdown(f"**ա��:** {doc.filename}")
                    st.markdown(f"**�����:** {doc.status}")
                    st.markdown(f"**�������B:** {doc.upload_date.strftime('%Y-%m-%d %H:%M:%S')}")
            finally:
                db.close()

        st.divider()

        # Clear chat button
        if st.button("=� ����et���", use_container_width=True):
            st.session_state.messages = []
            if st.session_state.qa_manager:
                st.session_state.qa_manager.clear_memory()
            st.rerun()

        # Session info
        st.divider()
        st.markdown("## 9 �÷���1")
        st.caption(f"�÷��ID: {st.session_state.session_id[:8]}...")
        st.caption(f"�û��p: {len(st.session_state.messages)}")

    # Main content
    if st.session_state.current_document_id:
        display_chat_interface()
    else:
        st.info("=H �����K�PDFա�뒢�����WfO`UD")

        # Instructions
        st.markdown("### =� D�")
        st.markdown("""
        1. �����K� PDFա�뒢�����
        2. ɭ����L�U��~g�dp�p	
        3. ����k�O�e�
        4. AIL ɭ����n����k�T�
        """)

        st.markdown("### ( y�")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("- = **ؾ�"**: ٯ��"g�#�1� �Oz�")
            st.markdown("- =� **q�**: ���W_�6j�q")
        with col2:
            st.markdown("- =� **�gCh:**: �Tn9�hj��@�:")
            st.markdown("- =� **et�X**: qet����X")


if __name__ == "__main__":
    main()
