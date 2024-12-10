from breact_sdk import BReactClient, BaseService, ServiceConfig
from typing import Dict, Any


# Create custom service
class QAService(BaseService):
    service_id = "qa_service"
    
    async def ask(self, question: str) -> Dict[str, Any]:
        return await self.execute("ask", {"question": question})

# Use the SDK
async def main():
    # Initialize client
    client = BReactClient(
        base_url="http://localhost:8000",
        api_key="your-api-key"
    )
    
    # Register and use custom service
    qa_service = client.register_service(QAService)
    response = await qa_service.ask("What is BReact OS?")
    
    # Or use generic execution
    response = await client.execute_service(
        "text_analyzer",
        "analyze",
        {"text": "Sample text"}
    )
    