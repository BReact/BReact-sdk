# BReact SDK

A Python SDK for interacting with BReact's AI services, supporting both synchronous and asynchronous operations.

## Installation

```bash
pip install breact-sdk
```

## Configuration

The SDK can be configured using environment variables or programmatically:

### Environment Variables
Create a `.env` file in your project root:
```env
BREACT_API_KEY=your_api_key
BREACT_BASE_URL=https://api-os.breact.ai  # Optional, defaults to this URL
```

### Programmatic Configuration
```python
from breactsdk.client import create_client

# Create client with custom configuration
client = create_client(
    api_key="your_api_key",  # If not provided, the SDK will use the one from the environment variable
    base_url="https://api-os.breact.ai"  # Optional
)
```

## Usage Examples

### Text Summarization

```python
from breactsdk.client import create_client

# Async usage
async with create_client(async_client=True) as client:
    summary = await client.aisummary.summarize(
        text="Your text to summarize",
        summary_type="executive",
        model_id="mistral-small",
        options={
            "temperature": 0.7,
            "max_tokens": 500
        }
    )

# Sync usage
with create_client() as client:
    summary = client.aisummary.summarize(
        text="Your text to summarize",
        summary_type="executive",
        model_id="mistral-small"
    )
```

### Email Analysis and Response Generation

```python
async with create_client(async_client=True) as client:
    # Analyze email thread
    analysis = await client.email_response.analyze_thread(
        email_thread=[{
            "sender": "client@example.com",
            "recipient": "support@company.com",
            "subject": "Urgent: Service Downtime",
            "content": "Email content here",
            "timestamp": "2024-01-20T09:00:00Z"
        }],
        analysis_type=["sentiment", "key_points", "action_items", "response_urgency"]
    )

    # Generate email response
    response = await client.email_response.generate_response(
        email_thread=[{
            "sender": "client@example.com",
            "recipient": "support@company.com",
            "subject": "Product Feature Inquiry",
            "content": "Email content here",
            "timestamp": "2024-01-20T10:30:00Z"
        }],
        tone="friendly",
        style_guide={
            "language": "en",
            "max_length": 150,
            "greeting_style": "casual",
            "signature": "\nBest regards,\nSupport Team"
        },
        key_points=[
            "Address AI capabilities",
            "Explain pricing plans",
            "Highlight support options"
        ]
    )
```

### Information Tracking

```python
# Define your schema
schema = {
    "type": "object",
    "properties": {
        "primary_symptom": {
            "type": "string",
            "enum": ["headache", "nausea", "dizziness"]
        },
        "duration": {
            "type": "string"
        }
    },
    "required": ["primary_symptom", "duration"]
}

# Process information
async with create_client(async_client=True) as client:
    result = await client.information_tracker.process(
        content="Your text content",
        context={
            "updateType": "medical_symptoms",
            "currentInfo": {
                "previous_symptoms": ["mild headache"]
            }
        },
        config={
            "modelId": "mistral-large-2411",
            "temperature": 0.1,
            "maxTokens": 2000,
            "schema": schema
        }
    )
```

### Concurrent Processing

```python
async with create_client(async_client=True) as client:
    tasks = [
        client.aisummary.summarize(
            text=f"Text {i}",
            summary_type="executive",
            model_id="mistral-small"
        ) for i in range(3)
    ]
    
    results = await asyncio.gather(*tasks)
```

## Error Handling

The SDK provides detailed error information:

```python
try:
    result = await client.aisummary.summarize(text="Your text")
except Exception as e:
    if hasattr(e, 'response'):
        print(f"Status code: {e.response.status_code}")
        print(f"Error details: {e.response.text}")
    print(f"Error: {str(e)}")
```

## Available Services

1. **AI Summary** (`client.aisummary`)
   - `summarize`: Generate text summaries

2. **Email Response** (`client.email_response`)
   - `analyze_thread`: Analyze email threads
   - `generate_response`: Generate email responses

3. **Information Tracker** (`client.information_tracker`)
   - `process`: Extract structured information from text

## Best Practices

1. Always use context managers (`with` or `async with`) to ensure proper resource cleanup
2. Choose between sync and async clients based on your application's needs
3. Set appropriate timeouts and model parameters for your use case
4. Handle errors appropriately in production code
5. Store API keys securely using environment variables

## Running the Demo

A comprehensive demo script is included that showcases all features:

```bash
python demo.py
```

## Support

For issues and feature requests, please contact office@breact.ai 