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
pip install lingualens
```

Alternatively, for development, you can clone this repository and install it in editable mode:

```bash
git clone https://github.com/your-github-username/lingualens.git # Replace with your repo URL
cd lingualens
pip install -e .
pip install -r requirements.txt # Install dependencies
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
*   **`ConfigManager`**: Loads configurations from `src/pool/*.json`.

## Configuration

Evaluation behavior is driven by JSON configuration files located in `src/pool/`:

*   `task_pool.json`: Defines different evaluation tasks, their descriptions, system prompts, associated metrics, and the weight of each metric in the final score.
*   `metrics_pool.json`: Defines individual metrics, their descriptions, and scoring criteria (e.g., score ranges and what each score level means).

You can customize these files or add new tasks and metrics to tailor the evaluation to your specific needs.

## Publishing to PyPI

These instructions assume you have a PyPI account and have `twine` installed (`pip install twine`).

1.  **Update Version:**
    *   Increment the `__version__` variable in `src/__init__.py`.
    *   Optionally, update the version in `setup.cfg` as well if you use it for metadata.

2.  **Build the Package:**
    Make sure you have the latest build tools:
    ```bash
    pip install --upgrade build wheel
    ```
    Remove any old distribution files:
    ```bash
    rm -rf dist/ build/ src/*.egg-info
    ```
    Build the source distribution and wheel:
    ```bash
    python -m build
    ```

3.  **Check the Distribution (Optional but Recommended):**
    ```bash
    twine check dist/*
    ```

4.  **Upload to TestPyPI (Optional but Recommended):**
    First, upload to the Test Python Package Index to ensure everything works.
    ```bash
    twine upload --repository testpypi dist/*
    ```
    You will be prompted for your TestPyPI username and password.
    You can then try installing from TestPyPI:
    ```bash
    pip install --index-url https://test.pypi.org/simple/ --no-deps lingualens
    ```

5.  **Upload to PyPI (Live):**
    Once you are confident, upload to the official PyPI.
    ```bash
    twine upload dist/*
    ```
    You will be prompted for your PyPI username and password.

**Updating the Package:**

To publish a new version, simply repeat the steps above:

1.  Update the version number in `src/__init__.py` (and potentially `setup.cfg`).
2.  Re-build the package (`python -m build`).
3.  Upload the new distribution files (`twine upload dist/*`).
