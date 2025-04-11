# Email Management Workflow

A workflow that orchestrates BReact OS services to analyze, classify, and generate responses to emails.

## Overview

This workflow demonstrates the capabilities of BReact OS by integrating multiple services to:
- Analyze email threads for sentiment, key points, action items, and response urgency
- Classify emails into categories (inquiry, complaint, support, feedback, sales)
- Generate contextually appropriate responses with the right tone based on classification and analysis

## Architecture

The workflow uses three primary BReact OS services:
1. **Email Response Service** - Analyzes email threads and generates appropriate responses
2. **Classifier Service** - Categorizes emails into predefined classes
3. **Information Tracker Service** - (Optional extension) Can extract structured information from emails

## Requirements

- Python 3.8+
- BReact SDK (`breactsdk`)
- Required Python packages: 
  - `python-dotenv`
  - `asyncio`

## Installation

1. Clone or download this repository
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Set up environment variables in a `.env` file:

```
BREACT_API_KEY=your_api_key_here
BREACT_BASE_URL=https://api-os.breact.ai
```

## Usage

### Command Line

Run the workflow from the command line:

```bash
python email_management_workflow.py --input example_email_thread.json --output results.json
```

Parameters:
- `--input`, `-i`: Input JSON file containing email thread (required)
- `--output`, `-o`: Output file for results (optional)
- `--example`, `-e`: Generate an example email thread JSON file

### Generate Example Email Thread

To generate an example email thread JSON file:

```bash
python email_management_workflow.py --example
```

This will create a file called `example_email_thread.json` that you can use as input for testing.

### Using as a Module

You can also use the `EmailManagementWorkflow` in your own code:

```python
import asyncio
from email_management_workflow import EmailManagementWorkflow

async def process_emails():
    # Initialize and set up the workflow
    workflow = await EmailManagementWorkflow().setup()
    
    # Define an email thread (list of email messages)
    email_thread = [
        {
            "sender": "customer@example.com",
            "recipient": "support@company.com",
            "subject": "Question about your product",
            "content": "Hi, I'm interested in your product but have some questions...",
            "timestamp": "2023-06-01T09:32:45Z"
        }
    ]
    
    # Process the email thread
    results = await workflow.process_email(email_thread)
    
    # Access the results
    print(f"Email classified as: {results['classification'].get('class')}")
    print(f"Sentiment: {results['analysis'].get('sentiment')}")
    print(f"Suggested response: {results['suggested_response']}")

# Run the example
asyncio.run(process_emails())
```

## Response Format

The workflow returns a dictionary with the following structure:

```json
{
  "analysis": {
    "sentiment": "neutral|positive|negative",
    "key_points": ["point1", "point2", ...],
    "action_items": ["action1", "action2", ...],
    "response_urgency": "low|medium|high"
  },
  "classification": {
    "class": "inquiry|complaint|support|feedback|sales",
    "confidence": 0.95
  },
  "suggested_response": "Generated email response..."
}
```

## Advanced Usage

### Custom Classification Types

You can specify custom classification types:

```python
results = await workflow.process_email(
    email_thread,
    classification_types=["technical_support", "billing_inquiry", "feature_request"]
)
```

### Integration with Other Systems

This workflow can be integrated with email systems, CRM platforms, or helpdesk software by:
1. Retrieving emails from the external system
2. Converting them to the required format
3. Processing them with the workflow
4. Sending the generated responses back or updating the system

## Extending the Workflow

Possible extensions to this workflow include:
- Adding more advanced email analysis capabilities
- Integrating with knowledge bases for more accurate responses
- Implementing email routing based on classification
- Adding multilingual support

## Support

For questions or issues, please contact:
- Email: your-email@example.com
- GitHub: https://github.com/yourusername/email-workflow 