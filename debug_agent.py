#!/usr/bin/env python3
"""
Debug script to help identify why too many LLM calls are happening.
This adds detailed logging to track each step of the agent execution.
"""

import asyncio
import os
from tenxagent import TenxAgent, OpenAIModel, Tool, safe_evaluate
from pydantic import BaseModel, Field

# Debug tool with logging
class CalculatorInput(BaseModel):
    expression: str = Field(description="Mathematical expression to evaluate")

class DebugCalculatorTool(Tool):
    name = "calculator"
    description = "Evaluates mathematical expressions safely"
    args_schema = CalculatorInput
    
    def execute(self, expression: str, metadata: dict = None) -> str:
        print(f"🔧 [TOOL] Calculator called with: expression='{expression}', metadata={metadata}")
        try:
            result = safe_evaluate(expression)
            response = f"Result: {result}"
            print(f"🔧 [TOOL] Calculator returning: '{response}'")
            return response
        except Exception as e:
            error_response = f"Error: {str(e)}"
            print(f"🔧 [TOOL] Calculator error: '{error_response}'")
            return error_response

async def debug_test():
    """Test with debug logging to see what's happening."""
    
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: OPENAI_API_KEY not found in environment variables.")
        return
    
    print("🐛 Starting debug test...")
    
    llm = OpenAIModel(model="gpt-4o-mini", temperature=0.1)
    calculator = DebugCalculatorTool()
    
    agent = TenxAgent(
        llm=llm,
        tools=[calculator],
        system_prompt="You are a helpful math assistant. Use the calculator tool for mathematical calculations.",
        max_llm_calls=5,  # Low limit to catch loops early
        max_tokens=2000
    )
    
    # Test cases that might cause issues
    test_cases = [
        {
            "query": "What is 5 + 3?",
            "metadata": None,
            "description": "Simple query without metadata"
        },
        {
            "query": "What is 10 * 20?", 
            "metadata": {"user_id": "test_user"},
            "description": "Simple query with basic metadata"
        },
        {
            "query": "Calculate 15 + 25",
            "metadata": {"user_id": "test_user", "precision": 2, "show_calculation": True},
            "description": "Query with complex metadata"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{'='*60}")
        print(f"🧪 Test {i}: {test_case['description']}")
        print(f"Query: {test_case['query']}")
        print(f"Metadata: {test_case['metadata']}")
        print("="*60)
        
        try:
            # Track LLM calls by wrapping the generate method
            original_generate = llm.generate
            call_count = 0
            
            async def debug_generate(messages, tools=None, metadata=None):
                nonlocal call_count
                call_count += 1
                print(f"🤖 [LLM] Call #{call_count}")
                print(f"    Messages count: {len(messages)}")
                print(f"    Last message: {messages[-1].role if messages else 'None'}")
                print(f"    Tools count: {len(tools) if tools else 0}")
                print(f"    Metadata: {metadata}")
                
                result = await original_generate(messages, tools, metadata)
                
                print(f"🤖 [LLM] Response:")
                print(f"    Content: {result.message.content[:100]}..." if result.message.content else "    Content: None")
                print(f"    Tool calls: {len(result.message.tool_calls) if result.message.tool_calls else 0}")
                if result.message.tool_calls:
                    for tc in result.message.tool_calls:
                        print(f"      - {tc.name}({tc.arguments})")
                
                return result
            
            # Temporarily replace the generate method
            llm.generate = debug_generate
            
            result = await agent.run(
                test_case["query"], 
                session_id=f"debug_session_{i}",
                metadata=test_case["metadata"]
            )
            
            # Restore original method
            llm.generate = original_generate
            
            print(f"\n✅ [RESULT] Final response: {result}")
            print(f"✅ [STATS] Total LLM calls: {call_count}")
            
        except Exception as e:
            print(f"\n❌ [ERROR] {str(e)}")
            print(f"❌ [STATS] LLM calls before error: {call_count}")
            
            # Restore original method even on error
            llm.generate = original_generate

async def main():
    await debug_test()
    
    print(f"\n{'='*60}")
    print("🐛 Debug Tips:")
    print("1. Check if tool calls are being parsed correctly")
    print("2. Look for repeated identical tool calls")
    print("3. Verify metadata isn't causing parsing issues")
    print("4. Check if the LLM is getting stuck in a loop")
    print("5. Make sure system prompt isn't conflicting with tool calls")

if __name__ == "__main__":
    asyncio.run(main()) 