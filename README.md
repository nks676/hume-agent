# Quantum Chatbot MCP Agent

This project implements a chatbot agent that interacts with a Quantum Computing MCP (Model Control Protocol) server using a Llama model via a local OpenAI-compatible API endpoint. Forked from dmintrih's toy-ai-agents and toy-fxpayment-mcp-server repos.

## Prerequisites

1.  **Python:** Ensure you have Python 3.10 or later installed.
2.  **Virtual Environments:** You need two separate Python virtual environments:
    *   One for this `toy-ai-agents` project.
    *   One for the MCP server project (e.g., `toy-fxpayment-mcp-server`).
3.  **`uv`:** This project uses `uv` to run the MCP server script within its virtual environment. Install `uv` if you haven't already:
    ```bash
    pip install uv
    # or
    pipx install uv
    ```
4.  **Dependencies:** Install the required Python packages for both projects by navigating to their respective directories and running:
    ```bash
    # In toy-ai-agents directory
    python -m venv .venv # Or your preferred venv name
    source .venv/bin/activate
    pip install -r requirements.txt

    # In your MCP server directory (e.g., toy-fxpayment-mcp-server)
    python -m venv .venv # Or your preferred venv name
    source .venv/bin/activate
    pip install -r requirements.txt
    ```
5.  **Local OpenAI-compatible Server:** Ensure you have a local server running that provides an OpenAI-compatible API (like Ollama, vLLM, etc.) accessible at `http://127.0.0.1:1234/v1/`.
6.  **API Keys:** If your MCP server requires API keys (like the `FOREX_API_KEY` mentioned in the script), make sure they are set as environment variables before running the agent.

## Configuration

Before running the agent, you need to configure the paths in `llama_mcp_agent.py`:

1.  **Find `uv` path:** Determine the absolute path to your `uv` installation:
    ```bash
    which uv
    ```
    Copy the output path.

2.  **Update `llama_mcp_agent.py`:** Open the `llama_mcp_agent.py` file and modify the following variables within the `main` function to match your local setup:
    *   `mcp_server_launch_cmd`: Set this to the absolute path of `uv` you found in the previous step.
    *   `mcp_server_directory`: Set this to the absolute path of the directory containing your MCP server project (e.g., `/path/to/your/toy-fxpayment-mcp-server`).
    *   `mcp_server_script`: Set this to the name of the Python script that starts your MCP server (e.g., `test.py` or `fxpayment.py`).

    ```python
    async def main():
        # ... other code ...

        # --- UPDATE THESE VARIABLES ---
        mcp_server_launch_cmd = "/path/to/your/uv" # e.g., /Users/youruser/.local/bin/uv
        mcp_server_directory = "/path/to/your/mcp-server-project" # e.g., /Users/narensathishkumar/work/learnqc/MCP/toy-fxpayment-mcp-server
        mcp_server_script = "your_server_script.py" # e.g., test.py
        # --- END UPDATES ---

        # ... rest of the main function ...
    ```

## Running the Agent

1.  **Activate MCP Server Environment (Optional but Recommended):** While `uv` handles running the script in its environment, activating it first can be helpful for debugging or direct interaction with the server.
    ```bash
    cd /path/to/your/mcp-server-project
    source .venv/bin/activate # Activate the server's venv
    # You can optionally test the server script directly here
    # python your_server_script.py
    deactivate # Deactivate if you activated it
    cd /path/to/toy-ai-agents # Go back to the agent directory
    ```

2.  **Activate Agent Environment:** Navigate to the `toy-ai-agents` directory and activate its virtual environment:
    ```bash
    cd /path/to/toy-ai-agents
    source .venv/bin/activate
    ```

3.  **Set Environment Variables (if needed):**
    ```bash
    export FOREX_API_KEY='your_api_key_here' # Example
    ```

4.  **Run the Agent:** Execute the agent script:
    ```bash
    python llama_mcp_agent.py
    ```

5.  **Interact:** Follow the prompts in the terminal to interact with the Quantum Chatbot. Use `Ctrl-C` to exit.