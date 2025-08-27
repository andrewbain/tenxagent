# in flexi_agent/agent.py
from .models import LanguageModel
from .tools import Tool
from .schemas import Message, GenerationResult, ToolCall 
from typing import List, Optional, Dict, Any
from .history import HistoryStore, InMemoryHistoryStore
from pydantic import BaseModel, Field
import json
import asyncio



class TenxAgent:
    def __init__(
        self,
        llm: LanguageModel,
        tools: List[Tool],
        system_prompt: str = None,
        max_llm_calls: int = 10, # RENAMED for clarity
        max_tokens: int = 4096,
        history_store: HistoryStore = None,
    ):
        self.llm = llm
        self.tools = {tool.name: tool for tool in tools}
        self.user_system_prompt = system_prompt
        self.max_llm_calls = max_llm_calls
        self.max_tokens = max_tokens
        self.history_store = history_store or InMemoryHistoryStore()

    def _get_system_prompt(self) -> str:
        """Get the system prompt from the LLM model, which handles tool calling instructions."""
        tools_list = list(self.tools.values()) if self.tools else None
        return self.llm.get_tool_calling_system_prompt(tools=tools_list, user_prompt=self.user_system_prompt)

    async def _execute_tool(self, tool_call: ToolCall, metadata: Dict[str, Any]) -> Message:
        """Helper to execute a single tool call and return a tool message."""
        tool = self.tools.get(tool_call.name)
        if not tool:
            result_content = f"Error: Tool '{tool_call.name}' not found."
        else:
            try:
                validated_args = tool.args_schema(**tool_call.arguments)
                result_content = await asyncio.to_thread(tool.execute, metadata=metadata, **validated_args.model_dump())
            except Exception as e:
                result_content = f"Error executing tool '{tool_call.name}': {e}"
        
        return Message(role="tool", content=result_content, tool_call_id=tool_call.id) # Assumes ToolCall has an ID

    async def run(self, user_input: str, session_id: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        metadata = metadata or {}
        llm_calls_count = 0
        total_tokens_used = 0
        messages = await self.history_store.get_messages(session_id)

        user_message = Message(role="user", content=user_input)
        await self.history_store.add_message(session_id, user_message)
        messages.append(user_message)
        
        if not any(msg.role == "system" for msg in messages):
            messages.insert(0, Message(role="system", content=self._get_system_prompt()))

        while True:
            if llm_calls_count >= self.max_llm_calls:
                return "Error: Maximum number of LLM calls reached."
            
            llm_calls_count += 1
            
            # Pass tools to the LLM (it will handle the conversion to its own format)
            tools_list = list(self.tools.values()) if self.tools else None
            generation_result = await self.llm.generate(messages, tools=tools_list, metadata=metadata)
            
            total_tokens_used += generation_result.input_tokens + generation_result.output_tokens
            if total_tokens_used >= self.max_tokens:
                return "Error: Token limit reached."
            
            response_message = generation_result.message
            await self.history_store.add_message(session_id, response_message)
            messages.append(response_message)
            
            # --- NEW: PARALLEL TOOL CALL LOGIC ---
            if response_message.tool_calls:
                # 1. Create a task for each tool call requested by the LLM
                execution_tasks = [
                    self._execute_tool(tool_call, metadata) for tool_call in response_message.tool_calls
                ]
                
                # 2. Run all tool calls concurrently
                tool_result_messages = await asyncio.gather(*execution_tasks)
                
                # 3. Add all results to history and continue the loop
                for msg in tool_result_messages:
                    await self.history_store.add_message(session_id, msg)
                    messages.append(msg)
                
                continue # Go back to the LLM with the tool results
            
            # If there are no tool calls, we have our final answer
            return response_message.content or "The agent finished without a final message."

class AgentToolInput(BaseModel):
    task: str = Field(description="The specific task for the agent to perform.")

def create_tenx_agent_tool(agent: TenxAgent, name: str, description: str) -> Tool:
    """Wraps an Agent to be used as a Tool by another Agent."""
    class AgentAsTool(Tool):
        name = name
        description = description
        args_schema = AgentToolInput

        def execute(self, task: str) -> str:
            return agent.run(task)
            
    return AgentAsTool()