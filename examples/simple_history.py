#!/usr/bin/env python3
"""
Example demonstrating simple history usage with TenxAgent.

This example shows two approaches:
1. Using the agent's internal history management (automatic)
2. Providing your own history messages to the agent

Before running this example:
1. Create a .env file with your OpenAI API key:
   OPENAI_API_KEY=your_api_key_here
   
2. Install dependencies:
   pip install -e .
   
3. Run the example:
   python examples/simple_history.py
"""

import asyncio
from tenxagent import TenxAgent, OpenAIModel, Tool, Message, safe_evaluate
from pydantic import BaseModel, Field
from typing import List

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

# Simple response model
class SimpleResponse(BaseModel):
    message: str = Field(description="Main response message")
    total_tokens: int = Field(default=0, description="Total tokens used")

async def demo_internal_history():
    """Demonstrate using agent's internal history management."""
    print("🔄 DEMO 1: Internal History Management")
    print("=" * 50)
    
    # Initialize the language model
    llm = OpenAIModel(model="gpt-4o-mini", temperature=0.7)
    calculator = CalculatorTool()
    
    # Create agent - it will manage its own history automatically
    agent = TenxAgent(
        llm=llm,
        tools=[calculator],
        system_prompt="You are a helpful math assistant. Use the calculator tool for mathematical calculations.",
        max_llm_calls=10,
        max_tokens=4000,
        output_model=SimpleResponse
    )
    
    # Have a conversation - agent remembers context automatically
    queries = [
        "Calculate 15 * 23",
        "Add 100 to that result",
        "What was my original calculation?"
    ]
    
    session_id = "math_session"
    
    for i, query in enumerate(queries, 1):
        print(f"\n📝 Query {i}: {query}")
        print("-" * 30)
        
        response = await agent.run(query, session_id=session_id)
        print(f"🤖 Response: {response.message}")
        print(f"💰 Tokens: {response.total_tokens}")

async def demo_provided_history():
    """Demonstrate providing your own history messages."""
    print("\n\n🔄 DEMO 2: Provided History Messages")
    print("=" * 50)
    
    # Initialize the language model
    llm = OpenAIModel(model="gpt-4o-mini", temperature=0.7)
    calculator = CalculatorTool()
    
    # Create agent
    agent = TenxAgent(
        llm=llm,
        tools=[calculator],
        system_prompt="You are a helpful math assistant. Use the calculator tool for mathematical calculations.",
        max_llm_calls=10,
        max_tokens=4000,
        output_model=SimpleResponse
    )
    
    # Create your own conversation history
    my_history = [
        Message(role="user", content="Hello, I need help with math"),
        Message(role="assistant", content="Hello! I'm here to help you with mathematical calculations. What would you like me to calculate?"),
        Message(role="user", content="What is 25 * 17?"),
        Message(role="assistant", content="I calculated 25 * 17 and the result is 425.")
    ]
    
    print("📚 Using provided history with context:")
    for msg in my_history:
        role_icon = {"user": "👤", "assistant": "🤖", "tool": "🔧"}.get(msg.role, "❓")
        print(f"  {role_icon} {msg.role}: {msg.content[:60]}{'...' if len(msg.content) > 60 else ''}")
    
    # Now ask a follow-up question with the provided history
    print(f"\n📝 New Query: What was that result divided by 5?")
    print("-" * 30)
    
    response = await agent.run(
        "What was that result divided by 5?", 
        history=my_history  # Provide the history
    )
    print(f"🤖 Response: {response.message}")
    print(f"💰 Tokens: {response.total_tokens}")
    print("\n💡 Note: When providing history, the agent doesn't store anything - it just uses what you give it.")

async def main():
    """Run both demos."""
    print("🤖 TenxAgent Simple History Demo")
    print("=" * 60)
    
    await demo_internal_history()
    await demo_provided_history()
    
    print("\n✅ Demo completed!")

if __name__ == "__main__":
    asyncio.run(main()) 