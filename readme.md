# BReact SDK

Official Python SDK for BReact OS, providing a simple and type-safe way to interact with BReact OS services.

## Features
- Type-safe service interactions using Pydantic models
- Async/await support for all operations
- Custom service creation through base classes
- Comprehensive error handling
- Full test coverage
- MIT Licensed

## Installation

### From PyPI
```bash
pip install breact-sdk
```

### For Development (Editable Mode)
1. Clone the repository:
```bash
git clone https://github.com/breactos/breact-sdk.git
cd breact-sdk
```

2. Create and activate a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install in editable mode with development dependencies:
```bash
pip install -e ".[dev]"
```

This installs the package in "editable" or "development" mode, meaning:
- Changes to the source code take effect immediately without reinstalling
- The package is installed as a reference to your source code
- Great for development and testing changes

## Quick Start

### Basic Usage
```python
from breact_sdk import BReactClient

async def main():
    # Initialize the client
    client = BReactClient(
        base_url="http://localhost:8000",
        api_key="your-api-key"
    )
    
    # List available services
    services = await client.get_services()
    
    # Execute a service
    response = await client.execute_service(
        "text_analyzer",
        "analyze",
        {"text": "Sample text"}
    )
```

### Creating Custom Services
```python
from breact_sdk import BaseService

class CustomService(BaseService):
    service_id = "custom_service"
    
    async def custom_endpoint(self, data: str):
        return await self.execute("custom_endpoint", {"data": data})

# Using the custom service
async def main():
    client = BReactClient(...)
    custom = client.register_service(CustomService)
    result = await custom.custom_endpoint("test data")
```

## Project Structure
```
breact_sdk/
├── breact_sdk/
│   ├── sdk/
│   │   ├── client.py          # Main BReactClient class
│   │   ├── types/            # Type definitions
│   │   ├── exceptions.py     # Custom exceptions
│   │   └── utils/           # Helper utilities
│   ├── services/            # Pre-built services
│   └── examples/            # Usage examples
└── tests/                   # Test suite
```

## Development

### Setup Development Environment
```bash
# Clone the repository
git clone https://github.com/breactos/breact-sdk.git
cd breact-sdk

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -r requirements.txt

# Install package in editable mode
pip install -e .
```

### Running Tests
```bash
pytest tests/
```

### Code Style
We use:
- Black for code formatting
- isort for import sorting
- mypy for type checking

Format code before committing:
```bash
black breact_sdk/
isort breact_sdk/
mypy breact_sdk/
```

## API Reference

### BReactClient
```python
client = BReactClient(
    base_url="http://localhost:8000",  # BReact OS server URL
    api_key="your-api-key",           # Optional API key
    timeout=30                        # Request timeout in seconds
)
```

#### Methods
- `async get_services()`: List available services
- `async execute_service(service_id, endpoint, params)`: Execute a service endpoint
- `register_service(service_class)`: Register a custom service

### BaseService
Base class for creating custom services:
```python
class CustomService(BaseService):
    service_id = "required_service_id"
    
    async def initialize(self):
        """Optional initialization"""
        pass
        
    async def your_method(self, param: str):
        return await self.execute("endpoint_name", {"param": param})
```

## Error Handling
The SDK provides several exception classes:
```python
from breact_sdk import (
    BReactError,           # Base exception
    BReactClientError,     # Client configuration errors
    ServiceExecutionError, # Service execution failures
    ServiceNotFoundError   # Service not found
)

try:
    result = await client.execute_service(...)
except ServiceExecutionError as e:
    print(f"Service execution failed: {e}")
```

## Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

## Documentation
For detailed documentation, visit [docs.breactos.com](https://docs.breactos.com)

## License
MIT License - see LICENSE file for details

## Support
- GitHub Issues: [breactos/breact-sdk/issues](https://github.com/breactos/breact-sdk/issues)
- Documentation: [docs.breactos.com](https://docs.breactos.com)
- Email: support@breactos.com