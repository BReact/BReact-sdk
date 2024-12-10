# BReact SDK Developer Guide

This document provides detailed technical information about the BReact SDK's architecture, core concepts, and development guidelines.

## Core Concepts

### 1. Client Architecture
The SDK is built around the `BReactClient` class, which handles:
- Service registration and management
- HTTP communication with BReact OS
- Authentication and request handling
- Service discovery and execution

### 2. Service Model
Services in BReact SDK follow a hierarchical structure:

```python
class BaseService:
    service_id: str              # Unique identifier
    service_config: ServiceConfig # Service configuration
    
    async def initialize()       # Service initialization
    async def execute()         # Generic execution method
```

#### Service Configuration
Services are configured using Pydantic models:
```python
class ServiceConfig:
    id: str
    name: str
    description: str
    version: str
    endpoints: Dict[str, Dict[str, Any]]
```

### 3. Response Handling
All service responses are wrapped in a standardized `ServiceResponse` model:
```python
class ServiceResponse:
    process_id: str
    access_token: str
    status: str
    result: Optional[Dict[str, Any]]
    error: Optional[str]
```

## Development Guidelines

### 1. Creating New Services

1. Inherit from `BaseService`
2. Define a unique `service_id`
3. Implement service-specific methods
4. Use the `execute()` method for API calls

Example:
```python
from breact_sdk import BaseService

class CustomService(BaseService):
    service_id = "custom_service"
    
    async def custom_method(self, data: str):
        return await self.execute("endpoint_name", {"data": data})
```

### 2. Error Handling

The SDK provides a hierarchy of exceptions:
- `BReactError` - Base exception
- `BReactClientError` - Client configuration issues
- `ServiceExecutionError` - Runtime execution failures
- `ServiceNotFoundError` - Service discovery issues

### 3. Testing Guidelines

1. Use pytest for all tests
2. Mock external HTTP calls
3. Test both success and error cases
4. Ensure async/await compatibility
5. Maintain test coverage above 90%

### 4. Code Style

Follow these standards:
- Use Black for formatting (line length: 88)
- Sort imports with isort
- Maintain type hints and use mypy
- Document all public methods and classes

## Project Structure

```
breact_sdk/
├── sdk/
│   ├── client.py      # Core client implementation
│   ├── types/         # Type definitions and models
│   ├── exceptions.py  # Exception hierarchy
│   └── utils/         # Helper utilities
├── services/          # Pre-built service implementations
└── examples/          # Usage examples and patterns
```

## Development Setup

1. Create development environment:
```bash
python -m venv venv
source venv/bin/activate
pip install -e ".[dev]"
```

2. Install development tools:
```bash
pip install -r requirements.txt
```

3. Run quality checks:
```bash
black breact_sdk/
isort breact_sdk/
mypy breact_sdk/
pytest tests/
```

## Common Development Tasks

### Adding a New Service

1. Create new file in `breact_sdk/services/`
2. Inherit from `BaseService`
3. Implement service methods
4. Add to `__init__.py`
5. Add tests in `tests/services/`

### Updating Client Capabilities

1. Modify `BReactClient` in `sdk/client.py`
2. Update type definitions if needed
3. Add tests for new functionality
4. Update documentation

### Release Process

1. Update version in:
   - `__init__.py`
   - `setup.py`
2. Run full test suite
3. Update CHANGELOG.md
4. Create GitHub release
5. Deploy to PyPI

## Performance Considerations

- Use connection pooling for multiple requests
- Implement proper timeout handling
- Consider rate limiting for API calls
- Cache service configurations when possible

## Security Best Practices

1. Never log API keys or sensitive data
2. Use environment variables for configuration
3. Validate all input parameters
4. Handle errors gracefully
5. Use HTTPS for all API communications

## Contributing

1. Fork the repository
2. Create feature branch
3. Follow code style guidelines
4. Add tests for new features
5. Submit pull request

## Troubleshooting

### Common Issues

1. Connection Errors
   - Check base_url configuration
   - Verify network connectivity
   - Confirm API key validity

2. Service Execution Failures
   - Validate input parameters
   - Check service availability
   - Review error messages

3. Type Checking Errors
   - Ensure proper type hints
   - Run mypy before committing
   - Check Pydantic model definitions

## Additional Resources

- API Documentation: [docs.breactos.com](https://docs.breactos.com)
- Issue Tracker: [GitHub Issues](https://github.com/breactos/breact-sdk/issues)
- Support: support@breactos.com
