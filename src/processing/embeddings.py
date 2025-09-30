"""Embedding generation utilities."""
import os
import logging
from langchain_openai import OpenAIEmbeddings

logger = logging.getLogger(__name__)


def get_embeddings(model: str = None) -> OpenAIEmbeddings:
    """
    Get OpenAI embeddings model.

    Args:
        model: Model name (default from env: EMBEDDING_MODEL or 'text-embedding-3-small')

    Returns:
        Configured OpenAIEmbeddings instance

    Raises:
        ValueError: If OPENAI_API_KEY is not set
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable is not set")

    if model is None:
        model = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")

    logger.info(f"Initializing embeddings with model: {model}")
    return OpenAIEmbeddings(
        model=model,
        openai_api_key=api_key
    )