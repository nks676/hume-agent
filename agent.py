from typing import Any, List
import json
#from dotenv import load_dotenv
import os
from openai import AsyncOpenAI
from mcp import ClientSession, StdioServerParameters, stdio_client
import asyncio
from config import config

# Get model ID from config
MODEL_ID = config["model_id"]

# System prompt that guides the LLM's behavior and capabilities
SYSTEM_PROMPT = """You are a Quantum Circuit assistant that ONLY uses tools to perform actions. Your responses should be minimal and focused on tool execution.

**Core Rules:**
1. ONLY use tools to perform actions - do not explain what you're doing
2. If you can't understand the request or need more information, ask for clarification
3. If parameters are incorrect or missing, ask for the correct parameters
4. Do not provide explanations of results - just execute the requested actions

**Available Tools:**
{tools}

**Response Guidelines:**
- For unclear requests: "Please provide a more specific command"
- For missing parameters: "Please specify [missing parameter]"
- For invalid parameters: "Invalid parameter. Please provide a valid [parameter]"
- For successful tool execution: No response needed
"""

# Initialize the OpenAI API-compatible client
client = AsyncOpenAI(
    base_url=config["base_url"],
    api_key=config["api_key"],
)

class MCPClient:
    """
    A client class for interacting with the MCP (Model Control Protocol) server.
    This class manages the connection and communication with the FX-Payment tool via MCP.
    """

    def __init__(self, server_params: StdioServerParameters):
        """Initialize the MCP client with server parameters"""
        self.server_params = server_params
        self.session = None
        self._client = None

    async def __aenter__(self):
        """Async context manager entry"""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.__aexit__(exc_type, exc_val, exc_tb)
        if self._client:
            await self._client.__aexit__(exc_type, exc_val, exc_tb)

    async def connect(self):
        """Establishes connection to MCP server"""
        self._client = stdio_client(self.server_params)
        self.read, self.write = await self._client.__aenter__()
        session = ClientSession(self.read, self.write)
        self.session = await session.__aenter__()
        await self.session.initialize()

    async def get_available_tools(self) -> List[Any]:
        """
        Retrieve a list of available tools from the MCP server.
        """
        if not self.session:
            raise RuntimeError("Not connected to MCP server")

        tools = (await self.session.list_tools()).tools
        # _, tools_list = tools
        # _, tools_list = tools_list
        # return tools_list
        return tools

    def call_tool(self, tool_name: str) -> Any:
        """
        Create a callable function for a specific tool.
        This allows us to execute database operations through the MCP server.

        Args:
            tool_name: The name of the tool to create a callable for

        Returns:
            A callable async function that executes the specified tool
        """
        if not self.session:
            raise RuntimeError("Not connected to MCP server")

        async def callable(*args, **kwargs):
            response = await self.session.call_tool(tool_name, arguments=kwargs)
            return response.content[0].text

        return callable


async def agent_loop(query: str, tools: dict, messages: List[dict] = None):
    """
    Main interaction loop that processes user queries using the LLM and available tools.
    Only executes tools and provides minimal responses for clarification needs.
    """
    messages = (
        [
            {
                "role": "system",
                "content": SYSTEM_PROMPT.format(
                    tools="\n- ".join(
                        [
                            f"{t['name']}: {t['schema']['function']['description']}"
                            for t in tools.values()
                        ]
                    )
                ),
            },
        ]
        if messages is None
        else messages
    )
    messages.append({"role": "user", "content": query})

    first_response = await client.chat.completions.create(
        model=MODEL_ID,
        messages=messages,
        tools=([t["schema"] for t in tools.values()] if len(tools) > 0 else None),
        max_tokens=4096,
        temperature=0,
    )

    stop_reason = (
        "tool_calls"
        if first_response.choices[0].message.tool_calls is not None
        else first_response.choices[0].finish_reason
    )

    if stop_reason == "tool_calls":
        for tool_call in first_response.choices[0].message.tool_calls:
            arguments = (
                json.loads(tool_call.function.arguments)
                if isinstance(tool_call.function.arguments, str)
                else tool_call.function.arguments
            )
            # Execute the tool and get the result
            tool_result = await tools[tool_call.function.name]["callable"](**arguments)
            
            # Add the tool result to the messages list
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": tool_call.function.name,
                    "content": json.dumps(tool_result),
                }
            )
            
            # Return the tool result directly instead of getting another response
            return tool_result, messages
            
    elif stop_reason == "stop":
        # If the LLM stopped without calling a tool, return its response
        response = first_response.choices[0].message.content
        messages.append({"role": "assistant", "content": response})
        return response, messages
    else:
        raise ValueError(f"Unknown stop reason: {stop_reason}")


async def main():
    """
    Main function that sets up the MCP server, initializes tools, and runs the interactive loop.
    The server is run in a Docker container to ensure isolation and consistency.
    """

    mcp_server_launch_cmd = "python"
    mcp_server_script = "server.py"


    server_params = StdioServerParameters(
        command=mcp_server_launch_cmd,
        args=[
            mcp_server_script,
        ]
    )

    # Start MCP client and create interactive session
    async with MCPClient(server_params) as mcp_client:
        # Get available database tools and prepare them for the LLM
        mcp_tools = await mcp_client.get_available_tools()
        # Convert MCP tools into a format the LLM can understand and use
        tools = {
            tool.name: {
                "name": tool.name,
                "callable": mcp_client.call_tool(
                    tool.name
                ),  # returns a callable function for the rpc call
                "schema": {
                    "type": "function",
                    "function": {
                        "name": tool.name,
                        "description": tool.description,
                        "parameters": tool.inputSchema,
                    },
                },
            }
            for tool in mcp_tools
        }

        # Start interactive prompt loop for user queries
        messages = None
        while True:
            try:
                # Get user input and check for exit commands
                user_input = input("\nEnter your prompt (or use Ctrl-C to exit): ")
                if user_input.lower() in ["quit", "exit", "q"]:
                    break

                # Process the prompt and run agent loop
                response, messages = await agent_loop(user_input, tools, messages)
                print("\nResponse:", response)
                # print("\nMessages:", messages)
            except KeyboardInterrupt:
                print("\nExiting...")
                break
            except Exception as e:
                print(f"\nError occurred: {e}")

if __name__ == "__main__":
    asyncio.run(main())