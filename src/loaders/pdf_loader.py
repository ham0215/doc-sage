"""PDF document loader implementation."""
import logging
from typing import List
from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader
from langchain.schema import Document

from .base_loader import BaseDocumentLoader
from ..processing.text_splitter import get_text_splitter

logger = logging.getLogger(__name__)


class PDFDocumentLoader(BaseDocumentLoader):
    """PDF document loader using PyPDFLoader."""

    def __init__(self):
        """Initialize PDF loader."""
        self.text_splitter = get_text_splitter()

    def load(self, file_path: str) -> List[Document]:
        """
        Load a PDF document.

        Args:
            file_path: Path to the PDF file

        Returns:
            List of Document objects, one per page

        Raises:
            FileNotFoundError: If the file doesn't exist
            Exception: If PDF loading fails
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"PDF file not found: {file_path}")

        try:
            logger.info(f"Loading PDF: {file_path}")
            loader = PyPDFLoader(str(path))
            documents = loader.load()
            logger.info(f"Loaded {len(documents)} pages from {path.name}")
            return documents
        except Exception as e:
            logger.error(f"Failed to load PDF {file_path}: {e}")
            raise

    def load_and_split(self, file_path: str) -> List[Document]:
        """
        Load a PDF and split it into chunks.

        Args:
            file_path: Path to the PDF file

        Returns:
            List of Document objects split into chunks

        Raises:
            FileNotFoundError: If the file doesn't exist
            Exception: If PDF loading or splitting fails
        """
        try:
            documents = self.load(file_path)
            chunks = self.text_splitter.split_documents(documents)
            logger.info(f"Split {len(documents)} pages into {len(chunks)} chunks")
            return chunks
        except Exception as e:
            logger.error(f"Failed to load and split PDF {file_path}: {e}")
            raise