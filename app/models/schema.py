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

class SalesAnalysisResponse(BaseModel):
    """
    Pydantic model the AI response to a sales query.
    """
    response_text: str = Field(
        description="The natural language response to the query"
    )
    class Product(BaseModel):
        name: str = Field(description="Name of a product mentioned in the query")
    products: list[Product]
    time_period: str = Field(
        description="Time period mentioned in the query (e.g., next month, this quarter)"
    )

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

class NewMarketInsights(BaseModel):
    """
    Pydantic model for market insights from the Assistant.
    """
    class MarketTrend(BaseModel):
        trend: str = Field(description="Market trend affecting the product")
        impact: str = Field(description="What is the effect on the product, Positive, Neutral, Negative")
        description: str = Field(description="Description of the trend")
    market_trends: list[MarketTrend]
    class Competitor(BaseModel):
        competitor: str = Field(description="Competitor mentioned in the query")
        action: str = Field(description="Action taken by the competitor")
        impact: str = Field(description="What is the effect on the product, Positive, Neutral, Negative")
        description: str = Field(description="Description of the competitor's action")
    competitive_landscape: list[Competitor]
    class RegulatoryConsideration(BaseModel):
        regulation: str = Field(description="Regulation mentioned in the query")
        timeline: str = Field(description="Timeline of the regulation")
        impact: str = Field(description="What is the effect on the product, Positive, Neutral, Negative")
        description: str = Field(description="Description of the regulation")
    regulatory_considerations: list[RegulatoryConsideration]

class MarketInsights(BaseModel):
    """
    Pydantic model for market insights from the Assistant.
    """
    market_trends: List[Dict[str, str]] = Field(..., description="Market trends affecting the product")
    competitive_landscape: List[Dict[str, str]] = Field(..., description="Competitive landscape analysis")
    regulatory_considerations: List[Dict[str, str]] = Field(..., description="Regulatory considerations")
    
    class Config:
        schema_extra = {
            "example": {
                "market_trends": [
                    {"trend": "Growing fitness awareness", "impact": "Positive", "description": "8% growth in energy bar demand due to fitness trends"}
                ],
                "competitive_landscape": [
                    {"competitor": "NewBar Inc", "action": "Market Entry", "impact": "Negative", "description": "New competitor entered market last month"}
                ],
                "regulatory_considerations": [
                    {"regulation": "Nutrition labeling", "timeline": "Next quarter", "impact": "Neutral", "description": "New nutrition labeling requirements take effect"}
                ]
            }
        }

class AugmentedResponse(BaseModel):
    """
    Pydantic model for an augmented sales response with market insights.
    """
    initial_response: SalesAnalysisResponse = Field(..., description="The initial sales response based on historical data")
    market_insights: NewMarketInsights = Field(..., description="Structured market insights from the Assistant")
    timestamp: datetime = Field(default_factory=datetime.now, description="Timestamp of the augmented response") 

class InventoryResponse(BaseModel):
    answer: str = Field(description="The answer to the user's question.")
    source: str = Field(description="The inventory id of the answer.")

class InventoryResponseSchema:
    inventory_response_json_schema = {
            "format": {
                "type": "json_schema",
                "name": "inventory_response",
                "schema": {
                    "type": "object",
                    "properties": {
                        "answer": {"type": "string"},
                        "source": {"type": "string"},
                    },
                    "required": ["answer", "source"],
                    "additionalProperties": False,
                },
                "strict": True,
            }
        }