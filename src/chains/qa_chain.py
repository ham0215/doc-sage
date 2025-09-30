"""Question-Answering chain implementation."""
import os
import logging
from typing import Dict, List, Optional

from langchain_openai import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain
from langchain.prompts import PromptTemplate
from langchain_community.vectorstores import Chroma

from .memory import ConversationMemoryManager, create_memory

logger = logging.getLogger(__name__)


# Default QA prompt template
DEFAULT_QA_TEMPLATE = """以下のコンテキストを使用して、質問に答えてください。
答えがわからない場合は、「わかりません」と答えてください。無理に答えを作らないでください。

コンテキスト:
{context}

質問: {question}

回答:"""


class QAChainManager:
    """Manages QA chain for document question-answering."""

    def __init__(
        self,
        vectorstore: Chroma,
        model_name: str = "gpt-3.5-turbo",
        temperature: float = 0,
        max_tokens: int = 500,
        k: int = 4
    ):
        """
        Initialize QA chain manager.

        Args:
            vectorstore: Chroma vector store instance
            model_name: OpenAI model name
            temperature: Model temperature (0 = deterministic)
            max_tokens: Maximum tokens in response
            k: Number of documents to retrieve
        """
        self.vectorstore = vectorstore
        self.k = k

        # Initialize LLM
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")

        self.llm = ChatOpenAI(
            model_name=model_name,
            temperature=temperature,
            max_tokens=max_tokens,
            openai_api_key=api_key
        )

        # Initialize memory manager
        self.memory_manager = ConversationMemoryManager()

        logger.info(
            f"Initialized QAChainManager with model: {model_name}, k: {k}"
        )

    def create_chain(self) -> ConversationalRetrievalChain:
        """
        Create a conversational retrieval chain.

        Returns:
            ConversationalRetrievalChain instance
        """
        chain = ConversationalRetrievalChain.from_llm(
            llm=self.llm,
            retriever=self.vectorstore.as_retriever(search_kwargs={"k": self.k}),
            memory=self.memory_manager.memory,
            return_source_documents=True,
            verbose=False
        )

        logger.info("Created ConversationalRetrievalChain")
        return chain

    def ask(
        self,
        question: str,
        chain: Optional[ConversationalRetrievalChain] = None
    ) -> Dict:
        """
        Ask a question and get an answer.

        Args:
            question: User's question
            chain: Existing chain (if None, creates new one)

        Returns:
            Dictionary with 'answer' and 'source_documents' keys
        """
        if chain is None:
            chain = self.create_chain()

        logger.info(f"Processing question: {question[:100]}...")

        try:
            result = chain({"question": question})

            answer = result["answer"]
            source_docs = result.get("source_documents", [])

            logger.info(f"Generated answer with {len(source_docs)} source documents")

            return {
                "answer": answer,
                "source_documents": source_docs
            }

        except Exception as e:
            logger.error(f"Error processing question: {e}")
            raise

    def ask_with_sources(
        self,
        question: str,
        chain: Optional[ConversationalRetrievalChain] = None
    ) -> Dict:
        """
        Ask a question and get an answer with formatted sources.

        Args:
            question: User's question
            chain: Existing chain (if None, creates new one)

        Returns:
            Dictionary with 'answer', 'sources', and 'source_documents' keys
        """
        result = self.ask(question, chain)

        # Format sources
        sources = []
        for i, doc in enumerate(result["source_documents"], 1):
            source_info = {
                "index": i,
                "content": doc.page_content[:200] + "...",
                "metadata": doc.metadata
            }
            sources.append(source_info)

        result["sources"] = sources

        return result

    def get_memory(self) -> ConversationMemoryManager:
        """Get the conversation memory manager."""
        return self.memory_manager

    def clear_memory(self):
        """Clear conversation history."""
        self.memory_manager.clear()
        logger.info("Cleared conversation memory")


def create_simple_qa_chain(
    vectorstore: Chroma,
    model_name: str = "gpt-3.5-turbo",
    k: int = 4
) -> ConversationalRetrievalChain:
    """
    Create a simple QA chain without the manager wrapper.

    Args:
        vectorstore: Chroma vector store
        model_name: OpenAI model name
        k: Number of documents to retrieve

    Returns:
        ConversationalRetrievalChain instance
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable is not set")

    llm = ChatOpenAI(
        model_name=model_name,
        temperature=0,
        openai_api_key=api_key
    )

    memory = create_memory()

    chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vectorstore.as_retriever(search_kwargs={"k": k}),
        memory=memory,
        return_source_documents=True
    )

    return chain
