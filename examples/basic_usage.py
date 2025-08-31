#!/usr/bin/env python3
"""
Example demonstrating async TenxAgent usage with environment variables.

Before running this example:
1. Create a .env file with your OpenAI API key:
   OPENAI_API_KEY=your_api_key_here
   
2. Install dependencies:
   pip install -e .
   
3. Run the example:
   python examples/basic_usage.py
"""

import asyncio
from tenxagent import TenxAgent, OpenAIModel, Tool, safe_evaluate
from pydantic import BaseModel, Field
from typing import List, Any
from enum import Enum

# Define a simple calculator tool
class CalculatorInput(BaseModel):
    expression: str = Field(description="Mathematical expression to evaluate (e.g., '2 + 3 * 4')")

class CalculatorTool(Tool):
    name = "calculator" 
    description = "Evaluates mathematical expressions safely"
    args_schema = CalculatorInput
    def execute(self, expression: str, metadata: dict = None) -> str:
        try:
            # Simple safe evaluation (only allow basic math)
            allowed_chars = set('0123456789+-*/().,e ')
            if not all(c in allowed_chars for c in expression):
                return "Error: Only basic mathematical operations are allowed"
            
            result = safe_evaluate(expression)
            return f"Result: {result}"
        except Exception as e:
            return f"Error: {str(e)}"

class ResponseType(str, Enum):
    text = "text"
    radio = "radio"
    checklist = "checklist"
    appointments = "appointments"
    personal_details = "personal_details"

class ChatResponse(BaseModel):
    type: ResponseType = Field(
        default=ResponseType.text, 
        description="Response type: 'text' for conversation, 'radio' for single choice, 'checklist' for multiple choice, 'appointments' for booking, 'personal_details' for forms"
    )
    message: str = Field(description="Main response message to display to the user")
    data: List[Any] = Field(default_factory=list, description="Additional data required by the response type (e.g., appointment slots, form fields, options)")
    tools_used: list[str] = Field(default_factory=list, description="List of tool names that were called to generate this response")
    user_id: str = Field(default="", description="ID of the user this response is intended for")
    total_tokens: int = Field(default=0, description="Total tokens used across all LLM calls")
    prompt_tokens: int = Field(default=0, description="Total prompt/input tokens used")
    completion_tokens: int = Field(default=0, description="Total completion/output tokens used")
    
    
async def main():
    """Example usage of the async TenxAgent."""
    
    # Initialize the language model (will load API key from .env automatically)
    llm = OpenAIModel(model="gpt-4o-mini", temperature=0.7)
    
    # Create tools
    calculator = CalculatorTool()
    
    # Create the agent (manages its own internal history automatically)
    agent = TenxAgent(
        llm=llm,
        tools=[calculator],
        system_prompt="You are a helpful math assistant. Use the calculator tool for any mathematical calculations.",
        max_llm_calls=10,
        max_tokens=4000,
        output_model=ChatResponse
    )
    
    # Example queries
    queries = [
        "What's 15 * 23 + 100?",
        "Calculate the result of (45 + 67) * 2.5",
        "What's the square root of 144? Use 144**0.5",
        "Hello! How are you today?",
        "What was my first question?"
    ]
    
    session_id = "demo_session"
    
    print("🤖 TenxAgent Async Demo")
    print("=" * 50)
    
    for i, query in enumerate(queries, 1):
        print(f"\n📝 Query {i}: {query}")
        print("-" * 30)
        
        try:
            # Run the agent asynchronously
            response = await agent.run(query, session_id=session_id)
            print(f"🤖 Response: {response}")
            
            # Display token usage if available
            if hasattr(response, 'total_tokens'):
                print(f"💰 Token Usage: {response.total_tokens} total ({response.prompt_tokens} prompt + {response.completion_tokens} completion)")
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
    
    print("\n✅ Demo completed!")

if __name__ == "__main__":
    asyncio.run(main()) 