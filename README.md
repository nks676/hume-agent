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
   Edit `config.py` to set your provider and model:
   ```python
   # Set your provider here: "ollama" or "local"
   PROVIDER = "ollama"  # or "local" for LM Studio and similar servers

   # You can override any settings there if needed
   # config["base_url"] = "http://localhost:8000/v1"
   # config["model_id"] = "your-model-name"
   # config["api_key"] = "your-api-key"
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