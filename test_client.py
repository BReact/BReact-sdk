import pytest
import asyncio
from typing import Dict, Any
from breact_sdk import BReactClient, BaseService

async def main():
    # Initialize client
    client = BReactClient(
        base_url="http://localhost:8000",
        api_key="your-api-key"
    )
    
    try:
        # Fetch available services
        print("\nFetching available services...")
        services = await client.fetch_services()
        print(f"Found {len(services)} services:")
        for service_id, service in services.items():
            print(f"- {service.name} ({service_id})")
        
        # Test pre-built summarization service
        print("\nTesting pre-built summarization service...")
        summarizer = await client.get_service("summarizer")
        if summarizer:
            result = await summarizer.summarize(
                text="""
                The BReact SDK provides a flexible interface for interacting with BReact OS services.
                It supports both pre-built service implementations and dynamic service creation.
                The SDK handles parameter validation, service discovery, and response parsing automatically.
                """,
                max_length=50
            )
            print("\nSummarization result:")
            #print(f"Full response: {result}")
            if result.status == "completed":
                service_result = result.result
                if service_result and service_result.status == "success":
                    content = service_result.result.get("content", "No summary generated")
                    print(f"Summary: {content.strip()}")
                else:
                    print(f"Service error: {service_result.error or 'Unknown error'}")
            else:
                print(f"Process error: {result.error or 'Unknown error'}")
        
        # Test generic target analyzer service
        print("\nTesting generic target analyzer service...")
        analyzer = await client.get_service("target_analyzer")
        if analyzer:
            targets = {
                "todo": [
                    {
                        "id": 1,
                        "target": "Document project requirements",
                        "done_when": "Core features and user stories are documented",
                        "depends_on": []
                    },
                    {
                        "id": 2,
                        "target": "Create project timeline",
                        "done_when": "Project milestones and deadlines are established",
                        "depends_on": [1]
                    },
                    {
                        "id": 3,
                        "target": "Define technical architecture",
                        "done_when": "System components and their interactions are specified",
                        "depends_on": [1]
                    }
                ],
                "done": []
            }
            
            result = await analyzer.execute(
                "analyze_targets",
                {
                    "text": """User: I need help with my project.
AI: I'll help you plan your project. Let's start by creating a timeline.
User: That sounds good. I think we should start with the requirements phase.
AI: Great choice! I've documented the requirements we discussed, including the core features and user stories.""",
                    "targets": targets,
                    "additional_context": "The user is starting a new software project and needs help with the planning phase.",
                    "model_id": "mistral",
                    "options": {
                        "tier": "basic",
                        "format": "json",
                        "temperature": 0,
                        "max_tokens": 1000
                    }
                }
            )
            
            print("\nTarget analysis result:")
            if result.status == "success":
                updated_targets = result.result
                print("\nCompleted targets:")
                for target in updated_targets.get("done", []):
                    print(f"- {target['target']}")
                print("\nRemaining targets:")
                for target in updated_targets.get("todo", []):
                    print(f"- {target['target']}")
            else:
                print(f"Analysis failed: {result.error or 'Unknown error'}")
        
        # Test generic service usage
        print("\nTesting generic service usage...")
        text_analyzer = await client.get_service("text_analyzer")
        if text_analyzer:
            result = await text_analyzer.execute(
                "analyze",
                {"text": "This is a sample text for analysis."}
            )
            print("\nText analysis result:")
            print(f"Word count: {result.get('word_count', 'N/A')}")
            print(f"Character count: {result.get('char_count', 'N/A')}")
            print(f"Average word length: {result.get('avg_word_length', 'N/A')}")
            
    except Exception as e:
        print(f"\nError occurred: {str(e)}")
    
if __name__ == "__main__":
    asyncio.run(main())
