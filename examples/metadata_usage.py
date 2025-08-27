#!/usr/bin/env python3
"""
Example demonstrating how to use metadata with TenxAgent.

This shows how metadata can be passed through the entire pipeline:
1. From the agent run call
2. Through to the LLM (for API-specific parameters)
3. Into tools (for context-aware execution)

Before running this example:
1. Create a .env file with your OpenAI API key:
   OPENAI_API_KEY=your_api_key_here
   
2. Install dependencies:
   pip install -e .
   
3. Run the example:
   python examples/metadata_usage.py
"""

import asyncio
import os
from tenxagent import TenxAgent, OpenAIModel, Tool, safe_evaluate
from pydantic import BaseModel, Field

# Example tool that uses metadata
class CalculatorInput(BaseModel):
    expression: str = Field(description="Mathematical expression to evaluate")

class MetadataAwareCalculatorTool(Tool):
    name = "calculator"
    description = "Evaluates mathematical expressions with metadata awareness"
    args_schema = CalculatorInput
    
    def execute(self, expression: str, metadata: dict = None) -> str:
        try:
            # Use metadata to customize behavior
            metadata = metadata or {}
            
            # Example: Use precision from metadata
            precision = metadata.get("precision", 2)
            
            # Example: Check if user has permission for certain operations
            user_role = metadata.get("user_role", "basic")
            
            if "**" in expression and user_role == "basic":
                return "Error: Power operations require elevated privileges"
            
            result = safe_evaluate(expression)
            
            # Format result based on metadata
            if isinstance(result, float):
                result = round(float(result), precision)
            
            # Include metadata context in response
            response = f"Result: {result}"
            if metadata.get("show_calculation", False):
                response += f" (calculated: {expression})"
            if metadata.get("user_id"):
                response += f" [calculated for user: {metadata['user_id']}]"
                
            return response
            
        except Exception as e:
            return f"Error: {str(e)}"

# Example tool that logs metadata
class LoggingInput(BaseModel):
    message: str = Field(default="", description="Optional message to log")

class LoggingTool(Tool):
    name = "logger"
    description = "Logs information with metadata context"
    args_schema = LoggingInput
    
    def execute(self, message: str = "", metadata: dict = None, **kwargs) -> str:
        metadata = metadata or {}
        
        log_entry = {
            "timestamp": metadata.get("timestamp", "unknown"),
            "user_id": metadata.get("user_id", "anonymous"),
            "session_id": metadata.get("session_id", "unknown"),
            "action": "tool_execution",
            "tool": self.name,
            "kwargs": kwargs
        }
        
        print(f"📋 Log Entry: {log_entry}")
        return f"Logged action with metadata: {list(metadata.keys())}"

async def demo_openai_metadata():
    """Demo using metadata with OpenAI API parameters."""
    print("🔧 Demo 1: OpenAI API Metadata")
    print("=" * 40)
    
    llm = OpenAIModel(model="gpt-4o-mini", temperature=0.1)
    calculator = MetadataAwareCalculatorTool()
    
    agent = TenxAgent(
        llm=llm,
        tools=[calculator],
        system_prompt="You are a helpful calculator assistant.",
        max_llm_calls=5,
        max_tokens=2000
    )
    
    # Metadata that will be passed to OpenAI API
    openai_metadata = {
        "user": "user123",  # OpenAI user tracking
        "seed": 42,         # For reproducible results
        "precision": 4,     # Custom metadata for our tool
        "show_calculation": True,
        "user_role": "admin"
    }
    
    query = "What's 25.123456 * 17.789?"
    print(f"Query: {query}")
    print(f"Metadata: {openai_metadata}")
    
    try:
        result = await agent.run(query, session_id="openai_demo", metadata=openai_metadata)
        print(f"Response: {result}")
    except Exception as e:
        print(f"❌ Error: {e}")

async def demo_tool_metadata():
    """Demo showing how tools can use metadata for different behaviors."""
    print("\n🔧 Demo 2: Tool Behavior Based on Metadata")
    print("=" * 50)
    
    llm = OpenAIModel(model="gpt-4o-mini", temperature=0.1)
    calculator = MetadataAwareCalculatorTool()
    
    agent = TenxAgent(
        llm=llm,
        tools=[calculator],
        system_prompt="You are a calculator. Use the calculator tool for math.",
        max_llm_calls=5,
        max_tokens=2000
    )
    
    # Test with basic user (should reject power operations)
    basic_metadata = {
        "user_id": "basic_user",
        "user_role": "basic",
        "precision": 2
    }
    
    print("Basic user trying power operation:")
    try:
        result = await agent.run("Calculate 2**10", session_id="basic_demo", metadata=basic_metadata)
        print(f"Response: {result}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test with admin user (should allow power operations)
    admin_metadata = {
        "user_id": "admin_user", 
        "user_role": "admin",
        "precision": 4,
        "show_calculation": True
    }
    
    print("\nAdmin user trying power operation:")
    try:
        result = await agent.run("Calculate 2**10", session_id="admin_demo", metadata=admin_metadata)
        print(f"Response: {result}")
    except Exception as e:
        print(f"❌ Error: {e}")

async def demo_logging_metadata():
    """Demo using metadata for logging and tracking."""
    print("\n🔧 Demo 3: Metadata for Logging and Tracking")
    print("=" * 50)
    
    llm = OpenAIModel(model="gpt-4o-mini", temperature=0.1)
    calculator = MetadataAwareCalculatorTool()
    logger = LoggingTool()
    
    agent = TenxAgent(
        llm=llm,
        tools=[calculator, logger],
        system_prompt="You are an assistant that can do math and logging.",
        max_llm_calls=5,
        max_tokens=2000
    )
    
    # Rich metadata for tracking
    tracking_metadata = {
        "user_id": "tracker_user",
        "session_id": "session_123",
        "timestamp": "2024-01-01T12:00:00Z",
        "request_id": "req_456",
        "client_ip": "192.168.1.1",
        "user_agent": "TenxAgent-Example/1.0",
        "precision": 3
    }
    
    query = "Calculate 15.5 * 23.7 and log this calculation"
    print(f"Query: {query}")
    
    try:
        result = await agent.run(query, session_id="tracking_demo", metadata=tracking_metadata)
        print(f"Response: {result}")
    except Exception as e:
        print(f"❌ Error: {e}")

async def main():
    """Run all metadata demos."""
    print("🚀 TenxAgent Metadata System Demo")
    print("=" * 60)
    
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  Error: OPENAI_API_KEY not found in environment variables.")
        print("Please create a .env file with your OpenAI API key.")
        return
    
    await demo_openai_metadata()
    await demo_tool_metadata()
    await demo_logging_metadata()
    
    print("\n✅ All metadata demos completed!")
    print("\n💡 Key Benefits of Metadata System:")
    print("- Pass API-specific parameters to LLM providers")
    print("- Customize tool behavior based on user context")
    print("- Enable logging, tracking, and audit trails")
    print("- Support role-based access control in tools")
    print("- Maintain context across the entire agent pipeline")

if __name__ == "__main__":
    asyncio.run(main()) 