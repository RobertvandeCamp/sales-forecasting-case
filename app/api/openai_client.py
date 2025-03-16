import os
import json
import openai
from typing import Dict, Any, List, Optional
from app.utils.logger import get_logger
from app.models.schema import SalesQuery, SalesResponse
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = get_logger()

class OpenAIClient:
    """
    Client for interacting with the OpenAI API.
    """
    def __init__(self, model: str = "gpt-4o"):
        """
        Initialize the OpenAI client.
        
        Args:
            model (str): The OpenAI model to use
        """
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            logger.error("OpenAI API key not found in environment variables")
            raise ValueError("OpenAI API key not found. Please set the OPENAI_API_KEY environment variable.")
        
        self.client = openai.OpenAI(api_key=self.api_key)
        self.model = model
        logger.info(f"OpenAI client initialized with model: {model}")
    
    def process_sales_query(self, query: SalesQuery, sales_data_summary: Dict[str, Any]) -> SalesResponse:
        """
        Process a sales query using the OpenAI API.
        
        Args:
            query (SalesQuery): The sales query to process
            sales_data_summary (Dict[str, Any]): Summary of sales data to provide context
            
        Returns:
            SalesResponse: The response to the query
        """
        try:
            logger.info(f"Processing sales query: {query.query_text}")
            
            # Create system message with context about the sales data
            system_message = self._create_system_message(sales_data_summary)
            
            # Create user message
            user_message = query.query_text
            
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.7,
            )
            
            # Extract response text
            response_text = response.choices[0].message.content
            
            # Create sales response
            sales_response = SalesResponse(
                query=query.query_text,
                response_text=response_text,
                data=None  # No structured data for now
            )
            
            logger.info(f"Sales query processed successfully")
            return sales_response
        
        except Exception as e:
            logger.error(f"Error processing sales query: {str(e)}")
            raise
    
    def _create_system_message(self, sales_data_summary: Dict[str, Any]) -> str:
        """
        Create a system message with context about the sales data.
        
        Args:
            sales_data_summary (Dict[str, Any]): Summary of sales data
            
        Returns:
            str: The system message
        """
        # Convert sales data summary to JSON string
        sales_data_json = json.dumps(sales_data_summary, default=str)
        
        # Create system message
        system_message = f"""
        You are an AI assistant specialized in sales forecasting and analysis.
        You have access to historical sales data for various food bar products.
        
        The available sales data includes:
        {sales_data_json}
        
        When responding to queries:
        1. Provide accurate information based on the available data.
        2. If a forecast is requested, give a reasonable estimate based on historical trends.
        3. Be clear about the limitations of your forecast.
        4. Keep responses concise but informative.
        5. If you don't know the answer or the data is insufficient, say so.
        
        Now, analyze the user's query and provide the best response you can.
        """
        
        return system_message 