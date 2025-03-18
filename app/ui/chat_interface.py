import streamlit as st
import pandas as pd
from typing import List, Dict, Any, Optional
from app.models.schema import ChatMessage, ChatHistory
from app.utils.logger import get_logger
from app.utils.conversation_storage import ConversationStorage

logger = get_logger()
conversation_storage = ConversationStorage()

def initialize_chat_interface() -> Optional[str]:
    """
    Initialize the Streamlit chat interface.
    
    Returns:
        Optional[str]: User input message if provided
    """
    # Set page title and icon
    st.set_page_config(
        page_title="Sales Forecasting Chatbot",
        page_icon="📊",
        layout="wide"
    )
    
    # Create a header with username display at top right
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.title("📊 AI-Powered Sales Forecasting Chatbot")
    
    with col2:
        # Display username if logged in
        if "username" in st.session_state and st.session_state.username:
            st.markdown(f"""
            <div style="text-align: right; padding-top: 15px; padding-right: 15px;">
                <p>Welcome: <b>{st.session_state.username}</b></p>
            </div>
            """, unsafe_allow_html=True)
    
    # User identification section
    with st.sidebar:
        st.header("User Identification")
        
        # Get available users
        available_users = conversation_storage.get_available_users()
        
        # Initialize username in session state if not exists
        if "username" not in st.session_state:
            st.session_state.username = ""
            
        # Determine if user is logged in
        is_logged_in = st.session_state.username != ""
        
        if not is_logged_in:
            # New user input
            new_username = st.text_input("Enter your username to save conversations:")
            
            # Select existing user
            if available_users:
                st.write("Or select an existing user:")
                selected_user = st.selectbox("Select user", [""] + available_users)
                
                if selected_user:
                    new_username = selected_user
            
            # Login button
            if st.button("Login") and new_username:
                st.session_state.username = new_username
                
                # Load previous conversation if user exists
                if new_username in available_users:
                    st.session_state.chat_history = conversation_storage.load_conversation(new_username)
                    st.rerun()
        else:
            # Show logged in user
            st.success(f"Logged in as: {st.session_state.username}")
            
            # Logout button
            if st.button("Logout"):
                # Save conversation before logout
                if len(st.session_state.chat_history.messages) > 0:
                    conversation_storage.save_conversation(
                        st.session_state.username, 
                        st.session_state.chat_history
                    )
                
                # Clear username and reset chat history
                st.session_state.username = ""
                st.session_state.chat_history = ChatHistory(messages=[])
                st.rerun()
    
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
    logger.debug(f"Assistant message: {message}")
    
    # Create a chat message
    chat_message = ChatMessage(
        role="assistant",
        content=message
    )
    
    # Add the message to the chat history
    st.session_state.chat_history.messages.append(chat_message)
    
    # Save conversation if user is logged in
    if st.session_state.username:
        conversation_storage.save_conversation(
            st.session_state.username,
            st.session_state.chat_history
        )
    
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