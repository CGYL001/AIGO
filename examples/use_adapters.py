"""
Model adapters usage example.

This example demonstrates how to use the different model adapters.
"""

import os
import sys
from pathlib import Path
import argparse

# Ensure aigo package is in the path
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from aigo.models.base import ModelConfig
from aigo.models.adapters import (
    TextGenerationAdapter,
    EmbeddingAdapter,
    ChatAdapter,
    create_adapter
)


def text_generation_example(provider, model_name, api_key=None, api_base=None):
    """Text generation example."""
    print("\n=== Text Generation Example ===")
    
    # Create model config
    config = ModelConfig(
        provider=provider,
        model_name=model_name,
        api_key=api_key,
        api_base=api_base
    )
    
    # Create adapter
    adapter = TextGenerationAdapter(config)
    
    # Get input from user
    prompt = input("Enter prompt for text generation: ")
    if not prompt:
        prompt = "Write a short poem about artificial intelligence."
        print(f"Using default prompt: {prompt}")
    
    # Generate text
    print("\nGenerating text...")
    try:
        response = adapter.process(prompt, temperature=0.7)
        print("\nResponse:")
        print(response)
    except Exception as e:
        print(f"Error: {e}")


def chat_example(provider, model_name, api_key=None, api_base=None):
    """Chat example."""
    print("\n=== Chat Example ===")
    
    # Create model config
    config = ModelConfig(
        provider=provider,
        model_name=model_name,
        api_key=api_key,
        api_base=api_base
    )
    
    # Create adapter
    adapter = ChatAdapter(config)
    
    # Create chat messages
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": input("Enter your message: ") or "Tell me a joke."}
    ]
    
    # Generate response
    print("\nGenerating response...")
    try:
        response = adapter.process(messages, temperature=0.7)
        print("\nResponse:")
        print(response)
    except Exception as e:
        print(f"Error: {e}")


def embedding_example(provider, model_name, api_key=None, api_base=None):
    """Embedding example."""
    print("\n=== Embedding Example ===")
    
    # Create model config
    config = ModelConfig(
        provider=provider,
        model_name=model_name,
        api_key=api_key,
        api_base=api_base
    )
    
    # Create adapter
    adapter = EmbeddingAdapter(config)
    
    # Get input from user
    text = input("Enter text for embedding: ")
    if not text:
        text = "This is a sample text for embedding."
        print(f"Using default text: {text}")
    
    # Generate embedding
    print("\nGenerating embedding...")
    try:
        embedding = adapter.process(text)
        print(f"\nEmbedding (first 5 dimensions): {embedding[:5]}...")
        print(f"Embedding dimensions: {len(embedding)}")
    except Exception as e:
        print(f"Error: {e}")


def streaming_example(provider, model_name, api_key=None, api_base=None):
    """Streaming example."""
    print("\n=== Streaming Example ===")
    
    # Create model config
    config = ModelConfig(
        provider=provider,
        model_name=model_name,
        api_key=api_key,
        api_base=api_base
    )
    
    # Create adapter
    adapter = TextGenerationAdapter(config)
    
    # Get input from user
    prompt = input("Enter prompt for streaming: ")
    if not prompt:
        prompt = "Write a short story about a robot learning to feel emotions."
        print(f"Using default prompt: {prompt}")
    
    # Stream response
    print("\nStreaming response:")
    try:
        for chunk in adapter.stream(prompt, temperature=0.7):
            print(chunk, end="", flush=True)
        print("\n")
    except NotImplementedError:
        print("Streaming not supported by this model.")
    except Exception as e:
        print(f"Error: {e}")


def main():
    """Run the adapter examples."""
    parser = argparse.ArgumentParser(description="Model adapter examples")
    parser.add_argument(
        "--provider", default="ollama", choices=["ollama", "openai"],
        help="Model provider to use"
    )
    parser.add_argument("--model", default="deepseek-r1:8b", help="Model name to use")
    parser.add_argument("--api-key", help="API key for OpenAI")
    parser.add_argument("--api-base", help="API base URL")
    parser.add_argument(
        "--example", default="all", 
        choices=["text", "chat", "embedding", "stream", "all"],
        help="Example to run"
    )
    
    args = parser.parse_args()
    
    # For OpenAI, try to get API key from environment if not provided
    if args.provider == "openai" and not args.api_key:
        args.api_key = os.environ.get("OPENAI_API_KEY")
        if not args.api_key:
            print("Error: OpenAI API key required. Provide via --api-key or OPENAI_API_KEY environment variable.")
            return 1
    
    print(f"Using {args.provider} provider with model {args.model}")
    
    try:
        # Run the selected example
        if args.example == "text" or args.example == "all":
            text_generation_example(args.provider, args.model, args.api_key, args.api_base)
            
        if args.example == "chat" or args.example == "all":
            chat_example(args.provider, args.model, args.api_key, args.api_base)
            
        if args.example == "embedding" or args.example == "all":
            # Only run embedding example for OpenAI
            if args.provider == "openai":
                embedding_example(args.provider, "text-embedding-3-small", args.api_key, args.api_base)
            else:
                print("\n=== Embedding Example ===")
                print("Skipping embedding example for non-OpenAI provider.")
            
        if args.example == "stream" or args.example == "all":
            streaming_example(args.provider, args.model, args.api_key, args.api_base)
            
        return 0
        
    except Exception as e:
        print(f"Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 