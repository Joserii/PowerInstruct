# PowerInstruct: Power System Instruction Dataset Generation Tool

## Project Overview

PowerInstruct is an automated dataset generation tool for power system instructions based on large language models. The tool supports two generation methods:

1. **Seed Generation**: First generate seed data in standard format using GPT4/Qwen and other large models.
2. **Code Generation**: Use models like Claude/o1 to generate conversion code based on seed data for batch data generation.

Key features:
- Support for multiple large models (GPT-4, Claude, Qwen, etc.)
- Batch data processing capability
- Real-time execution result display
- JSON/JSONL format export support
- Visualization platform display

## Installation Guide

1. Clone the project
```bash
git clone git@gitlab.alibaba-inc.com:baohuchu/PowerInstruct.git
cd PowerInstruct
```

2. Check branch and switch to dev branch (this step won't be needed after open source)

```bash
# Check current branch
git branch

# Switch to dev branch
git checkout dev

# If dev branch doesn't exist, pull from remote and switch
git checkout -b dev origin/dev

# Ensure code is up to date
git pull origin dev
```

3. Create and activate virtual environment
```bash
conda create -n powerinstruct python=3.10
conda activate powerinstruct
```

4. Install dependencies
```bash
pip install -r requirements.txt
```

4. Configure environment variables (idealab version)

Windows:
```bash
# Create .env file in C:\Users\[Your Username]\ directory
SERVER_API_KEY=your_api_key
```

Mac/Linux:
```bash
# Add to ~/.bashrc or ~/.zshrc
export SERVER_API_KEY=<your_api_key>

# Or create .env file in home directory
echo "SERVER_API_KEY=<your_api_key>" >> ~/.env
```

5. Configure environment variables (OpenAI, Anthropic, Qwen API Key support)

    TODO


## Quick Start

1. Start service
```bash
python run.py
```

2. Access Web Interface
- Open browser and visit `http://localhost:5000`

3. Usage Process
   - Upload data file (JSON format supported)
   - Select model to use (different models can be selected for Seed and Code generation)
   - Execute seed data generation
   - Merge code generation template
   - Execute code generation
   - Download generated dataset (JSON/JSONL format supported)

## Project Structure

```
powerinstruct/
├── app/                    # Backend service
│   ├── api/                # API routes
│   ├── core/               # Core business logic
│   ├── services/           # Service layer
│   └── utils/              # Utility functions
├── static/                 # Frontend interface
│   ├── css/                # Style files
│   └── js/                 # JavaScript files
│   templates/              # HTML templates
├── data/                   # Data directory
│   ├── templates/          # Template files
│   └── uploads/            # Upload files
├── config/                 # Configuration files
├── tests/                  # Test cases
├── requirements.txt        # Project dependencies
└── README.md              # Project documentation
```

## Core Features

1. **File Processing**
   - JSON file upload support
   - File format validation
   - Batch file processing

2. **Model Invocation**
   - Multiple large model support
   - Model parameter configuration
   - Error retry mechanism

3. **Data Generation**
   - Seed data generation
   - Code template generation
   - Batch data conversion

4. **Result Export**
   - JSON format export
   - JSONL format export
   - Instruction data extraction

## Configuration Guide

1. Model Configuration
```python
SUPPORT_MODELS = [
    "gpt-4",
    "claude-37",
    "qwen-max",
    "gemini-pro"
]
```

2. Template Configuration
```json
{
    "prompt": "your_prompt_template",
    "codegen": "your_code_template"
}
```

## Development Guide

1. Code Standards
   - Follow PEP 8 standards
   - Use TypeScript for type checking
   - Write unit tests

2. Commit Standards
   - feat: new features
   - fix: bug fixes
   - docs: documentation updates
   - style: code formatting
   - refactor: code refactoring

## TODO

- [ ] Add more model support
- [ ] Improve error handling mechanism
- [ ] Add data validation functionality
- [ ] Optimize UI interaction experience
- [ ] Complete unit tests

## License

MIT License

## Contributors

- Zhuoyue Chen

## Contact Information

TODO: Change to public contact information

- Issues: [PowerInstruct Issues Page](https://code.alibaba-inc.com/baohuchu/PowerInstruct/issues)
- Email: chenzhuoyue.czy@alibaba-inc.com