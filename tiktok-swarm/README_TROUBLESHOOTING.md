# Troubleshooting Guide

## Python Version Compatibility

The error you're seeing is likely due to Python 3.13 compatibility issues with LangGraph. The LangGraph ecosystem is currently optimized for Python 3.10-3.12.

### Solution Options:

#### Option 1: Use Python 3.11 or 3.12 (Recommended)
```bash
# Install Python 3.11 or 3.12
# Then create a virtual environment
python3.11 -m venv venv
# or
python3.12 -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

#### Option 2: Run Without LangGraph Studio
Instead of using `langgraph dev`, you can run the API server directly:

```bash
# From the tiktok-swarm directory
python run_local.py
```

This will start the FastAPI server on http://localhost:8000 without needing LangGraph Studio.

#### Option 3: Test Basic Functionality
Test if the swarm works without the dev server:

```bash
python test_swarm.py
```

## Alternative Installation

If you're still having issues, try installing specific versions:

```bash
pip install langgraph==0.2.50
pip install langchain-core==0.3.0
pip install langchain-openai==0.1.0
```

## Running Without Studio

To use the swarm without LangGraph Studio:

1. Start the API server:
   ```bash
   python run_local.py
   ```

2. Test with curl:
   ```bash
   curl -X POST "http://localhost:8000/chat" \
        -H "Content-Type: application/json" \
        -d '{"message": "Analyze trending TikTok dances"}'
   ```

3. Access the interactive docs:
   http://localhost:8000/docs

## Common Issues

### ImportError: cannot import name 'Graph'
This is a version mismatch between langgraph and langgraph-api. Solution:
- Use Python 3.11 or 3.12
- Install specific versions as listed above

### Module not found errors
Make sure you're in the tiktok-swarm directory and have activated your virtual environment.

### OPENAI_API_KEY not set
Edit the `.env` file and add your OpenAI API key:
```
OPENAI_API_KEY=sk-...
```