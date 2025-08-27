#!/usr/bin/env python3
"""
Example demonstrating async TenxAgent usage with environment variables.

Before running this example:
1. Create a .env file with your OpenAI API key:
   OPENAI_API_KEY=your_api_key_here
   
2. Install dependencies:
   pip install -e .
   
3. Run the example:
   python examples/async_usage.py
"""

import asyncio
from tenxagent import TenxAgent, OpenAIModel, Tool, safe_evaluate
from pydantic import BaseModel, Field

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

async def main():
    """Example usage of the async TenxAgent."""
    
    # Initialize the language model (will load API key from .env automatically)
    llm = OpenAIModel(model="gpt-4o-mini", temperature=0.7)
    
    # Create tools
    calculator = CalculatorTool()
    
    # Create the agent
    agent = TenxAgent(
        llm=llm,
        tools=[calculator],
        system_prompt="You are a helpful math assistant. Use the calculator tool for any mathematical calculations.",
        max_llm_calls=10,
        max_tokens=4000
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
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
    
    print("\n✅ Demo completed!")

if __name__ == "__main__":
    asyncio.run(main()) 