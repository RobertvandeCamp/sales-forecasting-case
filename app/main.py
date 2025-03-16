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
from models.schema import SalesQuery
from app.data.sales_data_service import generate_sales_data_summary

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
        
        # Use the stored data from session state
        sales_data_summary = st.session_state.sales_data_summary
        
        # Initialize OpenAI client
        openai_client = OpenAIClient()
        logger.info("OpenAI client initialized successfully")
        
        # Initialize Streamlit chat interface
        user_input = initialize_chat_interface()
        
        # Display sales data summary
        # display_sales_data_summary(sales_data)
        
        # Process user input
        if user_input:
            # Add user message to chat history
            add_user_message(user_input)
            
            # Create sales query
            sales_query = SalesQuery(query_text=user_input)
            
            # Process query with OpenAI
            with st.spinner("Thinking..."):
                sales_response = openai_client.process_sales_query(sales_query, sales_data_summary)
            
            # Add assistant message to chat history
            add_assistant_message(sales_response.response_text)
    
    except Exception as e:
        logger.error(f"Error in main function: {str(e)}")
        st.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main() 