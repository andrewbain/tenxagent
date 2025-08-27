# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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


## [0.1.0] - Initial Release

### Added
- Basic agent framework with tool calling support
- OpenAI integration
- Simple tool interface
- In-memory history storage
- Basic examples and tests 