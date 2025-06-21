#!/usr/bin/env python
"""
Advanced AIgo Features Example

This example demonstrates the advanced features of AIgo, including:
1. Translation middleware for multilingual support
2. Model optimization for performance on limited hardware
3. Model coordination for collaborative reasoning and ensembling
"""

import logging
import sys
import os
import platform
import psutil

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

logger = logging.getLogger(__name__)

# Add parent directory to path for direct script execution
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from aigo.models import (
    ModelConfig, 
    get_model_runner,
    OptimizationConfig,
    optimize_model,
    get_recommended_config,
    get_coordinator
)
from aigo.adapters import (
    BaseTranslator,
    OfflineTranslator,
    ApiTranslator,
    TranslationMiddleware,
    create_translator
)


def get_system_info():
    """Get system information for optimization."""
    system_info = {
        "os": platform.system(),
        "processor": platform.processor(),
        "memory_mb": psutil.virtual_memory().total // (1024 * 1024)
    }
    
    logger.info(f"System info: {system_info}")
    return system_info


def demonstrate_translation():
    """Demonstrate the translation middleware."""
    logger.info("=== Translation Middleware Demo ===")
    
    # Create a translator (offline version for demo)
    translator = create_translator(type="offline")
    
    # Create translation middleware
    middleware = TranslationMiddleware(
        translator=translator,
        user_lang="es",  # Spanish user
        model_lang="en"  # English-primary model
    )
    
    # Example user input in Spanish
    user_input = "¿Cuáles son las ventajas de usar inteligencia artificial en medicina?"
    logger.info(f"Original user input: {user_input}")
    
    # Translate to model's language
    model_input = middleware.translate_to_model(user_input)
    logger.info(f"Translated for model: {model_input}")
    
    # Simulate model output in English
    model_output = "Artificial intelligence in medicine offers several advantages: 1) Improved diagnostic accuracy through pattern recognition in medical images, 2) Personalized treatment recommendations based on patient data, 3) Early disease detection through continuous monitoring, 4) Reduced healthcare costs and administrative burden, and 5) Enhanced drug discovery and development processes."
    
    # Translate back to user's language
    user_output = middleware.translate_from_model(model_output)
    logger.info(f"Translated for user: {user_output}")


def demonstrate_optimization():
    """Demonstrate model optimization features."""
    logger.info("\n=== Model Optimization Demo ===")
    
    # Get system information
    system_info = get_system_info()
    
    # Create model configuration for Ollama
    config = ModelConfig(
        provider="ollama",
        model_name="llama2:7b",
        device="auto"
    )
    
    # Get recommended optimization configuration based on system and model
    opt_config = get_recommended_config(
        model_name="llama2:7b",
        system_memory_mb=system_info["memory_mb"]
    )
    
    logger.info(f"Recommended optimization config: {opt_config}")
    
    # Load the model
    try:
        model = get_model_runner(config)
        model.load()
        
        # Apply optimizations
        optimized_model = optimize_model(model, opt_config)
        
        # Test the optimized model
        prompt = "Explain quantum computing in simple terms."
        response = optimized_model.generate(prompt, max_tokens=100)
        
        logger.info(f"Optimized model response: {response[:100]}...")
    except Exception as e:
        logger.error(f"Error in optimization demo: {e}")


def demonstrate_model_coordination():
    """Demonstrate model coordination features."""
    logger.info("\n=== Model Coordination Demo ===")
    
    # Get the model coordinator
    coordinator = get_coordinator()
    
    # Add multiple models
    models_to_add = [
        ("llama2", ModelConfig(provider="ollama", model_name="llama2:7b")),
        ("codellama", ModelConfig(provider="ollama", model_name="codellama:7b")),
    ]
    
    for name, config in models_to_add:
        try:
            coordinator.add_model(name, config)
        except Exception as e:
            logger.error(f"Failed to add model {name}: {e}")
    
    # Add adapters
    coordinator.add_adapter("llama2_chat", "chat", "llama2")
    coordinator.add_adapter("codellama_text", "text", "codellama")
    
    # Demonstrate collaborative reasoning
    try:
        problem = """
        Create a Python function that calculates the Fibonacci sequence up to n terms
        using an efficient algorithm.
        """
        
        solution = coordinator.collaborative_reasoning(
            problem=problem,
            model_names=["llama2", "codellama"],
            max_iterations=2
        )
        
        logger.info(f"Collaborative solution:\n{solution}")
    except Exception as e:
        logger.error(f"Error in collaborative reasoning demo: {e}")
    
    # Demonstrate model ensembling
    try:
        prompt = "What are the ethical considerations of autonomous vehicles?"
        
        ensemble_result = coordinator.ensemble_generate(
            model_names=["llama2", "codellama"],
            prompt=prompt,
            aggregation_method="longest",
            max_tokens=200
        )
        
        logger.info(f"Ensemble result:\n{ensemble_result[:200]}...")
    except Exception as e:
        logger.error(f"Error in ensemble demo: {e}")
    
    # Demonstrate pipeline
    try:
        initial_input = "Write a function to sort a list of integers."
        
        pipeline_stages = [
            {"type": "adapter", "name": "llama2_chat", "params": {}},
            {"type": "adapter", "name": "codellama_text", "params": {"max_tokens": 300}}
        ]
        
        pipeline_result = coordinator.pipeline(
            stages=pipeline_stages,
            initial_input=initial_input
        )
        
        logger.info(f"Pipeline result:\n{pipeline_result[:200]}...")
    except Exception as e:
        logger.error(f"Error in pipeline demo: {e}")


def main():
    """Run the advanced features demonstration."""
    logger.info("AIgo Advanced Features Demo")
    
    try:
        # Run demonstrations
        demonstrate_translation()
        demonstrate_optimization()
        demonstrate_model_coordination()
        
        logger.info("\nDemo completed successfully")
    except Exception as e:
        logger.error(f"Demo failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 