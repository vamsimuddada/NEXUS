"""
NEXUS — setup.py
Makes the project pip-installable: pip install -e .
"""
from setuptools import setup, find_packages

setup(
    name="nexus-soc",
    version="0.4.0",
    description="Autonomous Cyber Warfare Simulation & Self-Evolving SOC Platform",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="NEXUS Research Team",
    python_requires=">=3.11",
    packages=find_packages(exclude=["tests*", "scripts*", "data*"]),
    install_requires=[
        "faker>=19.0.0",
        "python-dotenv>=1.0.0",
        "pydantic>=2.0.0",
        "rich>=13.0.0",
        "networkx>=3.1",
        "scikit-learn>=1.3.0",
        "numpy>=1.24.0",
        "stix2>=3.0.0",
        "anthropic>=0.25.0",
        "streamlit>=1.28.0",
        "plotly>=5.17.0",
        "pandas>=2.0.0",
    ],
    extras_require={
        "llm":    ["openai>=1.0.0", "langchain>=0.1.0"],
        "memory": ["chromadb>=0.4.0"],
        "dev":    ["pytest>=7.4.0"],
    },
    entry_points={
        "console_scripts": [
            "nexus=scripts.run_simulation:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Topic :: Security",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
    ],
)
