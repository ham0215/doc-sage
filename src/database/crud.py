"""CRUD operations for database models."""
import logging
from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from .models import Document, Conversation, DocumentChunk

logger = logging.getLogger(__name__)


# ============================================
# Document CRUD
# ============================================

def create_document(
    db: Session,
    filename: str,
    file_path: str,
    file_type: str,
    file_size: int = None,
    status: str = "processing"
) -> Document:
    """
    Create a new document record.

    Args:
        db: Database session
        filename: Name of the file
        file_path: Path to the file
        file_type: Type of file (e.g., 'pdf')
        file_size: Size of file in bytes
        status: Processing status

    Returns:
        Created Document instance
    """
    document = Document(
        filename=filename,
        file_path=file_path,
        file_type=file_type,
        file_size=file_size,
        status=status
    )
    db.add(document)
    db.commit()
    db.refresh(document)

    logger.info(f"Created document: {document.id} - {filename}")
    return document


def get_document(db: Session, document_id: int) -> Optional[Document]:
    """Get a document by ID."""
    return db.query(Document).filter(Document.id == document_id).first()


def get_documents(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    status: str = None
) -> List[Document]:
    """
    Get list of documents.

    Args:
        db: Database session
        skip: Number of records to skip
        limit: Maximum number of records to return
        status: Filter by status (optional)

    Returns:
        List of Document instances
    """
    query = db.query(Document)

    if status:
        query = query.filter(Document.status == status)

    return query.offset(skip).limit(limit).all()


def update_document_status(
    db: Session,
    document_id: int,
    status: str
) -> Optional[Document]:
    """
    Update document status.

    Args:
        db: Database session
        document_id: ID of the document
        status: New status

    Returns:
        Updated Document instance or None if not found
    """
    document = get_document(db, document_id)
    if document:
        document.status = status
        db.commit()
        db.refresh(document)
        logger.info(f"Updated document {document_id} status to: {status}")

    return document


def delete_document(db: Session, document_id: int) -> bool:
    """
    Delete a document.

    Args:
        db: Database session
        document_id: ID of the document

    Returns:
        True if deleted, False if not found
    """
    document = get_document(db, document_id)
    if document:
        db.delete(document)
        db.commit()
        logger.info(f"Deleted document: {document_id}")
        return True

    return False


# ============================================
# Conversation CRUD
# ============================================

def create_conversation(
    db: Session,
    session_id: str,
    user_message: str,
    assistant_message: str,
    document_id: int = None
) -> Conversation:
    """
    Create a new conversation record.

    Args:
        db: Database session
        session_id: Session identifier
        user_message: User's message
        assistant_message: Assistant's response
        document_id: Associated document ID (optional)

    Returns:
        Created Conversation instance
    """
    conversation = Conversation(
        session_id=session_id,
        document_id=document_id,
        user_message=user_message,
        assistant_message=assistant_message
    )
    db.add(conversation)
    db.commit()
    db.refresh(conversation)

    logger.info(f"Created conversation: {conversation.id} for session {session_id}")
    return conversation


def get_conversations_by_session(
    db: Session,
    session_id: str,
    limit: int = 50
) -> List[Conversation]:
    """
    Get conversation history for a session.

    Args:
        db: Database session
        session_id: Session identifier
        limit: Maximum number of records to return

    Returns:
        List of Conversation instances ordered by creation time
    """
    return (
        db.query(Conversation)
        .filter(Conversation.session_id == session_id)
        .order_by(Conversation.created_at.asc())
        .limit(limit)
        .all()
    )


def get_conversations_by_document(
    db: Session,
    document_id: int,
    limit: int = 50
) -> List[Conversation]:
    """
    Get conversations related to a specific document.

    Args:
        db: Database session
        document_id: Document ID
        limit: Maximum number of records to return

    Returns:
        List of Conversation instances
    """
    return (
        db.query(Conversation)
        .filter(Conversation.document_id == document_id)
        .order_by(Conversation.created_at.desc())
        .limit(limit)
        .all()
    )


def delete_conversations_by_session(db: Session, session_id: str) -> int:
    """
    Delete all conversations for a session.

    Args:
        db: Database session
        session_id: Session identifier

    Returns:
        Number of deleted records
    """
    count = (
        db.query(Conversation)
        .filter(Conversation.session_id == session_id)
        .delete()
    )
    db.commit()

    logger.info(f"Deleted {count} conversations for session {session_id}")
    return count


# ============================================
# DocumentChunk CRUD
# ============================================

def create_document_chunk(
    db: Session,
    document_id: int,
    chunk_index: int,
    content: str,
    vector_id: str = None
) -> DocumentChunk:
    """
    Create a document chunk record.

    Args:
        db: Database session
        document_id: Parent document ID
        chunk_index: Index of this chunk
        content: Chunk content
        vector_id: Chroma vector ID

    Returns:
        Created DocumentChunk instance
    """
    chunk = DocumentChunk(
        document_id=document_id,
        chunk_index=chunk_index,
        content=content,
        vector_id=vector_id
    )
    db.add(chunk)
    db.commit()
    db.refresh(chunk)

    return chunk


def get_document_chunks(
    db: Session,
    document_id: int
) -> List[DocumentChunk]:
    """
    Get all chunks for a document.

    Args:
        db: Database session
        document_id: Document ID

    Returns:
        List of DocumentChunk instances ordered by chunk_index
    """
    return (
        db.query(DocumentChunk)
        .filter(DocumentChunk.document_id == document_id)
        .order_by(DocumentChunk.chunk_index.asc())
        .all()
    )


def delete_document_chunks(db: Session, document_id: int) -> int:
    """
    Delete all chunks for a document.

    Args:
        db: Database session
        document_id: Document ID

    Returns:
        Number of deleted records
    """
    count = (
        db.query(DocumentChunk)
        .filter(DocumentChunk.document_id == document_id)
        .delete()
    )
    db.commit()

    logger.info(f"Deleted {count} chunks for document {document_id}")
    return count