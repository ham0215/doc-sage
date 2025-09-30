"""Vector store management using Chroma."""
import os
import logging
from typing import List, Optional
from pathlib import Path

from langchain_community.vectorstores import Chroma
from langchain.schema import Document

from .embeddings import get_embeddings

logger = logging.getLogger(__name__)


class VectorStoreManager:
    """Manages Chroma vector store operations."""

    def __init__(
        self,
        persist_directory: str = None,
        collection_name: str = "documents"
    ):
        """
        Initialize vector store manager.

        Args:
            persist_directory: Directory to persist vector store (default from env: CHROMA_PERSIST_DIRECTORY)
            collection_name: Name of the collection
        """
        if persist_directory is None:
            persist_directory = os.getenv(
                "CHROMA_PERSIST_DIRECTORY",
                "/app/data/vectorstore"
            )

        self.persist_directory = persist_directory
        self.collection_name = collection_name
        self.embeddings = get_embeddings()

        # Ensure directory exists
        Path(persist_directory).mkdir(parents=True, exist_ok=True)

        logger.info(
            f"Initialized VectorStoreManager with persist_directory: {persist_directory}, "
            f"collection: {collection_name}"
        )

    def create_vectorstore(
        self,
        documents: List[Document]
    ) -> Chroma:
        """
        Create a new vector store from documents.

        Args:
            documents: List of documents to add to the vector store

        Returns:
            Chroma vector store instance
        """
        logger.info(f"Creating vector store with {len(documents)} documents")

        vectorstore = Chroma.from_documents(
            documents=documents,
            embedding=self.embeddings,
            collection_name=self.collection_name,
            persist_directory=self.persist_directory
        )

        logger.info("Vector store created successfully")
        return vectorstore

    def get_vectorstore(self) -> Chroma:
        """
        Get existing vector store.

        Returns:
            Chroma vector store instance
        """
        logger.info(f"Loading vector store from {self.persist_directory}")

        vectorstore = Chroma(
            collection_name=self.collection_name,
            embedding_function=self.embeddings,
            persist_directory=self.persist_directory
        )

        return vectorstore

    def add_documents(
        self,
        documents: List[Document],
        vectorstore: Optional[Chroma] = None
    ) -> Chroma:
        """
        Add documents to an existing vector store.

        Args:
            documents: List of documents to add
            vectorstore: Existing vector store (if None, loads from disk)

        Returns:
            Updated Chroma vector store instance
        """
        if vectorstore is None:
            vectorstore = self.get_vectorstore()

        logger.info(f"Adding {len(documents)} documents to vector store")
        vectorstore.add_documents(documents)

        logger.info("Documents added successfully")
        return vectorstore

    def similarity_search(
        self,
        query: str,
        k: int = 4,
        vectorstore: Optional[Chroma] = None
    ) -> List[Document]:
        """
        Search for similar documents.

        Args:
            query: Search query
            k: Number of results to return
            vectorstore: Existing vector store (if None, loads from disk)

        Returns:
            List of similar documents
        """
        if vectorstore is None:
            vectorstore = self.get_vectorstore()

        logger.info(f"Searching for top {k} similar documents")
        results = vectorstore.similarity_search(query, k=k)

        logger.info(f"Found {len(results)} results")
        return results

    def delete_collection(self):
        """Delete the vector store collection."""
        logger.warning(f"Deleting collection: {self.collection_name}")

        vectorstore = self.get_vectorstore()
        vectorstore.delete_collection()

        logger.info("Collection deleted successfully")