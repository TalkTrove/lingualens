from setuptools import setup, find_packages
import os

# Read the contents of README.md
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="python-lingualens", # Distribution name on PyPI
    version="1.0.2",
    packages=find_packages(),
    package_dir={"": "."},
    package_data={
        "lingualens": ["pool/*.json"], # Include JSON files within the lingualens/pool directory
    },
    include_package_data=True,
    install_requires=[
        "openai>=1.0.0", # Core LLM client
        "requests>=2.25.0", # For Cloudverse client and potentially others
        "numpy>=1.21.0", # For metrics calculations (std dev, median, etc.)
        "python-dotenv>=0.19.0", # For loading API keys from .env
        # "pydantic>=2.0.0", # Not directly used in core logic reviewed, consider adding if models use it
        "typing-extensions>=4.0.0", # Often needed for modern type hints
        # Optional dependencies below - consider moving to extras_require if not core
        # "anthropic>=0.3.0",
        # "flask>=2.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "black>=22.0.0",
            "isort>=5.0.0",
            "mypy>=0.900",
            "flake8>=4.0.0",
            "pytest-cov>=3.0.0",
        ],
        "docs": [
            "sphinx>=4.0.0",
            "sphinx-rtd-theme>=1.0.0",
        ],
    },
    python_requires=">=3.8",
    author="Vishnu",
    author_email="mkpvishnu@gmail.com",
    description="A flexible evaluation framework for content using LLMs",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/TalkTrove/lingualens",
    project_urls={
        "Bug Tracker": "https://github.com/TalkTrove/lingualens/issues",
        "Documentation": "https://github.com/TalkTrove/lingualens/wiki",
        "Source Code": "https://github.com/TalkTrove/lingualens",
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Operating System :: OS Independent",
    ],
    keywords="llm, evaluation, content-analysis, machine-learning, nlp",
)
