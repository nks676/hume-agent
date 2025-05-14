# Quantum Chatbot MCP Agent

This project implements a chatbot agent that interacts with a Quantum Computing MCP (Model Control Protocol) server using an LLM via a local OpenAI-compatible API endpoint.

## Prerequisites

1. **Python:** Ensure you have Python 3.10 or later installed.
2. **Local OpenAI-compatible Server:** Ensure you have a local server running that provides an OpenAI-compatible API (like LM Studio, Ollama, vLLM, etc.).

## Setup

1. **Create and activate virtual environment:**
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate  # On Windows use `.venv\Scripts\activate`
    pip install -r requirements.txt
    ```

## Configuration

1. **Configure LLM Endpoint:** Open `agent.py` and modify the `client` initialization to point to your local OpenAI-compatible server's base URL and provide an API key if required (often a placeholder is fine for local servers).

    ```python
    # In agent.py
    client = AsyncOpenAI(
        base_url="http://127.0.0.1:1234/v1/", # <-- CHANGE THIS TO YOUR SERVER URL
        api_key="not-needed", # <-- CHANGE THIS IF YOUR SERVER NEEDS A KEY
    )
    ```

2. **(Optional) Configure Model ID:** You can also change the `MODEL_ID` variable in `agent.py` if you want to use a different model served by your endpoint.

    ```python
    # In agent.py
    MODEL_ID = "your-model-name" # <-- CHANGE THIS TO YOUR MODEL ID
    ```

## Running the Agent

1. **Ensure your OpenAI-compatible server is running** (e.g., LM Studio)
2. **Run the agent:**
    ```bash
    python agent.py
    ```
3. **Interact:** Follow the prompts in the terminal to interact with the Quantum Chatbot. Use `Ctrl-C` to exit.