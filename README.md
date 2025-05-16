# Quantum Chatbot MCP Agent

This project implements a chatbot agent that interacts with a Quantum Computing MCP (Model Control Protocol) server using an LLM via an OpenAI-compatible API endpoint.

## Prerequisites

1. **Python:** Ensure you have Python 3.10 or later installed.
2. **LLM Provider:** Choose either:
   - **Ollama:** Install from [ollama.ai](https://ollama.ai) and pull the model:
     ```bash
     ollama pull llama3.1
     ```
   - **Local OpenAI-compatible server:** Such as LM Studio, vLLM, or any other local server that provides an OpenAI-compatible API

## Setup

1. **Create and activate virtual environment:**
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate  # On Windows use `.venv\Scripts\activate`
    pip install -r requirements.txt
    ```

2. **Configure LLM Provider:**
   You can configure the LLM provider using environment variables
   ```bash
   # For Ollama
   export LLM_PROVIDER=ollama
   export LLM_MODEL_ID=llama3.1 # Change to whatever model you use
   
   # For local OpenAI-compatible servers (such as LM Studio)
   export LLM_PROVIDER=local
   export LLM_MODEL_ID=meta-llama-3.1-8b-instruct # Change to whatever model you use
   
   # Optionally, override the default port
   # For example, Ollama default port is 11434, LMStudio default port is 1234 
   export LLM_BASE_URL=http://localhost:YOUR_PORT/v1
   ```

## Running the Agent

1. **Start your LLM provider:**
   ```bash
   # For Ollama
   ollama serve
   
   # For local OpenAI-compatible servers
   # Start your server (e.g., LM Studio) and load your model
   ```

2. **Run the agent:**
   ```bash
   python agent.py
   ```

3. **Interact:** Follow the prompts in the terminal to interact with the Quantum Chatbot. Use `Ctrl-C` to exit.

## Available Commands

The agent supports the following quantum circuit operations:

- `create_circuit(num_qubits)`: Create a new circuit with 1-5 qubits
- `apply_gate(target_qubit, gate, angle)`: Apply a quantum gate to a specific qubit
- `show_circuit()`: Display the current circuit
- `show_state()`: Show the current quantum state
- `reset_circuit()`: Reset the circuit to initial state

Example usage:
```
Enter your prompt: create a 2-qubit circuit
Enter your prompt: apply a Hadamard gate to qubit 0
Enter your prompt: show the circuit state
```