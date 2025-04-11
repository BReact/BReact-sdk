#!/usr/bin/env python3
"""
Email Management Workflow - An agent that orchestrates BReact OS services
to analyze, classify, and generate responses to emails.
"""

import os
import json
import asyncio
import logging
import argparse
from typing import Dict, Any, List, Optional
from datetime import datetime

# Try to load environment variables from .env file if present
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Import BReact SDK
from breactsdk.client import create_client

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("EmailManagementWorkflow")

class EmailManagementWorkflow:
    """A workflow that analyzes, classifies, and generates responses to emails using BReact OS services."""
    
    def __init__(self):
        """Initialize the workflow."""
        self.client = None
        
    async def setup(self):
        """Set up the workflow, create client connection."""
        logger.info("Setting up EmailManagementWorkflow")
        self.client = create_client(async_client=True)
        return self
    
    async def process_email(self, email_thread: List[Dict[str, Any]], 
                           classification_types: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Process an email thread to analyze, classify, and generate a response.
        
        Args:
            email_thread: List of email messages in the thread, with each message containing
                          sender, recipient, subject, content, and timestamp fields
            classification_types: Optional list of classification types to use
                                 (defaults to ["inquiry", "complaint", "support", "feedback", "sales"])
        
        Returns:
            Dictionary containing analysis, classification, and suggested response
        """
        if not classification_types:
            classification_types = ["inquiry", "complaint", "support", "feedback", "sales"]
            
        logger.info(f"Processing email thread with {len(email_thread)} messages")
        
        # Step 1: Analyze the email thread
        logger.info("Analyzing email thread")
        print(f"[DEBUG] Sending to analyze_thread: {json.dumps(email_thread, indent=2)}")
        analysis = await self.client.email_response.analyze_thread(
            email_thread=email_thread,
            analysis_type=["sentiment", "key_points", "action_items", "response_urgency"]
        )
        print(f"[DEBUG] Received from analyze_thread: {json.dumps(analysis, indent=2)}")
        logger.info(f"Email analysis completed: {json.dumps(analysis, indent=2)}")
        
        # Step 2: Classify the email type
        logger.info("Classifying email")
        print(f"[DEBUG] Sending to classifier: content={email_thread[-1]['content'][:100]}... context={{'allowedClasses': {classification_types}}}")
        classification = await self.client.classifier.process(
            content=email_thread[-1]["content"],
            context={
                "allowedClasses": classification_types
            }
        )
        print(f"[DEBUG] Received from classifier: {json.dumps(classification, indent=2)}")
        
        # Debug the classification structure
        print(f"[DEBUG] Classification raw: {classification}")
        print(f"[DEBUG] Result key exists: {'result' in classification}")
        if 'result' in classification:
            print(f"[DEBUG] Result type: {type(classification['result'])}")
            print(f"[DEBUG] Result value: {classification['result']}")
            print(f"[DEBUG] Result.result exists: {'result' in classification['result']}")
            if 'result' in classification['result']:
                print(f"[DEBUG] Result.result type: {type(classification['result']['result'])}")
                print(f"[DEBUG] Result.result value: {classification['result']['result']}")
                print(f"[DEBUG] Result.result.class exists: {'class' in classification['result']['result']}")
                if 'class' in classification['result']['result']:
                    print(f"[DEBUG] Found class: {classification['result']['result']['class']}")
        
        # Extract class value correctly
        class_value = classification.get('result', {}).get('class', 'unknown')
        logger.info(f"Email classified as: {class_value}")
        
        # Step 3: Generate appropriate response based on classification and analysis
        logger.info("Generating response")
        
        # Determine tone based on classification and sentiment
        tone = "professional"
        if class_value == "complaint" or analysis.get("sentiment") == "negative":
            tone = "empathetic"
        elif class_value in ["inquiry", "feedback"]:
            tone = "friendly"
            
        # Determine priority based on urgency analysis
        priority = analysis.get("analysis", {}).get("response_urgency", "medium")
        
        print(f"[DEBUG] Sending to generate_response: email_thread={json.dumps(email_thread[:10], indent=2)}, style_guide={{'tone': '{tone}', 'priority': '{priority}'}}")
        response = await self.client.email_response.generate_response(
            email_thread=email_thread,
            style_guide={
                "tone": tone,
                "priority": priority
            }
        )
        print(f"[DEBUG] Received from generate_response: {json.dumps(response, indent=2)}")
        
        logger.info("Email response generated successfully")
        
        return {
            "analysis": analysis,
            "classification": classification,
            "suggested_response": response
        }
    
    async def process_from_file(self, input_file: str, output_file: Optional[str] = None) -> Dict[str, Any]:
        """
        Process an email thread from a JSON file and optionally save results to an output file.
        
        Args:
            input_file: Path to input JSON file containing email thread
            output_file: Optional path to output file for results
            
        Returns:
            Processing results
        """
        logger.info(f"Processing email thread from file: {input_file}")
        
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            if not isinstance(data, list):
                raise ValueError("Input file must contain a list of email messages")
                
            results = await self.process_email(data)
            
            if output_file:
                logger.info(f"Saving results to: {output_file}")
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(results, f, indent=2)
                    
            return results
            
        except Exception as e:
            logger.error(f"Error processing email from file: {str(e)}")
            raise
            
async def main():
    """Main function to run the workflow from command line."""
    parser = argparse.ArgumentParser(description="Email Management Workflow")
    parser.add_argument("--input", "-i", help="Input JSON file containing email thread")
    parser.add_argument("--output", "-o", help="Output file for results (optional)")
    parser.add_argument("--example", "-e", action="store_true", help="Generate example email thread JSON")
    
    args = parser.parse_args()
    
    if args.example:
        # Generate an example email thread JSON file
        example_file = "example_email_thread.json"
        example_thread = [
            {
                "sender": "customer@example.com",
                "recipient": "support@company.com",
                "subject": "Issue with recent order #12345",
                "content": "Hello,\n\nI placed an order (#12345) three days ago and still haven't received a shipping confirmation. According to your website, it should have shipped by now. Can you please check on this and let me know the status?\n\nThanks,\nJohn",
                "timestamp": datetime.now().isoformat()
            }
        ]
        
        with open(example_file, 'w', encoding='utf-8') as f:
            json.dump(example_thread, f, indent=2)
            
        print(f"Example email thread saved to: {example_file}")
        return
    
    if not args.input:
        parser.print_help()
        return
        
    workflow = await EmailManagementWorkflow().setup()
    results = await workflow.process_from_file(args.input, args.output)
    
    if not args.output:
        # Print results to console if no output file specified
        print(json.dumps(results, indent=2))
    
if __name__ == "__main__":
    asyncio.run(main()) 