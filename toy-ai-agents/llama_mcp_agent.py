from typing import Any, List
import json
#from dotenv import load_dotenv
import os
from openai import AsyncOpenAI
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import asyncio

MODEL_ID = "meta-llama-3.1-8b-instruct"

# System prompt that guides the LLM's behavior and capabilities
SYSTEM_PROMPT = """You are a friendly Quantum Chatbot assistant. Your primary goal is to help users interact with a quantum circuit simulator using the available tools.

**Your Main Task:**
Listen to the user's request and use the correct tool if their request involves:
*   Creating a new quantum circuit (`create_circuit`)
*   Applying a gate to a qubit (`apply_gate`)
*   Showing the circuit's structure (`show_circuit`)
*   Showing the circuit's quantum state (`show_state`)
*   Resetting the circuit (`reset_circuit`)

**Tool Usage Rules:**
1.  **Use Tools When Needed:** You MUST use the appropriate tool when the user's request directly corresponds to a tool's function listed above. If the request is conversational (e.g., "hello", "thank you") or doesn't clearly match a tool's purpose, respond naturally without forcing a tool call.
2.  **Automatic Display Awareness:** Remember, the system **automatically displays** the circuit state or structure right after you successfully use a tool that modifies or shows it (like `create_circuit`, `apply_gate`, `show_state`, `show_circuit`, `reset_circuit`). This happens *before* your final confirmation message.
3.  **Your Response After Tool Use:** Because the relevant information is shown automatically, your response following a tool call should be **very brief**:
    *   **DO:** Simply confirm the action was completed (e.g., "Okay, I've applied the H gate to qubit 0.", "Circuit created with 2 qubits.", "Done, the circuit is reset.").
    *   **DO:** Ask what the user wants to do next, if appropriate (e.g., "What would you like to do next?").
    *   **DO NOT:** Describe, repeat, or summarize the circuit state or structure information that was just automatically displayed by the system. Keep your confirmation minimal.
4.  **Handling Multiple Steps:** If the user asks for several actions in one message (e.g., "apply H then X to qubit 0, then show state"), try your best to identify and perform all the corresponding tool calls in the correct sequence.

**Available Tools:**
{tools}

**General Notes:**
- Always base your actions and responses on the latest tool results provided in the conversation history.
- Maintain a friendly and supportive tone.
"""

# Initialize the OpenAI API-compatible client
# Note: The base URL is set to a local server for testing purposes.
client = AsyncOpenAI(
    base_url="http://127.0.0.1:1234/v1/",
    api_key="1234567890",
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

        tools = await self.session.list_tools()
        _, tools_list = tools
        _, tools_list = tools_list
        return tools_list

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

    This function:
    1. Sends the user query to the LLM with context about available tools
    2. Processes the LLM's response, including any tool calls
    3. Returns the final response to the user

    Args:
        query: User's input question or command
        tools: Dictionary of available database tools and their schemas
        messages: List of messages to pass to the LLM, defaults to None
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
                ),  # Creates System prompt based on available MCP server tools
            },
        ]
        if messages is None
        else messages  # reuse existing messages if provided
    )
    # add user query to the messages list
    messages.append({"role": "user", "content": query})

    # Query LLM with the system prompt, user query, and available tools
    first_response = await client.chat.completions.create(
        model=MODEL_ID,
        messages=messages,
        tools=([t["schema"] for t in tools.values()] if len(tools) > 0 else None),
        max_tokens=4096,
        temperature=0,
    )
    # detect how the LLM call was completed:
    # tool_calls: if the LLM used a tool
    # stop: If the LLM generated a general response, e.g. "Hello, how can I help you today?"
    stop_reason = (
        "tool_calls"
        if first_response.choices[0].message.tool_calls is not None
        else first_response.choices[0].finish_reason
    )

    if stop_reason == "tool_calls":
        # Extract tool use details from response
        for tool_call in first_response.choices[0].message.tool_calls:
            arguments = (
                json.loads(tool_call.function.arguments)
                if isinstance(tool_call.function.arguments, str)
                else tool_call.function.arguments
            )
            # --- Added Print Statement ---
            # Print the tool name and arguments chosen by the LLM
            print(f"\n--- LLM decided to call tool: {tool_call.function.name} with args: {arguments} ---")
            # --- End Added Print Statement ---

            # Call the tool with the arguments using our callable initialized in the tools dict
            tool_result = await tools[tool_call.function.name]["callable"](**arguments)

            # Print the raw result received from the tool call directly
            print(f"\n{tool_result}")

            # Add the tool result to the messages list
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": tool_call.function.name,
                    "content": json.dumps(tool_result), # Send raw result back to LLM
                }
            )

        # Query LLM with the user query and the tool results
        new_response = await client.chat.completions.create(
            model=MODEL_ID,
            messages=messages,
        )

    elif stop_reason == "stop":
        # If the LLM stopped on its own, use the first response
        new_response = first_response

    else:
        raise ValueError(f"Unknown stop reason: {stop_reason}")

    # Add the LLM response to the messages list
    messages.append(
        {"role": "assistant", "content": new_response.choices[0].message.content}
    )

    # Return the LLM response and messages
    return new_response.choices[0].message.content, messages


async def main():
    """
    Main function that sets up the MCP server, initializes tools, and runs the interactive loop.
    The server is run in a Docker container to ensure isolation and consistency.
    """

    mcp_server_launch_cmd = "/Users/narensathishkumar/.local/bin/uv"
    mcp_server_directory = "/Users/narensathishkumar/work/learnqc/hume-agent/toy-fxpayment-mcp-server"
    mcp_server_script = "test.py"

    # mcp_server_launch_cmd = input("\nEnter the absolute path where 'uv' is installed: \n")
    # mcp_server_directory = input("\nEnter the absolute path where your MCP server resides: \n")
    # mcp_server_script = input("\nEnter your MCP server script: \n")

    server_params = StdioServerParameters(
        command=mcp_server_launch_cmd,
        args=[
            "--directory",
            mcp_server_directory,
            "run",
            mcp_server_script,
        ],
        #args=mcp_server_launch_args.split(),
        env={
            "FOREX_API_KEY": os.environ["FOREX_API_KEY"],
        }
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