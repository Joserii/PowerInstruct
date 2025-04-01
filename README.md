# PowerInstruct: Power System Instruction Dataset Generation Tool

## Project Overview

PowerInstruct is an automated dataset generation tool for power system instructions, leveraging large language models (LLMs). The tool supports two primary generation methods:

1. **Seed Generation**: Utilizes LLMs like GPT-4 or Qwen to produce seed data in a standardized format.
2. **Code Generation**: Employs models such as Claude or o1 to generate transformation code based on seed data, facilitating batch data generation.

Key features include:
- Compatibility with various LLMs (GPT-4, Claude, Qwen, etc.)
- Batch data processing capabilities
- Real-time execution result display
- Export options in JSON/JSONL formats
- Visualization platform for data presentation

## Installation Guide

1. **Clone the Project Repository**
   ```bash
   git clone https://github.com/Joserii/PowerInstruct.git
   cd PowerInstruct
   ```

2. **Check and Switch to the `dev` Branch** (This step may be omitted in future releases)
   ```bash
   # Check the current branch
   git branch

   # Switch to the dev branch
   git checkout dev

   # If the dev branch does not exist locally, fetch and switch to it
   git checkout -b dev origin/dev

   # Ensure the code is up-to-date
   git pull origin dev
   ```

3. **Create and Activate a Virtual Environment**
   ```bash
   conda create -n powerinstruct python=3.10
   conda activate powerinstruct
   ```

4. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Configure Environment Variables** (Support for OpenAI, Anthropic, Qwen API Keys)
   *TODO: Add specific instructions for setting up API keys.*

## Quick Start

1. **Launch the Service**
   ```bash
   python run.py
   ```

2. **Access the Web Interface**
   - Open a browser and navigate to `http://localhost:5000`

3. **Usage Workflow**
   - Upload data files (supports JSON format)
   - Select the model to use (different models can be chosen for Seed Generation and Code Generation)
   - Execute seed data generation
   - Merge code generation templates
   - Execute code generation
   - Download the generated dataset (supports JSON/JSONL formats)

## Project Structure

```
powerinstruct/
├── app/                    # Backend services
│   ├── api/                # API routes
│   ├── core/               # Core business logic
│   ├── services/           # Service layer
│   └── utils/              # Utility functions
├── static/                 # Frontend interface
│   ├── css/                # Stylesheets
│   └── js/                 # JavaScript files
│   templates/              # HTML templates
├── data/                   # Data directory
│   ├── templates/          # Template files
│   └── uploads/            # Uploaded files
├── config/                 # Configuration files
├── tests/                  # Test cases
├── requirements.txt        # Project dependencies
└── README.md               # Project documentation
```

## Core Features

1. **File Handling**
   - Supports JSON file uploads
   - File format validation
   - Batch file processing

2. **Model Invocation**
   - Supports multiple LLMs
   - Model parameter configuration
   - Error retry mechanisms

3. **Data Generation**
   - Seed data generation
   - Code template generation
   - Batch data transformation

4. **Result Export**
   - JSON format export
   - JSONL format export
   - Instruction data extraction

## Configuration Details

1. **Model Configuration**
   ```python
   SUPPORT_MODELS = [
       "gpt-4",
       "claude-37",
       "qwen-max",
       "gemini-pro"
   ]
   ```

2. **Template Configuration**
   ```json
   {
       "prompt": "your_prompt_template",
       "codegen": "your_code_template"
   }
   ``` 