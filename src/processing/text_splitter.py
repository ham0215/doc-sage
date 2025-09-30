"""Text splitting utilities for document processing."""
import os
from langchain.text_splitter import RecursiveCharacterTextSplitter


def get_text_splitter(
    chunk_size: int = None,
    chunk_overlap: int = None
) -> RecursiveCharacterTextSplitter:
    """
    Get a text splitter configured with specified or environment parameters.

    Args:
        chunk_size: Size of each text chunk (default from env: CHUNK_SIZE or 1000)
        chunk_overlap: Overlap between chunks (default from env: CHUNK_OVERLAP or 200)

    Returns:
        Configured RecursiveCharacterTextSplitter instance
    """
    if chunk_size is None:
        chunk_size = int(os.getenv("CHUNK_SIZE", "1000"))

    if chunk_overlap is None:
        chunk_overlap = int(os.getenv("CHUNK_OVERLAP", "200"))

    return RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        separators=["\n\n", "\n", " ", ""]
    )