import asyncio
import os
from breact_sdk import BReactClient
from dotenv import load_dotenv

load_dotenv(override=True)

async def test_summarizer(client: BReactClient):
    print("\nTesting pre-built summarization service...")
    try:
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
            if result.status == "completed":
                service_result = result.result
                if service_result and service_result.status == "success":
                    content = service_result.result.get("content", "No summary generated")
                    print(f"Summary: {content.strip()}")
                else:
                    print(f"Service error: {service_result.error or 'Unknown error'}")
            else:
                print(f"Process error: {result.error or 'Unknown error'}")
    except Exception as e:
        print(f"Summarizer error: {str(e)}")

async def test_target_analyzer(client: BReactClient):
    print("\nTesting generic target analyzer service...")
    try:
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
                        "tier": "standard",
                        "format": "json",
                        "temperature": 0,
                        "max_tokens": 1000
                    }
                }
            )
            
            print("\nTarget analysis result:")
            if result.status == "completed":
                updated_targets = result.result
                print("\nCompleted targets:")
                for target in updated_targets.get("done", []):
                    print(f"- {target['target']}")
                print("\nRemaining targets:")
                for target in updated_targets.get("todo", []):
                    print(f"- {target['target']}")
            else:
                print(f"Process error: {result.error or 'Unknown error'}")
    except Exception as e:
        print(f"Target analyzer error: {str(e)}")

async def test_text_analyzer(client: BReactClient):
    print("\nTesting generic service usage...")
    try:
        text_analyzer = await client.get_service("text_analyzer")
        if text_analyzer:
            result = await text_analyzer.execute(
                "analyze",
                {"text": "This is a sample text for analysis."}
            )
            print("\nText analysis result:")
            if result.status == "completed":
                service_result = result.result
                if service_result and isinstance(service_result, dict):
                    print(f"Word count: {service_result.get('word_count', 'N/A')}")
                    print(f"Character count: {service_result.get('char_count', 'N/A')}")
                    print(f"Average word length: {service_result.get('avg_word_length', 'N/A')}")
                else:
                    print(f"Service error: {result.error or 'Unknown error'}")
            else:
                print(f"Process error: {result.error or 'Unknown error'}")
    except Exception as e:
        print(f"Text analyzer error: {str(e)}")

async def main():
    # Initialize client
    client = BReactClient()
    
    try:
        # Fetch available services
        print("\nFetching available services...") # TODO: Client py init should fetch services
        services = await client.fetch_services()
        print(f"Found {len(services)} services:")
        for service_id, service in services.items():
            print(f"- {service.name} ({service_id})")
        
        # Run all tests in parallel
        await asyncio.gather(
            test_summarizer(client),
            test_target_analyzer(client),
            test_text_analyzer(client),
            return_exceptions=True
        )
        
    except Exception as e:
        print(f"\nError occurred: {str(e)}")
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(main())
