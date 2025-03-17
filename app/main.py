import os
import pandas as pd
from dotenv import load_dotenv
import streamlit as st
import json
from app.utils.logger import get_logger
from app.utils.data_loader import load_sales_data
from app.api.openai_client import OpenAIClient
from ui.chat_interface import (
    initialize_chat_interface,
    add_user_message, 
    add_assistant_message,
    display_sales_data_summary
)
from models.schema import SalesQuery, SalesResponse, AugmentedResponse
from app.data.sales_data_service import generate_sales_data_summary
from app.api.assistant_client import AssistantClient

# Load environment variables
load_dotenv()

# Initialize logger
logger = get_logger()


def main():
    """
    Main function for the Streamlit application.
    """
    try:
        # Load sales data and generate summary only once at startup
        load_sales_data_and_summary()
        
        # Initialize openAI clients only once and store in session state
        initialize_clients()
        
        # Initialize Streamlit chat interface
        user_input = initialize_chat_interface()
        
        # Process user input
        if user_input:
            # Add user message to chat history
            add_user_message(user_input)
            
            # Create sales query
            sales_query = SalesQuery(query_text=user_input)
            
            # Process query with OpenAI (Stage 1: Historical Analysis)
            with st.spinner("Analyzing historical data..."):
                sales_response = st.session_state.openai_client.process_sales_query(sales_query, st.session_state.sales_data_summary)
            
            # Check if we have products and time period in the structured data
            has_product = sales_response.data and "products" in sales_response.data and len(sales_response.data["products"]) > 0
            has_time_period = sales_response.data and "time_period" in sales_response.data and sales_response.data["time_period"] != "unknown"
            
            # Only proceed with augmentation if we have identified products and time period
            if has_product and has_time_period:
                # Process with Assistant (Stage 2: Market Context Augmentation)
                with st.spinner("Gathering market insights..."):
                    augmented_response = st.session_state.assistant_client.augment_sales_response(sales_response)
                
                # Format the combined response for display
                combined_response = format_augmented_response(augmented_response)
                
                # Add assistant message to chat history
                add_assistant_message(combined_response)
            else:
                # Just use the historical analysis if we couldn't identify product/time period
                add_assistant_message(sales_response.response_text)
    
    except Exception as e:
        logger.error(f"Error in main function: {str(e)}")
        st.error(f"An error occurred: {str(e)}")

def initialize_clients():
    """
    Initialize API clients only once and store them in session state.
    """
    # Initialize OpenAI client if not already created
    if "openai_client" not in st.session_state:
        st.session_state.openai_client = OpenAIClient()
    
    # Initialize Assistant client if not already created
    if "assistant_client" not in st.session_state:
        st.session_state.assistant_client = AssistantClient()

def load_sales_data_and_summary():
    if "sales_data" not in st.session_state:
        # Get the absolute path to the script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        # Navigate to the data directory inside the app folder
        data_path = os.path.join(script_dir, "data", "sales_data.csv")
        # Load the data using the absolute path
        st.session_state.sales_data = load_sales_data(data_path)
        logger.info("Sales data loaded successfully")
            
        # Generate sales data summary
        st.session_state.sales_data_summary = generate_sales_data_summary(st.session_state.sales_data)
        logger.info("Sales data summary generated and stored in session state")

def format_augmented_response(augmented_response: AugmentedResponse) -> str:
    """
    Format an augmented response for display.
    
    Args:
        augmented_response (AugmentedResponse): The augmented response
        
    Returns:
        str: The formatted response
    """
    # Get the initial response
    initial_response = augmented_response.initial_response.response_text
    
    # Get the market insights
    market_insights = augmented_response.market_insights
    
    # Format market trends with proper spacing
    market_trends = []
    for trend in market_insights.market_trends:
        trend_name = trend.get("trend", "")
        impact = trend.get("impact", "")
        description = trend.get("description", "")
        if trend_name:
            market_trends.append(f"• {trend_name} ({impact}): {description}")
        else:
            market_trends.append(f"• {description}")
    
    # Format competitive landscape with proper spacing
    competitive_landscape = []
    for comp in market_insights.competitive_landscape:
        competitor = comp.get("competitor", "")
        action = comp.get("action", "")
        impact = comp.get("impact", "")
        description = comp.get("description", "")
        if competitor:
            competitive_landscape.append(f"• {competitor} - {action} ({impact}): {description}")
        else:
            competitive_landscape.append(f"• {description}")
    
    # Format regulatory considerations with proper spacing
    regulatory_considerations = []
    for reg in market_insights.regulatory_considerations:
        regulation = reg.get("regulation", "")
        timeline = reg.get("timeline", "")
        impact = reg.get("impact", "")
        description = reg.get("description", "")
        if regulation:
            regulatory_considerations.append(f"• {regulation} - {timeline} ({impact}): {description}")
        else:
            regulatory_considerations.append(f"• {description}")
    
    # Join lists with double line breaks for Streamlit display
    market_trends_text = "\n\n".join(market_trends)
    competitive_landscape_text = "\n\n".join(competitive_landscape)
    regulatory_considerations_text = "\n\n".join(regulatory_considerations)
    
    # Combine everything with clear section headers
    combined_response = f"""
HISTORICAL DATA ANALYSIS
=======================
{initial_response}


MARKET TRENDS
============
{market_trends_text}


COMPETITIVE LANDSCAPE
===================
{competitive_landscape_text}


REGULATORY CONSIDERATIONS
======================
{regulatory_considerations_text}
    """
    
    return combined_response

if __name__ == "__main__":
    main() 