import os
import time
import json
from typing import Any, Optional
from openai import OpenAI
from app.utils.logger import get_logger
from app.models.schema import SalesAnalysisResponse, AugmentedResponse, MarketInsights, NewMarketInsights
from pydantic_core import from_json

# Initialize logger
logger = get_logger()

class AssistantClient:
    """
    Client for interacting with the OpenAI Assistant API.
    """
    def __init__(self):
        """
        Initialize the Assistant client.
        """
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.assistant_id = os.getenv("OPENAI_ASSISTANT_ID")
        
        if not self.api_key:
            logger.error("OpenAI API key not found in environment variables")
            raise ValueError("OpenAI API key not found. Please set the OPENAI_API_KEY environment variable.")
            
        if not self.assistant_id:
            logger.error("OpenAI Assistant ID not found in environment variables")
            raise ValueError("OpenAI Assistant ID not found. Please set the OPENAI_ASSISTANT_ID environment variable.")
        
        self.client = OpenAI(api_key=self.api_key)
        logger.info("Assistant client initialized successfully")
        
    def augment_sales_response(self, sales_response: SalesAnalysisResponse) -> AugmentedResponse:
        """
        Augment a sales response with market insights from the Assistant.
        
        Args:
            sales_response (SalesAnalysisResponse): The initial sales response with structured data
            
        Returns:
            AugmentedResponse: The augmented response with market insights
        """
        try:
            # Extract products and time period from the structured data
            products = sales_response.products
            time_period = sales_response.time_period
            
            # Use first product if multiple products are mentioned
            product = products[0] if products else "unknown"
            
            logger.info(f"Augmenting sales response for product: {product}, time period: {time_period}")
            
            # Create a thread
            thread = self.client.beta.threads.create()
            
            # Add a message to the thread
            message_content = self._create_message_content(sales_response, product, time_period)
            logger.debug(f"Message content being sent to Assistant:\n{message_content}")
            
            self.client.beta.threads.messages.create(
                thread_id=thread.id,
                role="user",
                content=message_content
            )
            logger.info("Message added to thread")
            
            # Run the assistant
            run = self.client.beta.threads.runs.create(
                thread_id=thread.id,
                assistant_id=self.assistant_id
            )
            logger.info(f"Assistant run created with ID: {run.id}")
            logger.info(f"Using assistant ID: {self.assistant_id}")
            
            # Wait for the run to complete
            run = self._wait_for_run(thread.id, run.id)
            
            # Get the assistant's response
            messages = self.client.beta.threads.messages.list(
                thread_id=thread.id,
                order="desc",
                limit=1
            )
            
            # Extract the assistant's response
            assistant_response = messages.data[0].content[0].text.value
            
            try:
                new_market_insights = NewMarketInsights.model_validate(from_json(assistant_response))
                logger.debug(f"New market insights: {new_market_insights.market_trends}")
                logger.debug(f"New market insights: {new_market_insights.competitive_landscape}")
                logger.debug(f"New market insights: {new_market_insights.regulatory_considerations}")
            except ValueError as e:
                logger.error(f"Error parsing json model into pydantic model NewMarketInsights")

                # market_insights = MarketInsights(
                #     market_trends=[{"description": "Could not parse market trends", "impact": "Unknown"}],
                #     competitive_landscape=[{"description": "Could not parse competitive landscape", "impact": "Unknown"}],
                #     regulatory_considerations=[{"description": "Could not parse regulatory considerations", "impact": "Unknown"}]
                # )
                  
           
            # Create augmented response
            augmented_response = AugmentedResponse(
                initial_response=sales_response,
                market_insights=new_market_insights
            )
            
            logger.info("Sales response augmented successfully")
            return augmented_response
            
        except Exception as e:
            logger.error(f"Error augmenting sales response: {str(e)}")
            raise
    
    def _create_message_content(self, sales_response: SalesAnalysisResponse, product: str, time_period: str) -> str:
        """
        Create the message content to send to the Assistant.
        
        Args:
            sales_response (SalesResponse): The initial sales response
            product (str): The product being forecasted
            time_period (str): The time period of the forecast
            
        Returns:
            str: The message content
        """
        return f"""
        Please provide market insights to augment this sales forecast:
        
        Product: {product}
        Time Period: {time_period}
        
        Initial Forecast (based on historical data):
        {sales_response.response_text}
        
        Provide only the JSON object in your instructions without any additional text or markdown formatting.
        """
    
    def _wait_for_run(self, thread_id: str, run_id: str, max_wait_seconds: int = 120) -> Any:
        """
        Wait for a run to complete.
        
        Args:
            thread_id (str): The thread ID
            run_id (str): The run ID
            max_wait_seconds (int): Maximum time to wait in seconds
            
        Returns:
            Any: The completed run
        """
        start_time = time.time()
        while time.time() - start_time < max_wait_seconds:
            run = self.client.beta.threads.runs.retrieve(
                thread_id=thread_id,
                run_id=run_id
            )
            
            if run.status == "completed":
                return run
            elif run.status in ["failed", "cancelled", "expired"]:
                logger.error(f"Run failed with status: {run.status}")
                raise Exception(f"Assistant run failed with status: {run.status}")
            
            # Wait before checking again
            time.sleep(1)
        
        # If we've exceeded the max wait time
        logger.error("Run timed out")
        raise Exception("Assistant run timed out")
