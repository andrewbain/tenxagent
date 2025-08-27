#!/usr/bin/env python3
"""
Example demonstrating the flexible model system in TenxAgent.

This shows how you can use different types of models:
1. OpenAI with native function calling
2. Any other model with manual tool calling via prompting

Before running this example:
1. Create a .env file with your OpenAI API key:
   OPENAI_API_KEY=your_api_key_here
   
2. Install dependencies:
   pip install -e .
   
3. Run the example:
   python examples/flexible_models.py
"""

import asyncio
from tenxagent import TenxAgent, OpenAIModel, ManualToolCallingModel, Tool, safe_evaluate
from pydantic import BaseModel, Field

# Define a simple calculator tool
class CalculatorInput(BaseModel):
    expression: str = Field(description="Mathematical expression to evaluate (e.g., '2 + 3 * 4')")

class CalculatorTool(Tool):
    name = "calculator" 
    description = "Evaluates mathematical expressions safely"
    args_schema = CalculatorInput
    
    def execute(self, expression: str) -> str:
        try:
            # Simple safe evaluation (only allow basic math)
            allowed_chars = set('0123456789+-*/().,e ')
            if not all(c in allowed_chars for c in expression):
                return "Error: Only basic mathematical operations are allowed"
            
            result = safe_evaluate(expression)
            return f"Result: {result}"
        except Exception as e:
            return f"Error: {str(e)}"

# Example of a simple model that just echoes back tool call requests
class EchoModel:
    """Simple model for demonstration - just echoes back what it receives."""
    
    async def generate(self, messages, tools=None):
        from tenxagent.schemas import Message, GenerationResult
        
        # Get the last user message
        user_messages = [m for m in messages if m.role == "user"]
        if user_messages:
            last_message = user_messages[-1].content
            
            # Simple logic: if it contains math, suggest a tool call
            if any(op in last_message for op in ['+', '-', '*', '/', 'calculate', 'math']):
                # Extract the expression (very simple extraction)
                expression = last_message
                for word in ['what is', 'calculate', 'compute', '?']:
                    expression = expression.replace(word, '').strip()
                
                response_content = f'{{"tool_calls": [{{"name": "calculator", "arguments": {{"expression": "{expression}"}}}}]}}'
            else:
                response_content = f"I understand you said: {last_message}"
            
            return GenerationResult(
                message=Message(role="assistant", content=response_content),
                input_tokens=50,
                output_tokens=20
            )
        
        return GenerationResult(
            message=Message(role="assistant", content="Hello!"),
            input_tokens=10,
            output_tokens=5
        )

async def demo_native_tool_calling():
    """Demo using OpenAI with native function calling."""
    print("🔧 Demo 1: OpenAI with Native Function Calling")
    print("=" * 50)
    
    # OpenAI model with native function calling
    llm = OpenAIModel(model="gpt-4o-mini", temperature=0.1)
    calculator = CalculatorTool()
    
    agent = TenxAgent(
        llm=llm,
        tools=[calculator],
        system_prompt="You are a math assistant. Use the calculator for any mathematical calculations.",
        max_llm_calls=5,
        max_tokens=2000
    )
    
    query = "What's 25 * 17?"
    print(f"Query: {query}")
    
    try:
        result = await agent.run(query, session_id="native_demo")
        print(f"Response: {result}")
        print(f"✅ Native tool calling: {llm.supports_native_tool_calling()}")
    except Exception as e:
        print(f"❌ Error: {e}")

async def demo_manual_tool_calling():
    """Demo using manual tool calling with prompting."""
    print("\n🔧 Demo 2: Manual Tool Calling via Prompting")
    print("=" * 50)
    
    # Create a manual tool calling model by wrapping the echo model
    echo_model = EchoModel()
    llm = ManualToolCallingModel(echo_model)
    calculator = CalculatorTool()
    
    agent = TenxAgent(
        llm=llm,
        tools=[calculator],
        system_prompt="You are a math assistant.",
        max_llm_calls=5,
        max_tokens=2000
    )
    
    query = "What's 15 + 27?"
    print(f"Query: {query}")
    
    try:
        result = await agent.run(query, session_id="manual_demo")
        print(f"Response: {result}")
        print(f"✅ Native tool calling: {llm.supports_native_tool_calling()}")
    except Exception as e:
        print(f"❌ Error: {e}")

async def show_system_prompts():
    """Show how different models generate different system prompts."""
    print("\n📝 Demo 3: Different System Prompts")
    print("=" * 40)
    
    calculator = CalculatorTool()
    tools = [calculator]
    
    # OpenAI model
    openai_model = OpenAIModel(model="gpt-4o-mini")
    openai_prompt = openai_model.get_tool_calling_system_prompt(
        tools=tools, 
        user_prompt="Be helpful and accurate."
    )
    
    print("OpenAI Model System Prompt:")
    print("-" * 30)
    print(openai_prompt)
    
    # Manual model
    echo_model = EchoModel()
    manual_model = ManualToolCallingModel(echo_model)
    manual_prompt = manual_model.get_tool_calling_system_prompt(
        tools=tools,
        user_prompt="Be helpful and accurate."
    )
    
    print("\nManual Tool Calling Model System Prompt:")
    print("-" * 30)
    print(manual_prompt)

async def main():
    """Run all demos."""
    print("🚀 TenxAgent Flexible Model System Demo")
    print("=" * 60)
    
    # Only run OpenAI demo if API key is available
    import os
    if os.getenv("OPENAI_API_KEY"):
        await demo_native_tool_calling()
    else:
        print("⚠️  Skipping OpenAI demo - no API key found")
    
    await demo_manual_tool_calling()
    await show_system_prompts()
    
    print("\n✅ All demos completed!")
    print("\n💡 Key Benefits:")
    print("- Easy to add support for new LLM providers")
    print("- Models can use native function calling OR manual prompting")
    print("- Agent code stays the same regardless of model type")
    print("- Each model handles its own tool call format and system prompts")

if __name__ == "__main__":
    asyncio.run(main()) 