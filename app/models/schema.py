from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union
from datetime import datetime

class SalesRecord(BaseModel):
    """
    Pydantic model for a single sales record.
    """
    date: datetime
    product: str
    sales_units: int
    revenue: float
    year: int
    month: int
    week: int
    quarter: int
    price_per_unit: float

class SalesQuery(BaseModel):
    """
    Pydantic model for a user query about sales data.
    """
    query_text: str = Field(..., description="The natural language query from the user")
    timestamp: datetime = Field(default_factory=datetime.now, description="Timestamp of the query")

class SalesResponse(BaseModel):
    """
    Pydantic model for the response to a sales query.
    """
    query: str = Field(..., description="The original query from the user")
    response_text: str = Field(..., description="The natural language response to the query")
    data: Optional[Dict[str, Any]] = Field(None, description="Any structured data related to the response")
    timestamp: datetime = Field(default_factory=datetime.now, description="Timestamp of the response")

class ChatMessage(BaseModel):
    """
    Pydantic model for a chat message.
    """
    role: str = Field(..., description="The role of the message sender (user or assistant)")
    content: str = Field(..., description="The content of the message")
    timestamp: datetime = Field(default_factory=datetime.now, description="Timestamp of the message")

class ChatHistory(BaseModel):
    """
    Pydantic model for chat history.
    """
    messages: List[ChatMessage] = Field(default_factory=list, description="List of chat messages")

class SalesForecast(BaseModel):
    """
    Pydantic model for sales forecast.
    """
    product: str
    forecast_units: int
    forecast_revenue: float
    forecast_date: datetime
    confidence_level: float = Field(default=0.8, ge=0.0, le=1.0, description="Confidence level of the forecast") 