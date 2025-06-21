"""
Simple example showing how to use the AIgo model API directly.
"""
import sys
import os
from pathlib import Path

# Add project root to path for direct imports
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Import from aigo package
from aigo.models.base import ModelConfig, get_model_runner


def main():
    """Run a simple model generation example."""
    # Print information
    print("AIgo Simple Example")
    print("==================")
    print("This example shows how to use the AIgo API directly to run model inference.")
    print()
    
    # Set up model configuration
    provider = input("Enter model provider (default: ollama): ") or "ollama"
    model_name = input("Enter model name (default: deepseek-r1:8b): ") or "deepseek-r1:8b"
    
    # Check if we need API key
    api_key = None
    if provider.lower() == "openai":
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            api_key = input("Enter OpenAI API key: ")
            if not api_key:
                print("Error: OpenAI API key is required for OpenAI provider")
                return 1
    
    # Create model config
    config = ModelConfig(
        provider=provider,
        model_name=model_name,
        api_key=api_key
    )
    
    try:
        # Get model runner
        print(f"\nInitializing {provider} model {model_name}...")
        runner = get_model_runner(config)
        
        # Load model
        print("Loading model...")
        runner.load()
        print("Model loaded successfully!")
        
        # Get prompt from user
        print("\nEnter prompt (press Ctrl+D or Ctrl+Z when done):")
        prompt = sys.stdin.read().strip()
        
        if not prompt:
            print("Error: Empty prompt")
            return 1
            
        # Generate response
        print("\nGenerating response...")
        response = runner.generate(prompt)
        
        print("\n-------- Response --------")
        print(response)
        print("-------------------------")
        
        return 0
    
    except Exception as e:
        print(f"Error: {e}")
        return 1
        

if __name__ == "__main__":
    sys.exit(main()) 