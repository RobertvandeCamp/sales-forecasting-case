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
    add_assistant_message
)
from models.schema import InventoryResponse, SalesQuery, SalesAnalysisResponse, AugmentedResponse
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
                sales_response =  st.session_state.openai_client.process_sales_query(sales_query, st.session_state.sales_data_summary)
                # Create a temporary container to show intermediate result
                historical_analysis_container = st.empty()
                historical_analysis_container.markdown(f"💡 **Historical Analysis:**\n{sales_response.response_text}")
            
            # Check if we have products and time period in the structured data
            has_product = len(sales_response.products) > 0
            if has_product:
                inventory_response = st.session_state.openai_client.process_inventory_query(sales_response.products)
                # Create another temporary container for inventory result
                inventory_container = st.empty()
                inventory_container.markdown(f"📦 **Current Inventory:**\n{inventory_response.answer}")
            else:
                inventory_response = None

            has_time_period = sales_response.time_period != "unknown"
            # Only proceed with augmentation if we have identified products and time period
            if has_product and has_time_period:
                # Process with Assistant (Stage 2: Market Context Augmentation)
                with st.spinner("Gathering market insights..."):
                    augmented_response:AugmentedResponse = st.session_state.assistant_client.augment_sales_response(sales_response)
                
                # Format the combined response for display
                historical_and_insights_response = format_augmented_response(augmented_response)
                
                # Clear the temporary result before showing final response
                historical_analysis_container.empty()
                inventory_container.empty()

                add_assistant_message(inventory_response.answer + " (Inventory ID: " + inventory_response.source + ")")
                add_assistant_message(historical_and_insights_response)
            else:
                # Just use the historical analysis if we couldn't identify product/time period
                add_assistant_message(sales_response.response_text)
            
            st.rerun()
    
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
    Format an augmented response for display using Markdown for better Streamlit presentation.
    
    Args:
        augmented_response (AugmentedResponse): The augmented response
        
    Returns:
        str: The formatted response in Markdown format
    """
    # Get the initial response
    initial_response = augmented_response.initial_response.response_text
    
    # Get the market insights
    market_insights = augmented_response.market_insights
    
    # Format market trends with proper Markdown
    market_trends = []
    for market_trend in market_insights.market_trends:
        trend_name = market_trend.trend
        impact = market_trend.impact
        description = market_trend.description
        
        # Format impact with color indicators using Markdown
        impact_formatted = f"**{impact}**"
        if impact == "Positive":
            impact_formatted = f"**:green[{impact}]**"
        elif impact == "Negative":
            impact_formatted = f"**:red[{impact}]**"
        elif impact == "Neutral":
            impact_formatted = f"**:blue[{impact}]**"
        
        if trend_name:
            market_trends.append(f"* **{trend_name}** ({impact_formatted}): {description}")
        else:
            market_trends.append(f"* {description}")
    
    # Format competitive landscape with proper Markdown
    competitive_landscape = []
    for comp in market_insights.competitive_landscape:
        competitor = comp.competitor
        action = comp.action
        impact = comp.impact
        description = comp.description
        
        # Format impact with color indicators using Markdown
        impact_formatted = f"**{impact}**"
        if impact == "Positive":
            impact_formatted = f"**:green[{impact}]**"
        elif impact == "Negative":
            impact_formatted = f"**:red[{impact}]**"
        elif impact == "Neutral":
            impact_formatted = f"**:blue[{impact}]**"
        
        if competitor:
            competitive_landscape.append(f"* **{competitor}** - {action} ({impact_formatted}): {description}")
        else:
            competitive_landscape.append(f"* {description}")
    
    # Format regulatory considerations with proper Markdown
    regulatory_considerations = []
    for reg in market_insights.regulatory_considerations:
        regulation = reg.regulation
        timeline = reg.timeline
        impact = reg.impact
        description = reg.description
        
        # Format impact with color indicators using Markdown
        impact_formatted = f"**{impact}**"
        if impact == "Positive":
            impact_formatted = f"**:green[{impact}]**"
        elif impact == "Negative":
            impact_formatted = f"**:red[{impact}]**"
        elif impact == "Neutral":
            impact_formatted = f"**:blue[{impact}]**"
        
        if regulation:
            regulatory_considerations.append(f"* **{regulation}** - {timeline} ({impact_formatted}): {description}")
        else:
            regulatory_considerations.append(f"* {description}")
    
    # Join lists with single line breaks for Markdown list formatting
    market_trends_text = "\n".join(market_trends)
    competitive_landscape_text = "\n".join(competitive_landscape)
    regulatory_considerations_text = "\n".join(regulatory_considerations)
    
    # Create a horizontal divider to separate sections
    divider = "---"
    
    # Combine everything with clear section headers in Markdown format
    combined_response = f"""
## 📊 Historical Data Analysis
{initial_response}

{divider}

## 📈 Market Trends
{market_trends_text}

{divider}

## 🏢 Competitive Landscape
{competitive_landscape_text}

{divider}

## 📝 Regulatory Considerations
{regulatory_considerations_text}
    """
    
    return combined_response

if __name__ == "__main__":
    main() 