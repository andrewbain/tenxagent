#!/usr/bin/env python3
"""
Test script to verify that create_tenx_agent_tool works properly.
"""

import asyncio
import os
from tenxagent import TenxAgent, OpenAIModel, Tool, safe_evaluate
from tenxagent.agent import create_tenx_agent_tool
from pydantic import BaseModel, Field

# Simple calculator tool
class CalculatorInput(BaseModel):
    expression: str = Field(description="Mathematical expression to evaluate")

class CalculatorTool(Tool):
    name = "calculator"
    description = "Evaluates mathematical expressions safely"
    args_schema = CalculatorInput
    
    def execute(self, expression: str, metadata: dict = None) -> str:
        try:
            result = safe_evaluate(expression)
            return f"Result: {result}"
        except Exception as e:
            return f"Error: {str(e)}"

async def test_agent_as_tool():
    """Test creating an agent and using it as a tool."""
    
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: OPENAI_API_KEY not found. Skipping test.")
        return
    
    print("🧪 Testing Agent as Tool...")
    
    # Create a math agent
    llm = OpenAIModel(model="gpt-4o-mini", temperature=0.1)
    calculator = CalculatorTool()
    
    math_agent = TenxAgent(
        llm=llm,
        tools=[calculator],
        system_prompt="You are a math assistant. Use the calculator for calculations.",
        max_llm_calls=5,
        max_tokens=2000
    )
    
    # Create an agent tool from the math agent
    try:
        math_tool = create_tenx_agent_tool(
            agent=math_agent,
            name="math_assistant",
            description="A specialized math assistant that can perform calculations"
        )
        
        print(f"✅ Agent tool created successfully!")
        print(f"   Name: {math_tool.name}")
        print(f"   Description: {math_tool.description}")
        
        # Test using the agent tool
        print("\n🔧 Testing tool execution...")
        result = math_tool.execute("What is 15 * 23 + 100?")
        print(f"✅ Tool result: {result}")
        
    except Exception as e:
        print(f"❌ Error creating agent tool: {e}")
        import traceback
        traceback.print_exc()

async def test_nested_agents():
    """Test using an agent tool within another agent."""
    
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: OPENAI_API_KEY not found. Skipping nested test.")
        return
    
    print("\n🧪 Testing Nested Agents...")
    
    # Create a math specialist agent
    llm = OpenAIModel(model="gpt-4o-mini", temperature=0.1)
    calculator = CalculatorTool()
    
    math_agent = TenxAgent(
        llm=llm,
        tools=[calculator],
        system_prompt="You are a specialized math calculator. Always use the calculator tool for any arithmetic.",
        max_llm_calls=3,
        max_tokens=1000
    )
    
    # Create a tool from the math agent
    math_tool = create_tenx_agent_tool(
        agent=math_agent,
        name="math_specialist",
        description="A math specialist that can handle complex calculations"
    )
    
    # Create a main agent that uses the math tool
    main_agent = TenxAgent(
        llm=llm,
        tools=[math_tool],
        system_prompt="You are a helpful assistant. Use the math specialist for any mathematical questions.",
        max_llm_calls=5,
        max_tokens=2000
    )
    
    try:
        print("🔧 Testing nested agent execution...")
        result = await main_agent.run(
            "I need to calculate the area of a rectangle that is 25.5 meters by 18.3 meters",
            session_id="nested_test"
        )
        print(f"✅ Nested agent result: {result}")
        
    except Exception as e:
        print(f"❌ Error in nested agents: {e}")
        import traceback
        traceback.print_exc()

async def main():
    print("🚀 Testing Agent as Tool Functionality")
    print("=" * 50)
    
    await test_agent_as_tool()
    await test_nested_agents()
    
    print("\n✅ All tests completed!")

if __name__ == "__main__":
    asyncio.run(main()) 