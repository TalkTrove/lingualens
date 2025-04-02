import os
import logging
# Assuming the package is installed or src is in PYTHONPATH
# If running directly from the repo root, adjust imports like:
# from src.evaluator import Evaluator
# from src.models import LLMManager
from lingualens import Evaluator, LLMManager # Use the package name defined in setup.py

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    """Basic usage example for the lingualens package"""

    # --- Configuration ---
    # Ensure your OpenAI API key is set as an environment variable
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        logging.error("Error: OPENAI_API_KEY environment variable not set.")
        return

    # Specify the task type (optional, can be auto-identified)
    # See src/pool/task_pool.json for available task types
    task_type = "conversation_evaluation" # Example task ty

    # Content to evaluate
    content_to_evaluate = """
    User: Hi, I'm having trouble with my account login.
    Agent: Hello! I can help with that. Could you please provide your username?
    User: My username is testuser123.
    Agent: Thank you. Let me check your account details. Okay, I see the issue. I've reset your password. Please check your email for instructions.
    User: Great, thank you!
    """

    # --- Initialization ---
    try:
        # 1. Initialize the LLM Client (e.g., OpenAI)
        # You can specify the model, vendor, etc.
        llm_client = LLMManager.initialize_client(
            vendor="openai",
            api_key=api_key,
            model_name="gpt-3.5-turbo" # Optional: Specify model if needed
        )

        # 2. Initialize the Evaluator
        # Specify the task type (or let it auto-detect)
        # Specify number of evaluations for robustness (default is 1)
        evaluator = Evaluator(
            task_type=task_type,
            num_evaluations=1, # Increase for more reliable scores
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
