"""Conversation memory management."""
import logging
from typing import List, Dict
from langchain.memory import ConversationBufferMemory
from langchain.schema import BaseMessage, HumanMessage, AIMessage

logger = logging.getLogger(__name__)


class ConversationMemoryManager:
    """Manages conversation memory for QA chains."""

    def __init__(self, memory_key: str = "chat_history", return_messages: bool = True):
        """
        Initialize conversation memory manager.

        Args:
            memory_key: Key to store conversation history
            return_messages: Whether to return messages as objects (True) or strings (False)
        """
        self.memory_key = memory_key
        self.return_messages = return_messages
        self.memory = ConversationBufferMemory(
            memory_key=memory_key,
            return_messages=return_messages
        )
        logger.info(f"Initialized ConversationMemoryManager with key: {memory_key}")

    def add_user_message(self, message: str):
        """
        Add a user message to memory.

        Args:
            message: User's message
        """
        self.memory.chat_memory.add_user_message(message)
        logger.debug(f"Added user message: {message[:50]}...")

    def add_ai_message(self, message: str):
        """
        Add an AI message to memory.

        Args:
            message: AI's response
        """
        self.memory.chat_memory.add_ai_message(message)
        logger.debug(f"Added AI message: {message[:50]}...")

    def add_exchange(self, user_message: str, ai_message: str):
        """
        Add a complete message exchange.

        Args:
            user_message: User's message
            ai_message: AI's response
        """
        self.add_user_message(user_message)
        self.add_ai_message(ai_message)

    def get_messages(self) -> List[BaseMessage]:
        """
        Get all messages in memory.

        Returns:
            List of message objects
        """
        return self.memory.chat_memory.messages

    def get_history_as_string(self) -> str:
        """
        Get conversation history as a formatted string.

        Returns:
            Formatted conversation history
        """
        messages = self.get_messages()
        history_lines = []

        for msg in messages:
            if isinstance(msg, HumanMessage):
                history_lines.append(f"User: {msg.content}")
            elif isinstance(msg, AIMessage):
                history_lines.append(f"Assistant: {msg.content}")

        return "\n".join(history_lines)

    def clear(self):
        """Clear all conversation history."""
        self.memory.clear()
        logger.info("Cleared conversation memory")

    def load_from_history(self, history: List[Dict[str, str]]):
        """
        Load conversation history from a list of exchanges.

        Args:
            history: List of dicts with 'user' and 'assistant' keys
        """
        self.clear()
        for exchange in history:
            self.add_exchange(exchange["user"], exchange["assistant"])

        logger.info(f"Loaded {len(history)} exchanges into memory")


def create_memory(memory_key: str = "chat_history") -> ConversationBufferMemory:
    """
    Create a simple ConversationBufferMemory instance.

    Args:
        memory_key: Key to store conversation history

    Returns:
        ConversationBufferMemory instance
    """
    return ConversationBufferMemory(
        memory_key=memory_key,
        return_messages=True
    )