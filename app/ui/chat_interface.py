import streamlit as st
import pandas as pd
from typing import List, Dict, Any
from app.models.schema import ChatMessage, ChatHistory
from app.utils.logger import get_logger

logger = get_logger()

def initialize_chat_interface():
    """
    Initialize the Streamlit chat interface.
    """
    # Set page title and icon
    st.set_page_config(
        page_title="Sales Forecasting Chatbot",
        page_icon="📊",
        layout="wide"
    )
    
    # Add header
    st.title("📊 AI-Powered Sales Forecasting Chatbot")
    st.markdown("""
    Ask questions about sales data and get AI-powered insights.
    
    **Example questions:**
    - What were the top-selling products last month?
    - Predict sales for Energy Bars next week.
    - Show me the average sales of Nut & Seed Bars in the last 3 months.
    """)
    
    # Initialize session state for chat history if it doesn't exist
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = ChatHistory(messages=[])
    
    # Display chat history
    display_chat_history()
    
    # Chat input
    user_input = st.chat_input("Type your question here...")
    
    return user_input

def display_chat_history():
    """
    Display the chat history.
    """
    chat_history = st.session_state.chat_history
    
    # Display each message in the chat history
    for message in chat_history.messages:
        with st.chat_message(message.role):
            st.write(message.content)

def add_user_message(message: str):
    """
    Add a user message to the chat history.
    
    Args:
        message (str): The user message
    """
    # Log the user message
    logger.info(f"User message: {message}")
    
    # Create a chat message
    chat_message = ChatMessage(
        role="user",
        content=message
    )
    
    # Add the message to the chat history
    st.session_state.chat_history.messages.append(chat_message)

def add_assistant_message(message: str):
    """
    Add an assistant message to the chat history.
    
    Args:
        message (str): The assistant message
    """
    # Log the assistant message
    logger.info(f"Assistant message: {message}")
    
    # Create a chat message
    chat_message = ChatMessage(
        role="assistant",
        content=message
    )
    
    # Add the message to the chat history
    st.session_state.chat_history.messages.append(chat_message)

    st.rerun()

def display_sales_data_summary(sales_data: pd.DataFrame):
    """
    Display a summary of the sales data.
    
    Args:
        sales_data (pd.DataFrame): The sales data
    """
    with st.expander("Sales Data Summary"):
        # Display basic info
        st.write(f"**Data Period:** {sales_data['Date'].min().strftime('%Y-%m-%d')} to {sales_data['Date'].max().strftime('%Y-%m-%d')}")
        st.write(f"**Number of Records:** {len(sales_data)}")
        st.write(f"**Products:** {', '.join(sales_data['Product'].unique())}")
        
        # Display summary statistics
        st.write("**Summary Statistics:**")
        st.dataframe(sales_data[['Sales_Units', 'Revenue']].describe())
        
        # Display sample data
        st.write("**Sample Data:**")
        st.dataframe(sales_data.head()) 