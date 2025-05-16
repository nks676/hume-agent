# Default configurations for different LLM providers
CONFIGURATIONS = {
    "ollama": {
        "base_url": "http://localhost:11434/v1",
        "api_key": "not-needed",
        "model_id": "llama3.1"
    },
    "local": {  # For LM Studio and other local OpenAI-compatible servers
        "base_url": "http://localhost:1234/v1",
        "api_key": "not-needed",
        "model_id": "meta-llama-3.1-8b-instruct"
    }
}

# Set your provider here: "ollama" or "local"
PROVIDER = "ollama"

# Get the configuration for the selected provider
config = CONFIGURATIONS[PROVIDER].copy()

# You can override any settings here if needed
# config["base_url"] = "http://localhost:8000/v1"
# config["model_id"] = "your-model-name"
# config["api_key"] = "your-api-key" 