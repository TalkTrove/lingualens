# LinguaLens (LSADA)

[![PyPI version](https://badge.fury.io/py/lingualens.svg)](https://badge.fury.io/py/lingualens)

LinguaLens (formerly LSADA - Language Services and Data Analysis) is a flexible Python framework for evaluating content quality using Large Language Models (LLMs).

It provides a structured way to:

*   Define evaluation tasks with specific metrics and weighting.
*   Use different LLM providers (currently OpenAI, Cloudverse supported).
*   Generate prompts tailored to your evaluation criteria.
*   Parse LLM responses to extract scores and justifications.
*   Aggregate results from multiple evaluations for robustness.

## Installation

You can install LinguaLens directly from PyPI:

```bash
pip install python-lingualens
```

## Quick Start Example

1.  **Set your LLM API Key:**
    Make sure you have your API key (e.g., for OpenAI) set as an environment variable:

    ```bash
    export OPENAI_API_KEY="your_api_key_here"
    # On Windows (Command Prompt)
    # set OPENAI_API_KEY=your_api_key_here
    # On Windows (PowerShell)
    # $env:OPENAI_API_KEY="your_api_key_here"
    ```

2.  **Run the basic usage script:**
    Navigate to the `examples` directory and run the script:

    ```bash
    cd examples
    python 1_basic_usage.py
    ```

    This script demonstrates:
    *   Initializing an OpenAI client.
    *   Initializing the `Evaluator` for a specific task (`conversation_evaluation`).
    *   Evaluating sample content.
    *   Printing the detailed results, including the overall score, individual metric scores, and justifications.

    ```python
    # examples/1_basic_usage.py (Simplified Snippet)
    import os
    import logging
    from lingualens import Evaluator, LLMManager

    logging.basicConfig(level=logging.INFO)

    api_key = os.getenv("OPENAI_API_KEY")
    task_type = "conversation_evaluation"
    content_to_evaluate = "... (your content here) ..."

    if not api_key:
        logging.error("OPENAI_API_KEY not set.")
    else:
        try:
            llm_client = LLMManager.initialize_client(vendor="openai", api_key=api_key)
            evaluator = Evaluator(task_type=task_type, include_justification=True)
            result = evaluator.evaluate(content=content_to_evaluate, llm_client=llm_client)

            print("\n----- Evaluation Results -----")
            print(f"Task Type: {result.get('metadata', {}).get('task_type')}")
            print(f"Total Weighted Score: {result.get('total_weighted_score')}")
            # ... (print detailed scores and justifications) ...

        except Exception as e:
            logging.error(f"An error occurred: {e}", exc_info=True)

    ```

## Core Components

*   **`Evaluator`**: The main class to orchestrate the evaluation.
*   **`LLMManager`**: Manages and initializes clients for different LLM vendors.
*   **`TaskManager`**: Handles task definitions, metrics, and can auto-identify tasks.
*   **`PromptGenerator`**: Creates detailed prompts for the LLM based on configuration.
*   **`LLMResponseParser`**: Extracts structured data from LLM responses.
*   **`MetricsCalculator`**: Aggregates scores and performs calculations.
*   **`ConfigManager`**: Loads configurations from pool