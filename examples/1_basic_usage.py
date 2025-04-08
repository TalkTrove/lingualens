import os
import logging
from lingualens import Evaluator, LLMManager # Use the package name defined in setup.py
from dotenv import load_dotenv

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    """Basic usage example for the lingualens package"""
    
    # Load environment variables from .env file
    load_dotenv()

    # --- Configuration ---
    # Ensure your OpenAI API key is set as an environment variable
    api_key = "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"
    if not api_key:
        logging.error("Error: OPENAI_API_KEY environment variable not set.")
        return

    # Specify the task type (optional, can be auto-identified)
    # See src/pool/task_pool.json for available task types
    task_type = "code_generation" # Example task type

    # Content to evaluate
    content_to_evaluate = """
# Request: Generate a Python function to calculate the factorial of a number recursively.
# Include basic error handling for negative numbers.

def factorial_recursive(n):
  # Base case: factorial of 0 or 1 is 1
  if n == 0 or n == 1:
    return 1
  # Recursive step: n * factorial(n-1)
  elif n > 1:
    return n * factorial_recursive(n-1)
  # Error handling for negative numbers
  else:
    raise ValueError("Factorial is not defined for negative numbers")

# Example usage:
# print(factorial_recursive(5)) # Output: 120
# print(factorial_recursive(0)) # Output: 1
# try:
#   print(factorial_recursive(-2))
# except ValueError as e:
#   print(e) # Output: Factorial is not defined for negative numbers
"""

    # --- Initialization ---
    try:
        # 1. Initialize the LLM Client (e.g., OpenAI)
        # You can specify the model, vendor, etc.
        print("Initializing LLM client...")
        llm_client = LLMManager.initialize_client(
            vendor="openai",
            api_key=api_key,
            model_name="gpt-4o-mini" # Optional: Specify model if needed
        )

        # 2. Initialize the Evaluator
        # Specify the task type (or let it auto-detect)
        # Specify number of evaluations for robustness (default is 1)
        evaluator = Evaluator(
            task_type=task_type,
            num_evaluations=3, # Increase for more reliable scores (tests aggregation)
            include_justification=True # Get explanations for scores
        )

        # --- Evaluation ---
        logging.info(f"Starting evaluation for task: {evaluator.task_type}...")
        result = evaluator.evaluate(
            content=content_to_evaluate,
            llm_client=llm_client
        )

        # --- Results ---
        logging.info("Evaluation Complete.")
        print("\n----- Evaluation Results -----")

        # Print metadata
        metadata = result.get("metadata", {})
        print(f"Task Type: {metadata.get('task_type', 'N/A')}")
        print(f"Evaluations Performed: {metadata.get('num_evaluations', 'N/A')}")
        print(f"Timestamp: {metadata.get('timestamp', 'N/A')}")

        # Print overall score
        print(f"\nTotal Weighted Score: {result.get('total_weighted_score', 'N/A')}")

        # Print detailed scores and justifications
        print("\nDetailed Scores:")
        scores_data = result.get("Scores", {})
        for metric, data in scores_data.items():
            print(f"  Metric: {metric.upper()}")
            print(f"    Score (Median): {data.get('score', 'N/A'):.2f}")
            # print(f"    Raw Scores: {data.get('raw_scores', [])}") # Uncomment to see all raw scores
            # print(f"    Filtered Scores (Outliers Removed): {data.get('filtered_scores', [])}") # Uncomment for filtered scores
            print(f"    Normalized Score: {data.get('normalized_score', 'N/A'):.2f}")
            print(f"    Weight: {data.get('weight', 'N/A'):.2f}")
            print(f"    Weighted Score Contrib.: {data.get('weighted_score', 'N/A'):.2f}")
            if "justifications" in data and data["justifications"]:
                 print(f"    Justification(s):")
                 for i, just in enumerate(data.get('justifications', [])):
                    print(f"      Eval {i+1}: {just}")
            print("-" * 20)

    except ValueError as ve:
        logging.error(f"Configuration or Value Error: {ve}")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}", exc_info=True)

if __name__ == "__main__":
    main()
