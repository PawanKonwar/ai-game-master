import os
import uuid
from typing import Optional
from dotenv import load_dotenv
from langchain.chat_models import ChatOpenAI
from langchain.agents import AgentExecutor
from langchain.agents.openai_functions_agent.base import OpenAIFunctionsAgent
from langchain.agents.openai_functions_agent.agent_token_buffer_memory import AgentTokenBufferMemory
from langchain.prompts import MessagesPlaceholder, ChatPromptTemplate
from langchain.schema import SystemMessage
from tools import dice_roller_tool
from memory_store import memory_store

# Load environment variables
load_dotenv()

# Get OpenAI API key from environment
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


class GameMasterAgent:
    """A LangChain-based AI Game Master agent for fantasy role-playing games."""
    
    def __init__(self, session_id: Optional[str] = None):
        """
        Initialize the Game Master agent with OpenAI and memory.
        
        Args:
            session_id: Optional session ID for tracking game sessions. If not provided, a new one is generated.
        """
        if not OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY not found in environment variables. Please check your .env file.")
        
        # Initialize session ID
        self.session_id = session_id or str(uuid.uuid4())
        
        # Initialize memory store
        self.memory_store = memory_store
        
        # Initialize OpenAI Chat model
        self.llm = ChatOpenAI(
            openai_api_key=OPENAI_API_KEY,
            temperature=0.7,
            model_name="gpt-3.5-turbo"
        )
        
        # System prompt for fantasy game master
        self.system_prompt = """You are an experienced and creative fantasy game master for a tabletop role-playing game. 
Your role is to:
- Create immersive and engaging fantasy worlds and scenarios
- Describe vivid scenes with rich details about environments, characters, and atmosphere
- Respond to player actions with dynamic and interesting consequences
- Maintain consistency in the game world and story
- Balance challenge and fun for the players
- Use descriptive language to bring the fantasy world to life
- Roll dice when needed for game mechanics (e.g., determining outcomes, random events, damage, skill checks)
- Access and use past game memories to maintain consistency and build upon previous sessions

You have access to:
1. A dice roller tool that can roll dice in standard notation:
   - Use "3d6" to roll three 6-sided dice
   - Use "1d20" to roll one 20-sided die
   - Use "2d10+5" to roll two 10-sided dice and add 5
   - Use the dice_roller tool whenever you need to determine random outcomes, damage, skill checks, or any game mechanics that require dice rolls

2. A persistent memory system that stores:
   - Past game sessions and events
   - NPC information, personalities, and relationships
   - Location descriptions and world lore
   - Item information and properties
   
   When generating scenes, relevant memories from past sessions will be provided to you. Use these memories to:
   - Maintain consistency with previously established NPCs, locations, and events
   - Reference past player actions and their consequences
   - Build upon existing world lore and story elements
   - Create a cohesive narrative that connects across sessions

You should create scenes that are:
- Rich in detail and atmosphere
- Interactive and responsive to player choices
- Balanced between action, exploration, and role-playing opportunities
- Consistent with fantasy genre conventions
- Include dice rolls when appropriate for game mechanics
- Consistent with past game memories and established world elements

Always respond in character as the game master, providing engaging narrative and clear descriptions. When you use dice rolls, incorporate the results naturally into your narrative. When relevant memories are provided, weave them naturally into your scene descriptions to maintain continuity."""
        
        # Initialize tools
        self.tools = [dice_roller_tool]
        
        # Create memory for the agent
        self.memory = AgentTokenBufferMemory(
            llm=self.llm,
            memory_key="chat_history",
            return_messages=True
        )
        
        # Create prompt with system message
        prompt = OpenAIFunctionsAgent.create_prompt(
            system_message=SystemMessage(content=self.system_prompt),
            extra_prompt_messages=[MessagesPlaceholder(variable_name="chat_history")]
        )
        
        # Create the agent
        agent = OpenAIFunctionsAgent(
            llm=self.llm,
            tools=self.tools,
            prompt=prompt
        )
        
        # Create agent executor
        self.agent_executor = AgentExecutor(
            agent=agent,
            tools=self.tools,
            memory=self.memory,
            verbose=False,
            return_intermediate_steps=True
        )
    
    def generate_scene(self, prompt: str, include_dice_rolls: bool = False) -> str:
        """
        Generate a game scene based on a user prompt with RAG memory integration.
        
        Args:
            prompt: A description of what kind of scene to generate
            include_dice_rolls: If True, the AI may include dice rolls in the scene generation
            
        Returns:
            A generated game scene description
        """
        # Retrieve relevant memories using RAG
        relevant_memories = self._retrieve_relevant_memories(prompt)
        
        # Build context from retrieved memories
        memory_context = self._format_memory_context(relevant_memories)
        
        # Format the prompt to request a scene with memory context
        if include_dice_rolls:
            scene_prompt = f"""Create a detailed fantasy game scene: {prompt}

{memory_context}

Feel free to use dice rolls to determine random elements, outcomes, or game mechanics as appropriate. Use the provided memories to maintain consistency with past sessions."""
        else:
            scene_prompt = f"""Create a detailed fantasy game scene: {prompt}

{memory_context}

Use the provided memories to maintain consistency with past sessions and build upon established world elements."""
        
        # Use agent executor which has access to tools
        result = self.agent_executor({"input": scene_prompt})
        response_text = result["output"]
        
        # Save the generated scene to memory
        self._save_scene_to_memory(prompt, response_text)
        
        return response_text
    
    def _retrieve_relevant_memories(self, query: str, k: int = 5) -> list:
        """
        Retrieve relevant memories from all collections using RAG.
        
        Args:
            query: Search query
            k: Number of results per collection
            
        Returns:
            List of relevant documents from all collections
        """
        all_memories = []
        
        # Retrieve from sessions
        try:
            session_memories = self.memory_store.retrieve_session_memories(
                query, session_id=self.session_id, k=k
            )
            all_memories.extend(session_memories)
        except Exception as e:
            print(f"Error retrieving session memories: {e}")
        
        # Retrieve from NPCs
        try:
            npc_memories = self.memory_store.retrieve_npc_memories(query, k=k)
            all_memories.extend(npc_memories)
        except Exception as e:
            print(f"Error retrieving NPC memories: {e}")
        
        # Retrieve from locations
        try:
            location_memories = self.memory_store.retrieve_location_memories(query, k=k)
            all_memories.extend(location_memories)
        except Exception as e:
            print(f"Error retrieving location memories: {e}")
        
        # Retrieve from items
        try:
            item_memories = self.memory_store.retrieve_item_memories(query, k=k)
            all_memories.extend(item_memories)
        except Exception as e:
            print(f"Error retrieving item memories: {e}")
        
        return all_memories
    
    def _format_memory_context(self, memories: list) -> str:
        """
        Format retrieved memories into a context string for the prompt.
        
        Args:
            memories: List of Document objects from memory retrieval
            
        Returns:
            Formatted context string
        """
        if not memories:
            return "No relevant past memories found. Create a new scene from scratch."
        
        context_parts = ["Relevant memories from past sessions:"]
        
        for i, memory in enumerate(memories, 1):
            memory_type = memory.metadata.get("type", "unknown")
            content = memory.page_content
            
            # Add metadata context if available
            metadata_info = []
            if "npc_name" in memory.metadata:
                metadata_info.append(f"NPC: {memory.metadata['npc_name']}")
            if "location_name" in memory.metadata:
                metadata_info.append(f"Location: {memory.metadata['location_name']}")
            if "item_name" in memory.metadata:
                metadata_info.append(f"Item: {memory.metadata['item_name']}")
            
            metadata_str = f" ({', '.join(metadata_info)})" if metadata_info else ""
            context_parts.append(f"{i}. [{memory_type}]{metadata_str}: {content}")
        
        return "\n".join(context_parts)
    
    def _save_scene_to_memory(self, prompt: str, scene_text: str) -> None:
        """
        Save the generated scene to memory.
        
        Args:
            prompt: The original prompt used to generate the scene
            scene_text: The generated scene text
        """
        try:
            # Save to session memory
            self.memory_store.save_session_memory(
                session_id=self.session_id,
                content=f"Prompt: {prompt}\n\nGenerated Scene: {scene_text}",
                metadata={
                    "prompt": prompt,
                    "scene_type": "generated",
                    "timestamp": str(uuid.uuid4())  # Simple timestamp placeholder
                }
            )
        except Exception as e:
            print(f"Error saving scene to memory: {e}")
    
    def respond(self, player_input: str) -> str:
        """
        Respond to player input in the game with memory integration.
        
        Args:
            player_input: What the player says or does
            
        Returns:
            The game master's response
        """
        # Retrieve relevant memories for context
        relevant_memories = self._retrieve_relevant_memories(player_input, k=3)
        memory_context = self._format_memory_context(relevant_memories)
        
        # Enhance the input with memory context
        enhanced_input = f"{player_input}\n\n{memory_context}"
        
        # Use agent executor which has access to tools and memory
        result = self.agent_executor({"input": enhanced_input})
        response_text = result["output"]
        
        # Save player action and response to memory
        try:
            self.memory_store.save_session_memory(
                session_id=self.session_id,
                content=f"Player: {player_input}\n\nGame Master: {response_text}",
                metadata={
                    "type": "player_interaction",
                    "player_input": player_input
                }
            )
        except Exception as e:
            print(f"Error saving interaction to memory: {e}")
        
        return response_text
    
    def clear_memory(self):
        """Clear the conversation memory."""
        if hasattr(self.memory, 'clear'):
            self.memory.clear()
        elif hasattr(self.memory, 'chat_memory'):
            self.memory.chat_memory.clear()


# Create a global instance for easy import
game_master = GameMasterAgent()
