# Quantum Chatbot MCP Agent

This project implements a chatbot agent that interacts with a Quantum Computing MCP (Model Control Protocol) server using an LLM via a local OpenAI-compatible API endpoint.

## Prerequisites

1.  **Python:** Ensure you have Python 3.10 or later installed.
2.  **uv:** Install the `uv` package manager. It's recommended for faster dependency management, although `pip` within the virtual environments will also work.
    ```bash
    # Recommended installation (macOS/Linux)
    curl -LsSf https://astral.sh/uv/install.sh | sh
    # Or using pip (if you prefer)
    # pip install uv
    ```
3.  **Local OpenAI-compatible Server:** Ensure you have a local server running that provides an OpenAI-compatible API (like Ollama, vLLM, LM Studio, etc.).

## Setup

You can set up the necessary virtual environments and install dependencies using the provided script or manually.

**Option 1: Using the Setup Script (Recommended)**

1.  Make the script executable (Linux/macOS):
    ```bash
    chmod +x setup.sh
    ```
2.  Run the script:
    ```bash
    ./setup.sh
    ```
    This will create `.venv` directories inside both `agent` and `server` folders and install their respective requirements.

**Option 2: Manual Setup**

1.  **Create Agent Environment:**
    ```bash
    cd agent
    python3 -m venv .venv
    source .venv/bin/activate # On Windows use `.venv\Scripts\activate`
    pip install -r requirements.txt
    deactivate
    cd ..
    ```
2.  **Create Server Environment:**
    ```bash
    cd server
    python3 -m venv .venv
    source .venv/bin/activate # On Windows use `.venv\Scripts\activate`
    pip install -r requirements.txt
    deactivate
    cd ..
    ```

## Configuration

1.  **Configure LLM Endpoint:** Open `agent/agent.py` and modify the `client` initialization to point to your local OpenAI-compatible server's base URL and provide an API key if required (often a placeholder is fine for local servers).

    ```python
    # In agent/agent.py
    client = AsyncOpenAI(
        base_url="http://127.0.0.1:1234/v1/", # <-- CHANGE THIS TO YOUR SERVER URL
        api_key="not-needed", # <-- CHANGE THIS IF YOUR SERVER NEEDS A KEY
    )
    ```

2.  **(Optional) Configure Model ID:** You can also change the `MODEL_ID` variable in `agent/agent.py` if you want to use a different model served by your endpoint.

    ```python
    # In agent/agent.py
    MODEL_ID = "your-model-name" # <-- CHANGE THIS TO YOUR MODEL ID
    ```

## Running the Agent

1.  **Navigate to Agent Directory:**
    ```bash
    cd agent
    ```
2.  **Activate Agent Environment:**
    ```bash
    source .venv/bin/activate # On Windows use `.venv\Scripts\activate`
    ```
3.  **Run the Agent:**
    ```bash
    python agent.py
    ```
4.  **Interact:** Follow the prompts in the terminal to interact with the Quantum Chatbot. Use `Ctrl-C` to exit.