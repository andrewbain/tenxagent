#!/usr/bin/env python3
"""
Test script to verify that tool calls work properly with the TenxAgent.
This requires a real OpenAI API key set in your .env file.
"""

import asyncio
import os
from tenxagent import TenxAgent, OpenAIModel, Tool
from pydantic import BaseModel, Field

# Simple calculator tool for testing
class CalculatorInput(BaseModel):
    expression: str = Field(description="Mathematical expression to evaluate (e.g., '2 + 3')")

class CalculatorTool(Tool):
    name = "calculator"
    description = "Evaluates simple mathematical expressions"
    args_schema = CalculatorInput
    
    def execute(self, expression: str) -> str:
        try:
            # Simple safe evaluation - only allow basic math
            allowed_chars = set('0123456789+-*/().,e ')
            if not all(c in allowed_chars for c in expression):
                return "Error: Only basic mathematical operations are allowed"
            
            result = eval(expression)
            return f"The result is: {result}"
        except Exception as e:
            return f"Error: {str(e)}"

async def test_tool_calls():
    """Test if the agent properly uses tool calls."""
    

    # Create the model and agent
    llm = OpenAIModel(model="gpt-4o-mini", temperature=0.1)
    calculator = CalculatorTool()
    
    agent = TenxAgent(
        llm=llm,
        tools=[calculator],
        system_prompt="You are a helpful assistant. When asked to do math, use the calculator tool to get accurate results.",
        max_llm_calls=5,
        max_tokens=2000
    )
    
    print("🧪 Testing TenxAgent Tool Calls")
    print("=" * 40)
    
    # Test cases
    test_cases = [
        "What is 15 * 23?",
        "Calculate 100 + 200 + 300",
        "What's 2.5 * 4.8?",
    ]
    
    for i, question in enumerate(test_cases, 1):
        print(f"\n📝 Test {i}: {question}")
        print("-" * 30)
        
        try:
            result = await agent.run(question, session_id=f"test_{i}")
            print(f"🤖 Agent Response: {result}")
            
            # Check if tool was likely used (look for calculator-like result)
            if "result is:" in result.lower() or any(op in result for op in ["=", "equals", "answer"]):
                print("✅ Tool call appears to have been used!")
            else:
                print("⚠️  Tool call may not have been used properly")
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")
    
    print("\n🏁 Test completed!")

if __name__ == "__main__":
    asyncio.run(test_tool_calls()) 