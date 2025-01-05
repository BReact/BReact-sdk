# BReact SDK

Official Python SDK for BReact OS, providing a simple and type-safe way to interact with BReact OS services.

## Features
- Type-safe service interactions using Pydantic models
- Async/await support for all operations
- Custom service creation through base classes
- Parallel service execution with asyncio
- Comprehensive error handling
- Full test coverage
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

## Quick Start

### Basic Usage
```python
from breact_sdk import BReactClient

async def main():
    # Initialize client
    client = BReactClient(
        base_url="http://localhost:8000",
        api_key="your-api-key"
    )
    
    try:
        # Fetch available services
        services = await client.fetch_services()
        print(f"Found {len(services)} services:")
        for service_id, service in services.items():
            print(f"- {service.name} ({service_id})")
            
        # Execute text analysis service
        text_analyzer = await client.get_service("text_analyzer")
        result = await text_analyzer.execute(
            "analyze",
            {"text": "This is a sample text for analysis."}
        )
        
        if result.status == "completed":
            service_result = result.result
            print(f"Word count: {service_result.get('word_count')}")
            print(f"Character count: {service_result.get('char_count')}")
    finally:
        await client.close()
```

### Parallel Service Execution
```python
import asyncio
from breact_sdk import BReactClient

async def analyze_text(client: BReactClient):
    try:
        analyzer = await client.get_service("text_analyzer")
        result = await analyzer.execute(
            "analyze",
            {"text": "Sample text for analysis"}
        )
        return result
    except Exception as e:
        print(f"Text analyzer error: {str(e)}")

async def summarize_text(client: BReactClient):
    try:
        summarizer = await client.get_service("summarizer")
        result = await summarizer.summarize(
            text="Text to summarize",
            max_length=50
        )
        return result
    except Exception as e:
        print(f"Summarizer error: {str(e)}")

async def main():
    client = BReactClient(
        base_url="http://localhost:8000",
        api_key="your-api-key"
    )
    
    try:
        # Run services in parallel
        await asyncio.gather(
            analyze_text(client),
            summarize_text(client),
            return_exceptions=True
        )
    finally:
        await client.close()
```

### Error Handling
```python
from breact_sdk import BReactClient, ServiceExecutionError

async def main():
    client = BReactClient(...)
    try:
        result = await client.execute_service(
            "text_analyzer",
            "analyze",
            {"text": "Sample text"}
        )
        if result.status == "completed":
            print(result.result)
        else:
            print(f"Error: {result.error}")
    except ServiceExecutionError as e:
        print(f"Service execution failed: {e}")
    finally:
        await client.close()
```

## API Reference

### BReactClient
```python
client = BReactClient(
    base_url="http://localhost:8000",  # BReact OS server URL
    api_key="your-api-key",           # Optional API key
    request_timeout=30,               # Request timeout in seconds
    poll_interval=3.0,               # Polling interval for async operations
    poll_timeout=180.0              # Maximum polling time
)
```

#### Methods
- `async fetch_services()`: List available services
- `async get_service(service_id)`: Get a specific service
- `async execute_service(service_id, endpoint, params)`: Execute a service endpoint
- `async close()`: Close client and cleanup resources

## Development

### Running Tests
```bash
pytest tests/
```

### Code Style
```bash
black breact_sdk/
isort breact_sdk/
mypy breact_sdk/
```

## License
MIT License - see LICENSE file for details

## Support
- GitHub Issues: [breactos/breact-sdk/issues](https://github.com/breactos/breact-sdk/issues)
- Documentation: [docs.breactos.com](https://docs.breactos.com)
- Email: support@breactos.com

