"""Base document loader interface."""
from abc import ABC, abstractmethod
from typing import List
from langchain.schema import Document


class BaseDocumentLoader(ABC):
    """Abstract base class for document loaders."""

    @abstractmethod
    def load(self, file_path: str) -> List[Document]:
        """
        Load a document from the given file path.

        Args:
            file_path: Path to the document file

        Returns:
            List of Document objects containing the loaded content
        """
        pass

    @abstractmethod
    def load_and_split(self, file_path: str) -> List[Document]:
        """
        Load a document and split it into chunks.

        Args:
            file_path: Path to the document file

        Returns:
            List of Document objects split into chunks
        """
        pass