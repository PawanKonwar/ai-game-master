import os
import time
import uuid
from typing import Optional
from dotenv import load_dotenv
from loguru import logger
from langchain.chat_models import ChatOpenAI
from langchain.agents import AgentExecutor
from langchain.agents.openai_functions_agent.base import OpenAIFunctionsAgent
from langchain.agents.openai_functions_agent.agent_token_buffer_memory import AgentTokenBufferMemory
from langchain.prompts import MessagesPlaceholder, ChatPromptTemplate
from langchain.schema import SystemMessage
from tools import dice_roller_tool
from memory_store import memory_store

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

class GameMasterAgent:
    def __init__(self, session_id: Optional[str] = None):
        if not OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY not found in environment variables.")
        
        self.session_id = session_id or str(uuid.uuid4())
        self.memory_store = memory_store
        self.llm = ChatOpenAI(
            openai_api_key=OPENAI_API_KEY,
            temperature=0.7,
            model_name="gpt-3.5-turbo"
        )
        
        # STRICT SYSTEM PROMPT: Forces the "Choice X:" markers for the UI to find
        self.system_prompt = """You are an expert, fast-paced Fantasy Game Master. 
STRICT RESPONSE RULES:
1. BREVITY: Max 3 punchy sentences for the narrative.
2. FORMATTING: Use **bold** for items, locations, and NPCs.
3. CHOICES: You MUST end every response with two distinct choices starting with 'Choice 1:' and 'Choice 2:'.
4. TONE: Immersive and high-stakes.

Example:
The **Iron Door** creaks open, revealing a hoard of **Goblins**. They haven't seen you yet.
Choice 1: Attack the Goblins with your sword.
Choice 2: Sneak past them into the shadows.
"""
        
        self.tools = [dice_roller_tool]
        self.memory = AgentTokenBufferMemory(llm=self.llm, memory_key="chat_history", return_messages=True)
        
        prompt = OpenAIFunctionsAgent.create_prompt(
            system_message=SystemMessage(content=self.system_prompt),
            extra_prompt_messages=[MessagesPlaceholder(variable_name="chat_history")]
        )
        
        agent = OpenAIFunctionsAgent(llm=self.llm, tools=self.tools, prompt=prompt)
        self.agent_executor = AgentExecutor(
            agent=agent, 
            tools=self.tools, 
            memory=self.memory, 
            verbose=False, 
            return_intermediate_steps=True
        )

    def generate_scene(self, prompt: str, include_dice_rolls: bool = False) -> str:
        relevant_memories = self._retrieve_relevant_memories(prompt)
        memory_context = self._format_memory_context(relevant_memories)
        scene_prompt = f"Narrate this scene: {prompt}\n\nContext: {memory_context}\nInclude 2 clear choices at the end."
        
        result = self.agent_executor({"input": scene_prompt})
        return result["output"]

    def respond(self, player_input: str) -> str:
        relevant_memories = self._retrieve_relevant_memories(player_input, k=3)
        memory_context = self._format_memory_context(relevant_memories)
        result = self.agent_executor({"input": f"Player: {player_input}\n\n{memory_context}"})
        return result["output"]

    def _retrieve_relevant_memories(self, query: str, k: int = 5) -> list:
        try:
            return self.memory_store.retrieve_session_memories(query, session_id=self.session_id, k=k)
        except: return []

    def _format_memory_context(self, memories: list) -> str:
        if not memories: return ""
        return "Recent History:\n" + "\n".join([f"- {m.page_content}" for m in memories])

game_master = GameMasterAgent()