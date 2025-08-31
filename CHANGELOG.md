# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **Structured Output Support**: Added Pydantic model support for structured agent responses
  - New `output_model` parameter in `TenxAgent` constructor accepts any Pydantic model class
  - Automatic JSON schema injection into system prompts for structured output guidance
  - Response validation and parsing against the specified Pydantic model
  - Returns actual Pydantic model instances instead of raw strings when `output_model` is specified
  - Graceful error handling for invalid response formats with descriptive error messages
  - Backward compatible - regular string responses when no output model is specified

### Changed
- **Agent Return Type**: Updated `TenxAgent.run()` return type to `Union[str, BaseModel]`
  - Returns Pydantic model instance when `output_model` is specified
  - Returns string when no output model is provided (backward compatible)

### Added
- **Comprehensive Token Tracking**: Complete token usage monitoring across all LLM calls
  - Tracks `total_tokens`, `prompt_tokens`, and `completion_tokens` for main agent and nested agent-as-tool calls
  - Automatic propagation of token usage from nested agents back to parent agents
  - Auto-population of token fields in response models when present
  - Metadata-based token accumulation system for accurate cross-agent tracking

- **Simplified History Management**: Clean and intuitive history handling
  - Agent manages its own internal history automatically (no configuration needed)
  - Optional `history` parameter in `run()` method to provide custom message history
  - When `history` is provided, agent uses it without storing anything internally
  - When `history` is not provided, agent uses its internal `InMemoryHistoryStore`
  - Simple `List[Message]` format for all history - standard LLM message format
  - No complex configuration or schema conversion needed

### Improved
- **System Prompt Generation**: Enhanced structured output instructions for better LLM comprehension
  - Clear field-by-field descriptions with type information and constraints
  - Special handling for enum types with explicit valid values
  - Realistic example generation with proper enum values
  - Stricter formatting rules to ensure JSON-only responses
  - Better error prevention for complex Pydantic models

### Fixed
- **Message Safety**: Improved robustness when handling messages with optional tool_calls
  - Safe access using `getattr()` and `or []` patterns to prevent AttributeError
  - Graceful handling of messages that may not have tool_calls attribute
  - Backward compatibility with different message formats

### Changed
- **Agent Interface**: Dramatically simplified history management
  - Removed complex `history_store` parameter from agent constructor
  - Added simple optional `history` parameter to `run()` method for custom message lists
  - `session_id` parameter now defaults to "default" for even simpler usage
  - Agent automatically manages internal history when no custom history provided
  
- **History Architecture**: Removed all complexity
  - Eliminated flexible history stores, schemas, and conversion logic
  - Single `InMemoryHistoryStore` class for internal use only
  - No more abstract base classes or generic types
  - Simple, direct approach with standard `Message` objects only

## [0.1.2] - 2024-01-01

### Fixed
- **Agent-as-Tool Functionality**: Fixed `create_tenx_agent_tool()` function that was failing with attribute assignment errors
  - Resolved `name = name` class attribute assignment issue in nested class definition
  - Simplified async execution handling for better reliability
  - Added proper metadata parameter support to agent tool execution
  - Improved thread-based execution for nested async contexts
  - Reduced complexity by 90% while maintaining full functionality

- **Tool Signature Compatibility**: Updated all tool examples to include required `metadata` parameter
  - Fixed `CalculatorTool` and other example tools to match new signature requirements
  - Added safe evaluation using `safe_evaluate()` instead of `eval()` for security

### Changed
- **Simplified Architecture**: Streamlined agent-as-tool implementation
  - Removed complex event loop management and nested async handling
  - Implemented simple thread-based approach for async execution conflicts
  - Removed `nest-asyncio` dependency for cleaner dependencies

## [0.1.1] - 2024-01-01

### Added
- **Comprehensive Metadata System**: Added full metadata support throughout the agent pipeline
  - Metadata flows from agent calls through to LLM APIs and tool executions
  - OpenAI-specific metadata parameters supported (`user`, `seed`, `response_format`, `stream`)
  - Tools can access and use metadata for context-aware execution
  - Role-based access control and logging capabilities via metadata

- **Flexible Model System**: Complete overhaul of the language model architecture
  - Abstract `LanguageModel` base class with standardized interface
  - `supports_native_tool_calling()` method to distinguish model capabilities
  - `convert_tools_to_model_format()` for model-specific tool conversion
  - `get_tool_calling_system_prompt()` for model-specific instructions
  - `ManualToolCallingModel` wrapper for models without native function calling

- **Enhanced OpenAI Integration**
  - Native function calling support with proper tool call parsing
  - Async `AsyncOpenAI` client usage
  - Proper handling of tool call responses and message formatting
  - Support for OpenAI-specific API parameters via metadata

- **Environment Variables Support**
  - Added `python-dotenv` integration for secure API key management
  - Automatic loading of `.env` files
  - Support for `OPENAI_API_KEY`, `OPENAI_ORG_ID`, and `OPENAI_BASE_URL`

- **Safe Expression Evaluation**
  - `safe_evaluate()` function using AST parsing instead of `eval()`
  - Protection against code injection and unsafe operations
  - Support for basic mathematical operations only

- **Comprehensive Examples**
  - `examples/flexible_models.py`: Demonstrates different model types
  - `examples/metadata_usage.py`: Shows metadata usage patterns
  - `examples/basic_usage.py`: Updated with async support and metadata
  - Debug utilities for troubleshooting agent behavior

### Changed
- **Agent Architecture**: Completely refactored for async operation and metadata support
  - `TenxAgent.run()` now async and accepts optional metadata parameter
  - Renamed `max_tool_calls` to `max_llm_calls` for clarity
  - Tools receive metadata in `execute()` method signature
  - System prompt generation delegated to language models

- **Tool Interface**: Updated for metadata support and consistency
  - All tool `execute()` methods now include `metadata: Dict[str, Any] = None` parameter
  - Abstract `Tool` class updated with new signature requirements
  - Better error handling and validation in tool execution

- **Message Schema**: Enhanced to support modern tool calling patterns
  - Added `tool_calls` field for multiple parallel tool calls
  - Added `tool_call_id` for proper tool response tracking
  - Made `content` optional to support tool-only messages

- **History Management**: Improved session-based conversation handling
  - Automatic system message insertion for new sessions
  - Better message persistence and retrieval
  - Support for tool messages in conversation history

### Fixed
- **Tool Call Parsing**: Resolved issues with OpenAI function calling format
  - Proper conversion between OpenAI tool call format and internal representation
  - Fixed message content handling for tool call requests
  - Eliminated "null content" errors in OpenAI API calls

- **Import Issues**: Fixed all relative import problems
  - Consistent use of relative imports throughout the package
  - Proper module structure and `__init__.py` exports
  - Added missing type imports and dependencies

- **Test Suite**: Updated all tests for new async interface and metadata support
  - Added `pytest-asyncio` support
  - Updated mock objects to match new signatures
  - Fixed tool call test data format

### Dependencies
- Added `python-dotenv` for environment variable management
- Added `pytest-asyncio` for async test support
- Updated OpenAI client usage to async patterns

### Migration Guide
For users upgrading from previous versions:

1. **Update tool signatures**:
   ```python
   # Before
   def execute(self, param: str) -> str:
   
   # After  
   def execute(self, param: str, metadata: dict = None) -> str:
   ```

2. **Update agent calls**:
   ```python
   # Before
   result = agent.run("query")
   
   # After
   result = await agent.run("query", session_id="session_1")
   # With metadata
   result = await agent.run("query", session_id="session_1", metadata={"user": "user123"})
   ```

3. **Add async/await**:
   ```python
   # Before
   def main():
       agent = TenxAgent(llm, tools)
       result = agent.run("query")
   
   # After
   async def main():
       agent = TenxAgent(llm, tools)
       result = await agent.run("query", session_id="session_1")
   
   if __name__ == "__main__":
       asyncio.run(main())
   ```

4. **Using structured output (new in v0.1.3)**:
   ```python
   from pydantic import BaseModel, Field
   
   class OutputModel(BaseModel):
       answer: str = Field(description="The main answer")
       confidence: float = Field(description="Confidence score 0-1")
   
   # Create agent with structured output
   agent = TenxAgent(llm=llm, tools=tools, output_model=OutputModel)
   
   # Returns Pydantic model instance
   result = await agent.run("query", session_id="session_1")
   print(f"Answer: {result.answer}, Confidence: {result.confidence}")
   ```

5. **Using custom history (new in v0.1.3)**:
   ```python
   from tenxagent import Message
   
   # Option 1: Let agent manage history automatically
   agent = TenxAgent(llm=llm, tools=tools)
   result = await agent.run("Hello", session_id="session_1")  # Remembers context
   result = await agent.run("What did I just say?", session_id="session_1")  # Uses history
   
   # Option 2: Provide your own history messages
   my_history = [
       Message(role="user", content="Hello"),
       Message(role="assistant", content="Hi there! How can I help?"),
       Message(role="user", content="What's 2+2?"),
       Message(role="assistant", content="2+2 equals 4.")
   ]
   
   # Agent uses provided history without storing anything
   result = await agent.run("What was my math question?", history=my_history)
   ```


## [0.1.0] - Initial Release

### Added
- Basic agent framework with tool calling support
- OpenAI integration
- Simple tool interface
- In-memory history storage
- Basic examples and tests

---

## Release Notes

### v0.1.3 - Structured Output & Simplified History  
This release adds powerful structured output capabilities and dramatically simplifies history management:

- 🎯 **New**: Pydantic model support for structured agent responses
- 🎯 **New**: Automatic JSON schema generation and validation  
- 🎯 **New**: Returns actual Pydantic model instances for easy data handling
- 🎯 **New**: Comprehensive token tracking across all LLM calls (including nested agents)
- ✨ **Simplified**: Removed all complex history store architecture
- ✨ **Simplified**: Agent manages its own internal history automatically
- 🎯 **New**: Optional `history` parameter to provide custom message lists
- 🎯 **New**: Simple `List[Message]` format for all history operations
- ✨ **Enhanced**: Improved system prompt generation for better structured output reliability
- ✨ **Enhanced**: Special enum handling and clearer field descriptions for LLMs  
- ✨ **Simplified**: No more abstract base classes or generic types for history

### v0.1.2 - Bug Fixes & Simplification
This release focuses on fixing the agent-as-tool functionality and simplifying the codebase:

- ✅ **Fixed**: `create_tenx_agent_tool()` now works reliably without complex async handling
- ✅ **Simplified**: Reduced code complexity while maintaining all functionality  
- ✅ **Updated**: All examples now use proper tool signatures with metadata support
- ✅ **Secured**: Replaced `eval()` with `safe_evaluate()` in examples

### v0.1.1 - Major Feature Release
This release introduced the comprehensive metadata system and flexible model architecture:

- 🚀 **New**: Complete metadata pipeline from agent → LLM → tools
- 🚀 **New**: Flexible model system supporting different LLM providers
- 🚀 **New**: Enhanced OpenAI integration with native function calling
- 🚀 **New**: Environment variable support with `.env` files
- 🚀 **New**: Safe expression evaluation system 