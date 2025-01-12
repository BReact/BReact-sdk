import asyncio
import os
from typing import Dict, List
from dotenv import load_dotenv
from breact_sdk import BReactClient

# Load environment variables
load_dotenv()

async def test_target_analyzer():
    # Initialize client
    client = BReactClient()
    
    try:
        # First, fetch available services
        print("Fetching available services...")
        services = await client.fetch_services()
        print(f"Available services: {list(services.keys())}")

        TargetAnalyzer = await client.target_analyze("Input text here")

        # Get generic service instance
        print("\nGetting target analyzer service...")
        service = await client.get_service("target_analyzer")
        if not service:
            print("Error: Target Analyzer service not found")
            return

        # Example targets
        sample_targets = {
            "todo": [
                {
                    "id": 1,
                    "target": "Document project requirements",
                    "done_when": "Core features and user stories are documented",
                    "depends_on": []
                },
                {
                    "id": 2,
                    "target": "Set up development environment",
                    "done_when": "Local development environment is configured and running",
                    "depends_on": [1]  # Depends on documentation
                }
            ],
            "done": []
        }

        # Rest of the code remains the same...
        chat_history = """
        User: I've finished writing up all the core features and user stories in the requirements document.
        Assistant: Great! The documentation looks comprehensive and covers all the necessary aspects.
        User: Should we move on to setting up the development environment?
        Assistant: Yes, now that we have the requirements documented, we can proceed with the environment setup.
        """

        params = {
            "text": chat_history,
            "targets": sample_targets,
            "additional_context": "Project initialization phase",
            "options": {
                "tier": "standard",
                "format": "json",
                "temperature": 0,
                "max_tokens": 1000
            }
        }

        print("\nAnalyzing targets...")
        response = await service.execute("analyze_targets", params)

        if response.status == "completed":
            # Access the result attribute of the ServiceResponse
            result = response.result
            
            print("\nResults:")
            print("\nCompleted Targets:")
            if isinstance(result, dict):  # Add type checking
                for target in result.get("done", []):
                    print(f"- {target['target']} (ID: {target['id']})")
                
                print("\nRemaining Targets:")
                for target in result.get("todo", []):
                    print(f"- {target['target']} (ID: {target['id']})")
                    if target["depends_on"]:
                        print(f"  Depends on: {target['depends_on']}")
            else:
                print(f"Unexpected result format: {result}")
        else:
            print(f"Error: {response.error}")

    except Exception as e:
        print(f"Error occurred: {str(e)}")
        import traceback
        print(traceback.format_exc())
    finally:
        await client.close()

# Run the test
if __name__ == "__main__":
    asyncio.run(test_target_analyzer()) 