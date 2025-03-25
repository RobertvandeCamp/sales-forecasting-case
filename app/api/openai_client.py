from dataclasses import Field
import os
import json
import openai
from typing import Dict, Any, List
from app.data.inventory import inventory_service
from app.utils.logger import get_logger
from app.models.schema import InventoryResponse, SalesQuery, SalesAnalysisResponse, inventory_response_json_schema
from dotenv import load_dotenv
from pydantic import BaseModel, Field
import traceback
from pydantic_core import from_json

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
            raise ValueError(
                "OpenAI API key not found. Please set the OPENAI_API_KEY environment variable."
            )

        self.client = openai.OpenAI(api_key=self.api_key)
        self.model = model
        logger.info(f"OpenAI client initialized with model: {model}")

    def process_sales_query(
        self, query: SalesQuery, sales_data_summary: Dict[str, Any]
    ) -> SalesAnalysisResponse:
        """
        Process a sales query using the OpenAI API with JSON schema response format.

        Args:
            query (SalesQuery): The sales query to process
            sales_data_summary (Dict[str, Any]): Summary of sales data to provide context

        Returns:
            SalesAnalysisResponse: The response to the query with structured data
        """
        try:
            logger.info(f"Processing sales query: {query.query_text}")

            # Create system message with context about the sales data
            system_message = self._create_system_message(sales_data_summary)

            completion = self.client.beta.chat.completions.parse(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": query.query_text},
                ],
                response_format=SalesAnalysisResponse,
                temperature=0.7,
            )

            sales_response = completion.choices[0].message.parsed

            logger.debug(f"Response {sales_response.response_text}")
            logger.debug(f"Response {sales_response.products}")
            logger.debug(f"Response {sales_response.time_period}")

            logger.info(f"Sales query processed successfully")

            if sales_response.products:
                inventory_response = self.process_inventory_query(
                    sales_response.products
                )
            else:
                inventory_response = None

            return sales_response, inventory_response

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
        6. Carefully identify all products mentioned in the query.
        7. Identify the time period mentioned in the query (e.g., next month, this quarter, next year).
        
        Your response will be in JSON format with these fields:
        - products: An array of product names mentioned in the query
        - time_period: The time period mentioned in the query
        - forecast_text: Your natural language response to the query
        
        Now, analyze the user's query and provide the best response you can.
        """

        return system_message

    def process_inventory_query(self, products: List[str]) -> str:
        """
        Process an inventory query using the OpenAI API.

        Args:
            products (List[str]): The products to get inventory for

        Returns:
            str: The response to the inventory query
        """

        tools = [
            {
                "name": "get_inventory",
                "description": "Get the inventory of the product",
                "type": "function",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "product_name": {
                            "type": "string",
                            "description": "The name of the product",
                        }
                    },
                    "required": ["product_name"],
                    "additionalProperties": False,
                },
                "strict": True,
            }
        ]

        try:
            logger.info(f"Processing inventory query for products: {products}")

            messages = [
                {
                    "role": "system",
                    "content": "You are a helpful assistant that can answer questions about the inventory of an FMCG company.",
                },
                {
                    "role": "user",
                    "content": f"What is the inventory for the following products: {products}",
                },
            ]

            # First completion to get the tool calls and find out if a tool call is needed.
            inventory_completion = self.client.responses.create(
                model=self.model,
                input=messages,
                tools=tools,
                temperature=0.7
            )

            logger.info(f"Inventory Completion: {inventory_completion}")

            messages.append(
                {
                    "role": "assistant",
                    "content": inventory_completion.output_text,
                }
            )

            # Get the tool call output.
            for tool_call in inventory_completion.output:
                # Check if the tool call is for getting the inventory.
                if tool_call.name == "get_inventory":
                    # Get the arguments for the tool call.
                    args = json.loads(tool_call.arguments)
                    # Get the inventory for the product.
                    inventory = inventory_service.get_inventory(
                        args.get("product_name")
                    )

                    messages.append(tool_call)
                    messages.append(
                        {
                            "type": "function_call_output",
                            "call_id": tool_call.call_id,
                            "output": json.dumps(inventory.model_dump()) if inventory else "",
                        }
                    )

            # Second completion to get the final response, send the tool call output to the model.
            completion_2 = self.client.responses.create(
                model=self.model,
                input=messages,
                tools=tools,
                text=inventory_response_json_schema # This is the JSON schema for the response.
            )

            logger.info(f"Inventory Completion 2: {completion_2.output_text}")

            # --------------------------------------------------------------
            # Step 5: Check model response
            # --------------------------------------------------------------

            # Validate the response using the JSON schema. (this is the response from the model)
            inventory_response: InventoryResponse = InventoryResponse.model_validate(from_json(completion_2.output_text))
            return inventory_response

        except Exception as e:
            logger.error(f"Error processing inventory query: {str(e)}")
            logger.error(traceback.print_tb(e.__traceback__))
            raise
