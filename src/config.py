"""Application configuration."""
import os
import logging
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Application configuration."""

    # OpenAI
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")

    # Embedding
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
    CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", "1000"))
    CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", "200"))

    # Vector Store
    CHROMA_PERSIST_DIRECTORY: str = os.getenv(
        "CHROMA_PERSIST_DIRECTORY",
        "/app/data/vectorstore"
    )

    # Database
    DB_PATH: str = os.getenv("DB_PATH", "/app/data/doc-sage.db")

    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    @classmethod
    def setup_logging(cls):
        """Set up logging configuration."""
        logging.basicConfig(
            level=getattr(logging, cls.LOG_LEVEL.upper()),
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

    @classmethod
    def validate(cls):
        """Validate required configuration."""
        if not cls.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is not set")

        # Ensure directories exist
        Path(cls.CHROMA_PERSIST_DIRECTORY).mkdir(parents=True, exist_ok=True)
        Path(cls.DB_PATH).parent.mkdir(parents=True, exist_ok=True)


# Initialize logging
Config.setup_logging()