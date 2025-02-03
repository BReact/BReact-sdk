# BReact SDK

Official Python SDK for BReact OS, providing a simple and type-safe way to interact with BReact OS services.

## Features
- Type-safe service interactions using Pydantic models
- Async/await support for all operations
- Custom service creation through base classes
- Parallel service execution with asyncio
- Comprehensive error handling
- Built-in services for text analysis, summarization, and email processing
- Automatic service discovery and initialization
- MIT Licensed

## Installation

### From PyPI
```bash
pip install breact-sdk
```

### For Development (Editable Mode)
```bash
git clone https://github.com/breactos/breact-sdk.git
cd breact-sdk
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e ".[dev]"
```

### Configuration
The SDK can be configured using environment variables or programmatically when initializing the client.

#### Using Environment Variables (Recommended)
Create a `.env` file in your project root:
```env
BREACT_API_KEY=your-api-key
# Optional: Override the default endpoint
# BREACT_BASE_URL=https://api-os.breact.ai
```

Or set them in your shell:
```bash
export BREACT_API_KEY=your-api-key
```

Or set them in your code:
```python
from breact_sdk import BReactClient
BReactClient.create(api_key="your-api-key")
```

## Quick Start

### Basic Usage
```python
from breact_sdk import BReactClient

async def main():
    # Initialize client using environment variables
    client = await BReactClient.create()
    
    try:
        # Example: Use AI Summarization
        summary_result = await client.ai_summarize(
            text="Your text to summarize",
            summary_type="brief",
            model_id="mistral-small"  # Optional: specify model
        )
        
        if summary_result.status == "completed":
            print(f"Summary: {summary_result.result}")
            
        # Example: Analyze Targets
        targets_result = await client.analyze_targets(
            text="Sample text for target analysis",
            targets=["key_points", "sentiment"],
            model_id="mistral-small"
        )
        
        if targets_result.status == "completed":
            print(f"Analysis: {targets_result.result}")
            
    finally:
        await client.close()
```

### Email Processing Features
```python
async def process_emails():
    # You can also override settings programmatically if needed
    client = await BReactClient.create(
        api_key="override-api-key",  # Optional: override environment variable
        base_url="custom-endpoint"   # Optional: override default endpoint
    )
    
    try:
        # Generate email response
        response = await client.generate_email_response(
            email_thread=[
                {
                    "sender": "user@example.com",
                    "content": "Initial email content",
                    "timestamp": "2024-03-20T10:00:00Z"
                }
            ],
            tone="professional",
            style_guide={
                "language": "en",
                "max_length": 300,
                "greeting_style": "formal"
            }
        )
        
        if response.status == "completed":
            print(f"Generated response: {response.result}")
            
    finally:
        await client.close()
```

### Information Processing
```python
async def process_info():
    client = await BReactClient.create(api_key="your-api-key")
    
    try:
        # Extract structured information
        result = await client.extract_information(
            text="Your text content",
            schema={
                "name": "string",
                "age": "number",
                "interests": "array"
            }
        )
        
        if result.status == "completed":
            print(f"Extracted info: {result.result}")
            
    finally:
        await client.close()
```

## Core Services

### Text Analysis
- Target Analysis: Analyze specific aspects of text
- AI Summarization: Generate concise summaries
- Information Extraction: Extract structured data from text

### Email Processing
- Response Generation: Create contextual email responses
- Thread Analysis: Analyze email conversations
- Style Customization: Control tone and format

## API Reference

### BReactClient
The client can be initialized with or without arguments:

```python
# Using environment variables (recommended)
client = await BReactClient.create()

# Or with optional overrides
client = await BReactClient.create(
    base_url="https://api-os.breact.ai",  # Optional: override default endpoint
    api_key="your-api-key",               # Optional: override BREACT_API_KEY
    request_timeout=30,                   # Optional: default is 30
    poll_interval=1.0,                   # Optional: default is 1.0
    poll_timeout=180.0                  # Optional: default is 180.0
)
```

All parameters are optional when using `create()`:
- `base_url`: Defaults to "https://api-os.breact.ai" if not specified
- `api_key`: Uses BREACT_API_KEY environment variable if not specified
- `request_timeout`: HTTP request timeout in seconds (default: 30)
- `poll_interval`: Polling interval for async operations (default: 1.0)
- `poll_timeout`: Maximum polling time (default: 180.0)

#### Key Methods
- `async ai_summarize(text, summary_type="brief", model_id=None)`: Generate text summaries
- `async analyze_targets(text, targets, model_id="mistral-small")`: Analyze specific aspects of text
- `async generate_email_response(email_thread, tone="professional")`: Generate email responses
- `async extract_information(text, schema)`: Extract structured information
- `async close()`: Close client and cleanup resources

## Requirements
- Python >= 3.11
- httpx >= 0.24.0
- pydantic >= 2.0.0
- typing-extensions >= 4.0.0

## License
MIT License - see LICENSE file for details

## Support
- GitHub Issues: [breactos/breact-sdk/issues](https://github.com/breactos/breact-sdk/issues)
- Documentation: [docs.breactos.com](https://docs.breactos.com)
- Email: office@breact.ai

