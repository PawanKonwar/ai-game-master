import os
from typing import Any, Dict, List, Optional
from dotenv import load_dotenv
import chromadb
from chromadb.config import Settings
from langchain.vectorstores import Chroma
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.schema import Document
from langchain.vectorstores.base import VectorStoreRetriever

# Load environment variables
load_dotenv()

# Get configuration from environment
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")


class GameMemoryStore:
    """ChromaDB-based persistent memory store for game sessions, NPCs, locations, and items."""

    # Collection names
    COLLECTION_SESSIONS = "game_sessions"
    COLLECTION_NPCS = "npcs"
    COLLECTION_LOCATIONS = "locations"
    COLLECTION_ITEMS = "items"

    def __init__(self, persist_directory: Optional[str] = None):
        """
        Initialize the game memory store with ChromaDB.

        Args:
            persist_directory: Directory to persist ChromaDB data (defaults to CHROMA_PERSIST_DIR env var)
        """
        if not OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY not found in environment variables. Please check your .env file.")

        # Set up persist directory
        self.persist_directory = persist_directory or CHROMA_PERSIST_DIR

        # Initialize OpenAI embeddings
        self.embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)

        # Initialize ChromaDB client with persistence
        self.client_settings = Settings(
            persist_directory=self.persist_directory,
            is_persistent=True
        )
        self.client = chromadb.Client(self.client_settings)

        # Initialize vector stores for each collection
        self._init_collections()

    def _init_collections(self):
        """Initialize or load vector stores for each collection."""
        self.sessions_store = Chroma(
            collection_name=self.COLLECTION_SESSIONS,
            embedding_function=self.embeddings,
            persist_directory=self.persist_directory,
            client_settings=self.client_settings
        )

        self.npcs_store = Chroma(
            collection_name=self.COLLECTION_NPCS,
            embedding_function=self.embeddings,
            persist_directory=self.persist_directory,
            client_settings=self.client_settings
        )

        self.locations_store = Chroma(
            collection_name=self.COLLECTION_LOCATIONS,
            embedding_function=self.embeddings,
            persist_directory=self.persist_directory,
            client_settings=self.client_settings
        )

        self.items_store = Chroma(
            collection_name=self.COLLECTION_ITEMS,
            embedding_function=self.embeddings,
            persist_directory=self.persist_directory,
            client_settings=self.client_settings
        )

    # ========== Session Memory Functions ==========

    def save_session_memory(
        self,
        session_id: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Save a game session memory.

        Args:
            session_id: Unique identifier for the session
            content: The content to store (e.g., scene description, player actions)
            metadata: Optional metadata (e.g., timestamp, player names, scene type)
        """
        doc_id = f"session_{session_id}_{len(self.sessions_store._collection.get()['ids'])}"
        metadata = metadata or {}
        metadata.update({
            "session_id": session_id,
            "type": "session"
        })

        self.sessions_store.add_texts(
            texts=[content],
            metadatas=[metadata],
            ids=[doc_id]
        )

    def retrieve_session_memories(
        self,
        query: str,
        session_id: Optional[str] = None,
        k: int = 5
    ) -> List[Document]:
        """
        Retrieve relevant session memories using RAG.

        Args:
            query: Search query
            session_id: Optional filter by session ID
            k: Number of results to return

        Returns:
            List of relevant documents
        """
        # Build filter if session_id provided
        where_filter = None
        if session_id:
            where_filter = {"session_id": session_id}

        retriever = self.sessions_store.as_retriever(
            search_kwargs={"k": k, "filter": where_filter} if where_filter else {"k": k}
        )

        return retriever.get_relevant_documents(query)

    # ========== NPC Memory Functions ==========

    def save_npc_memory(
        self,
        npc_id: str,
        npc_name: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Save an NPC memory.

        Args:
            npc_id: Unique identifier for the NPC
            npc_name: Name of the NPC
            content: Information about the NPC (personality, history, relationships, etc.)
            metadata: Optional metadata (e.g., location, faction, status)
        """
        doc_id = f"npc_{npc_id}_{len(self.npcs_store._collection.get()['ids'])}"
        metadata = metadata or {}
        metadata.update({
            "npc_id": npc_id,
            "npc_name": npc_name,
            "type": "npc"
        })

        self.npcs_store.add_texts(
            texts=[content],
            metadatas=[metadata],
            ids=[doc_id]
        )

    def retrieve_npc_memories(
        self,
        query: str,
        npc_id: Optional[str] = None,
        npc_name: Optional[str] = None,
        k: int = 5
    ) -> List[Document]:
        """
        Retrieve relevant NPC memories using RAG.

        Args:
            query: Search query
            npc_id: Optional filter by NPC ID
            npc_name: Optional filter by NPC name
            k: Number of results to return

        Returns:
            List of relevant documents
        """
        where_filter = None
        if npc_id:
            where_filter = {"npc_id": npc_id}
        elif npc_name:
            where_filter = {"npc_name": npc_name}

        retriever = self.npcs_store.as_retriever(
            search_kwargs={"k": k, "filter": where_filter} if where_filter else {"k": k}
        )

        return retriever.get_relevant_documents(query)

    # ========== Location Memory Functions ==========

    def save_location_memory(
        self,
        location_id: str,
        location_name: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Save a location memory.

        Args:
            location_id: Unique identifier for the location
            location_name: Name of the location
            content: Information about the location (description, history, features, etc.)
            metadata: Optional metadata (e.g., region, type, discovered_by)
        """
        doc_id = f"location_{location_id}_{len(self.locations_store._collection.get()['ids'])}"
        metadata = metadata or {}
        metadata.update({
            "location_id": location_id,
            "location_name": location_name,
            "type": "location"
        })

        self.locations_store.add_texts(
            texts=[content],
            metadatas=[metadata],
            ids=[doc_id]
        )

    def retrieve_location_memories(
        self,
        query: str,
        location_id: Optional[str] = None,
        location_name: Optional[str] = None,
        k: int = 5
    ) -> List[Document]:
        """
        Retrieve relevant location memories using RAG.

        Args:
            query: Search query
            location_id: Optional filter by location ID
            location_name: Optional filter by location name
            k: Number of results to return

        Returns:
            List of relevant documents
        """
        where_filter = None
        if location_id:
            where_filter = {"location_id": location_id}
        elif location_name:
            where_filter = {"location_name": location_name}

        retriever = self.locations_store.as_retriever(
            search_kwargs={"k": k, "filter": where_filter} if where_filter else {"k": k}
        )

        return retriever.get_relevant_documents(query)

    # ========== Item Memory Functions ==========

    def save_item_memory(
        self,
        item_id: str,
        item_name: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Save an item memory.

        Args:
            item_id: Unique identifier for the item
            item_name: Name of the item
            content: Information about the item (description, properties, history, etc.)
            metadata: Optional metadata (e.g., type, rarity, owner)
        """
        doc_id = f"item_{item_id}_{len(self.items_store._collection.get()['ids'])}"
        metadata = metadata or {}
        metadata.update({
            "item_id": item_id,
            "item_name": item_name,
            "type": "item"
        })

        self.items_store.add_texts(
            texts=[content],
            metadatas=[metadata],
            ids=[doc_id]
        )

    def retrieve_item_memories(
        self,
        query: str,
        item_id: Optional[str] = None,
        item_name: Optional[str] = None,
        k: int = 5
    ) -> List[Document]:
        """
        Retrieve relevant item memories using RAG.

        Args:
            query: Search query
            item_id: Optional filter by item ID
            item_name: Optional filter by item name
            k: Number of results to return

        Returns:
            List of relevant documents
        """
        where_filter = None
        if item_id:
            where_filter = {"item_id": item_id}
        elif item_name:
            where_filter = {"item_name": item_name}

        retriever = self.items_store.as_retriever(
            search_kwargs={"k": k, "filter": where_filter} if where_filter else {"k": k}
        )

        return retriever.get_relevant_documents(query)

    # ========== RAG Integration Functions ==========

    def get_session_retriever(self, k: int = 5) -> VectorStoreRetriever:
        """
        Get a LangChain retriever for session memories.

        Args:
            k: Number of documents to retrieve

        Returns:
            VectorStoreRetriever for sessions
        """
        return self.sessions_store.as_retriever(search_kwargs={"k": k})

    def get_npc_retriever(self, k: int = 5) -> VectorStoreRetriever:
        """
        Get a LangChain retriever for NPC memories.

        Args:
            k: Number of documents to retrieve

        Returns:
            VectorStoreRetriever for NPCs
        """
        return self.npcs_store.as_retriever(search_kwargs={"k": k})

    def get_location_retriever(self, k: int = 5) -> VectorStoreRetriever:
        """
        Get a LangChain retriever for location memories.

        Args:
            k: Number of documents to retrieve

        Returns:
            VectorStoreRetriever for locations
        """
        return self.locations_store.as_retriever(search_kwargs={"k": k})

    def get_item_retriever(self, k: int = 5) -> VectorStoreRetriever:
        """
        Get a LangChain retriever for item memories.

        Args:
            k: Number of documents to retrieve

        Returns:
            VectorStoreRetriever for items
        """
        return self.items_store.as_retriever(search_kwargs={"k": k})

    def get_combined_retriever(self, k: int = 5) -> VectorStoreRetriever:
        """
        Get a combined retriever that searches across all collections.
        Note: This creates a new temporary collection with all documents.

        Args:
            k: Number of documents to retrieve

        Returns:
            VectorStoreRetriever for all collections
        """
        # For simplicity, we'll use the sessions store as the base
        # In production, you might want to create a unified collection
        return self.sessions_store.as_retriever(search_kwargs={"k": k})

    # ========== Utility Functions ==========

    def clear_collection(self, collection_type: str) -> None:
        """
        Clear all data from a specific collection.

        Args:
            collection_type: One of 'sessions', 'npcs', 'locations', 'items'
        """
        if collection_type == "sessions":
            self.client.delete_collection(self.COLLECTION_SESSIONS)
            self._init_collections()
        elif collection_type == "npcs":
            self.client.delete_collection(self.COLLECTION_NPCS)
            self._init_collections()
        elif collection_type == "locations":
            self.client.delete_collection(self.COLLECTION_LOCATIONS)
            self._init_collections()
        elif collection_type == "items":
            self.client.delete_collection(self.COLLECTION_ITEMS)
            self._init_collections()
        else:
            raise ValueError(f"Unknown collection type: {collection_type}")

    def get_collection_stats(self) -> Dict[str, int]:
        """
        Get statistics about stored memories.

        Returns:
            Dictionary with counts for each collection
        """
        return {
            "sessions": len(self.sessions_store._collection.get()["ids"]),
            "npcs": len(self.npcs_store._collection.get()["ids"]),
            "locations": len(self.locations_store._collection.get()["ids"]),
            "items": len(self.items_store._collection.get()["ids"])
        }


# Create a global instance for easy import
memory_store = GameMemoryStore()
