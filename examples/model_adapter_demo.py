"""
Model adapter demonstration script.

This example shows how to use different model backends with the unified adapter interface.
Usage:
  python examples/model_adapter_demo.py
"""

import os
import sys
from pathlib import Path
import argparse

# Ensure aigo package is in the path
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from aigo.models.base import ModelConfig, get_model_runner


def main():
    """Run the model adapter demo."""
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Model adapter demo")
    parser.add_argument(
        "--provider", default="ollama", choices=["ollama", "openai"],
        help="Model provider to use"
    )
    parser.add_argument("--model", default="deepseek-r1:8b", help="Model name to use")
    parser.add_argument("--stream", action="store_true", help="Stream the response")
    parser.add_argument("--api-key", help="API key for OpenAI")
    parser.add_argument("--api-base", help="API base URL")
    parser.add_argument("--prompt", help="Prompt to send to the model")
    
    args = parser.parse_args()
    
    # For OpenAI, try to get API key from environment if not provided
    if args.provider == "openai" and not args.api_key:
        args.api_key = os.environ.get("OPENAI_API_KEY")
        if not args.api_key:
            print("Error: OpenAI API key required. Provide via --api-key or OPENAI_API_KEY environment variable.")
            return 1
    
    print(f"Using {args.provider} provider with model {args.model}")
    
    # Create model configuration
    config = ModelConfig(
        provider=args.provider,
        model_name=args.model,
        api_key=args.api_key,
        api_base=args.api_base
    )
    
    try:
        # Get appropriate runner for the configuration
        runner = get_model_runner(config)
        print(f"Selected model runner: {runner.__class__.__name__}")
        
        # Load the model
        print("Loading model...")
        runner.load()
        
        # Get prompt from user if not provided
        prompt = args.prompt
        if not prompt:
            print("\nEnter your prompt (Ctrl+D to end):")
            prompt = sys.stdin.read().strip()
        
        # Generate or stream the response
        print("\nGenerating response...")
        if args.stream and hasattr(runner, "stream_generate"):
            print("\n--- Response ---")
            for chunk in runner.stream_generate(prompt):
                print(chunk, end="", flush=True)
            print("\n")
        else:
            response = runner.generate(prompt)
            print("\n--- Response ---")
            print(response)
        
        return 0
    
    except Exception as e:
        print(f"Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 