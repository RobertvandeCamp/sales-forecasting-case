import pandas as pd
import os
from datetime import datetime
from app.utils.logger import get_logger

logger = get_logger()

def load_sales_data(file_path: str) -> pd.DataFrame:
    """
    Load sales data from a CSV file.
    
    Args:
        file_path (str): Path to the CSV file
        
    Returns:
        pd.DataFrame: DataFrame containing sales data
    """
    try:
        logger.info(f"Loading sales data from {file_path}")
        
        # Check if file exists
        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Read CSV file
        df = pd.read_csv(file_path)
        
        # Check if required columns exist
        required_columns = ['Date', 'Product', 'Sales_Units', 'Revenue']
        for col in required_columns:
            if col not in df.columns:
                logger.error(f"Required column {col} not found in {file_path}")
                raise ValueError(f"Required column {col} not found in {file_path}")
        
        # Preprocess data
        df = preprocess_sales_data(df)
        
        logger.info(f"Successfully loaded and preprocessed sales data with {len(df)} rows")
        return df
    
    except Exception as e:
        logger.error(f"Error loading sales data: {str(e)}")
        raise

def preprocess_sales_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Preprocess sales data.
    
    Args:
        df (pd.DataFrame): Raw sales data
        
    Returns:
        pd.DataFrame: Preprocessed sales data
    """
    # Convert Date column to datetime
    df['Date'] = pd.to_datetime(df['Date'])
    
    # Ensure Sales_Units and Revenue are numeric
    df['Sales_Units'] = pd.to_numeric(df['Sales_Units'], errors='coerce')
    df['Revenue'] = pd.to_numeric(df['Revenue'], errors='coerce')
    
    # Handle missing values
    df = df.dropna()
    
    # Add derived columns that might be useful for analysis
    df['Year'] = df['Date'].dt.year
    df['Month'] = df['Date'].dt.month
    df['Week'] = df['Date'].dt.isocalendar().week
    df['Quarter'] = df['Date'].dt.quarter
    
    # Calculate Average Price per Unit
    df['Price_Per_Unit'] = df['Revenue'] / df['Sales_Units']
    
    return df 