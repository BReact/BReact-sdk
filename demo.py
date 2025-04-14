import asyncio
import logging
from breactsdk.client import create_client

# Configure logging to be less verbose
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)
logging.getLogger("breactsdk").setLevel(logging.INFO)

# Sample text for demonstrations
SAMPLE_TEXT = """
Artificial Intelligence (AI) has transformed various industries, from healthcare to finance.
Machine learning algorithms can now process vast amounts of data to identify patterns and make predictions.
Natural Language Processing has enabled computers to understand and generate human-like text.
Computer Vision systems can recognize objects and faces with remarkable accuracy.
These advancements have led to improved automation and decision-making capabilities.
"""

SAMPLE_EMAIL = """
Hi Support Team,

I'm wondering about the timeline for our current project. We seem to be running behind
schedule on the database implementation phase. Could you provide an update on when
we can expect this to be completed?

Also, will this delay affect our final delivery date?

Thanks,
John
"""

# Medical information schema for the information tracker demo
MEDICAL_SCHEMA = {
    "type": "object",
    "properties": {
        "primary_symptom": {
            "type": "string",
            "enum": ["headache", "nausea", "dizziness", "fatigue", "pain"]
        },
        "duration": {
            "type": "string"
        },
        "pain_level": {
            "type": "string"
        },
        "associated_symptoms": {
            "type": "array",
            "items": {
                "type": "string"
            }
        },
        "aggravating_factors": {
            "type": "array",
            "items": {
                "type": "string"
            }
        },
        "family_history": {
            "type": "object",
            "properties": {
                "present": {
                    "type": "boolean"
                },
                "details": {
                    "type": "string"
                }
            },
            "required": ["present"]
        }
    },
    "required": ["primary_symptom", "duration", "pain_level"]
}

async def demo_text_summarization():
    """Demonstrate the text summarization service."""
    print("\n=== Text Summarization Demo ===")
    async with create_client(async_client=True) as client:
        try:
            result = await client.summary.summarize(
                text=SAMPLE_TEXT,
                summary_type="executive",
                model_id="mistral-small",
                options={
                    "temperature": 0.7,
                    "max_tokens": 500
                }
            )
            print(f"Summary: {result}")
            if not result:
                print("Warning: Received empty result from the service")
        except Exception as e:
            print(f"Error in text summarization: {str(e)}")
            print(f"Error type: {type(e)}")
            raise

async def demo_email_analysis():
    """Demonstrate email analysis and response generation."""
    print("\n=== Email Analysis Demo ===")
    async with create_client(async_client=True) as client:
        try:
            # First analyze the email thread
            analysis = await client.email_response.analyze_thread(
                email_thread=[{
                    "sender": "client@example.com",
                    "recipient": "support@company.com",
                    "subject": "Urgent: Service Downtime",
                    "content": """Hello,

We're experiencing issues with the API integration. Our production system is affected and we need immediate assistance. This is causing significant delays in our operations.

Please help ASAP.

Regards,
John""",
                    "timestamp": "2024-01-20T09:00:00Z"
                },
                {
                    "sender": "support@company.com",
                    "recipient": "client@example.com",
                    "subject": "Re: Urgent: Service Downtime",
                    "content": """Hi John,

I understand the urgency. Our team is looking into this right now. Could you please provide your API key and any error messages you're seeing?

We'll prioritize this issue.

Best regards,
Sarah""",
                    "timestamp": "2024-01-20T09:15:00Z"
                }],
                analysis_type=["sentiment", "key_points", "action_items", "response_urgency"]
            )
            print("\nEmail Analysis Results:")
            print(f"Analysis: {analysis}")

            # Generate a response
            response = await client.email_response.generate_response(
                email_thread=[{
                    "sender": "client@example.com",
                    "recipient": "support@company.com",
                    "subject": "Product Feature Inquiry",
                    "content": """Hi there,

I'm interested in your product but I have a few questions about the features. Could you tell me more about the AI capabilities and pricing plans? Also, what kind of support do you offer?

Thanks,
John""",
                    "timestamp": "2024-01-20T10:30:00Z"
                }],
                tone="friendly",
                style_guide={
                    "language": "en",
                    "max_length": 150,
                    "greeting_style": "casual",
                    "signature": "\nBest regards,\nSarah\nCustomer Success Team"
                },
                key_points=[
                    "Address AI capabilities",
                    "Explain pricing plans",
                    "Highlight support options"
                ]
            )
            print("\nGenerated Response:")
            print(response)
        except Exception as e:
            print(f"Error during email demo: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response status code: {e.response.status_code}")
                print(f"Response content: {e.response.text}")
            raise

async def demo_information_tracker():
    """Demonstrate the information tracker service."""
    print("\n=== Information Tracker Demo ===")
    async with create_client(async_client=True) as client:
        result = await client.information_tracker.process(
            content="Patient reports severe headache lasting for 3 days, accompanied by nausea and sensitivity to light. Pain level is described as 8/10. Symptoms worsen with physical activity. No prior history of migraines, but family history shows mother had similar symptoms.",
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
                "schema": MEDICAL_SCHEMA
            }
        )
        print("\nExtracted Information:")
        print(result)

def demo_sync_usage():
    """Demonstrate synchronous usage of the SDK."""
    print("\n=== Synchronous Usage Demo ===")
    with create_client() as client:
        # Simple text summarization
        result = client.summary.summarize(
            text=SAMPLE_TEXT,
            summary_type="executive",
            model_id="mistral-small"
        )
        print(f"\nSync Summary: {result}")

async def demo_concurrent_processing():
    """Demonstrate concurrent processing of multiple requests."""
    print("\n=== Concurrent Processing Demo ===")
    async with create_client(async_client=True) as client:
        # Process multiple texts concurrently
        tasks = [
            client.summary.summarize(
                text=f"Part {i} of the text: {SAMPLE_TEXT}",
                summary_type="executive",
                model_id="mistral-small"
            ) for i in range(3)
        ]
        
        results = await asyncio.gather(*tasks)
        for i, result in enumerate(results):
            print(f"\nSummary {i + 1}: {result}")

async def main():
    """Run all demos."""
    try:
        await demo_text_summarization()
        await demo_email_analysis()
        await demo_information_tracker()
        demo_sync_usage()
        await demo_concurrent_processing()
    except Exception as e:
        print(f"\nDemo failed: {str(e)}")
        return 1
    return 0

if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        exit(exit_code)
    except KeyboardInterrupt:
        print("\nDemo interrupted by user")
        exit(1)
    except Exception as e:
        print(f"\nUnexpected error: {str(e)}")
        exit(1) 