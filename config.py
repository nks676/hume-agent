import os
from typing import Dict, Any

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
        "model_id": "local-model"
    }
}

def get_config() -> Dict[str, Any]:
    """
    Get the current configuration based on environment variables or defaults.
    Environment variables take precedence over default configurations.
    
    Available providers:
    - ollama: For Ollama local models
    - local: For LM Studio and other local OpenAI-compatible servers
    """
    # Get the provider from environment variable or default to ollama
    provider = os.getenv("LLM_PROVIDER", "ollama").lower()
    
    # Get the base configuration for the selected provider
    config = CONFIGURATIONS.get(provider, CONFIGURATIONS["ollama"]).copy()
    
    # Override with environment variables if they exist
    # Only override base_url if explicitly set (otherwise use provider default)
    if os.getenv("LLM_BASE_URL"):
        config["base_url"] = os.getenv("LLM_BASE_URL")
    if os.getenv("LLM_API_KEY"):
        config["api_key"] = os.getenv("LLM_API_KEY")
    if os.getenv("LLM_MODEL_ID"):
        config["model_id"] = os.getenv("LLM_MODEL_ID")
    
    return config 