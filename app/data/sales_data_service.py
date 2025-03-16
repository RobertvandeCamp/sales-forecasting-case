import pandas as pd
import json
from app.utils.logger import get_logger

# Initialize logger
logger = get_logger()

def generate_sales_data_summary(sales_data: pd.DataFrame) -> dict:
    """
    Generate a summary of the sales data to provide context to the OpenAI model.
    
    Args:
        sales_data (pd.DataFrame): The sales data
        
    Returns:
        dict: Summary of the sales data
    """
    try:
        summary = {
            "data_period": {
                "start_date": sales_data['Date'].min().strftime('%Y-%m-%d'),
                "end_date": sales_data['Date'].max().strftime('%Y-%m-%d')
            },
            "products": sales_data['Product'].unique().tolist(),
            "total_records": len(sales_data),
            "product_statistics": {}
        }
        
        # Add statistics for each product
        for product in summary["products"]:
            product_data = sales_data[sales_data['Product'] == product]
            summary["product_statistics"][product] = {
                "total_sales_units": int(product_data['Sales_Units'].sum()),
                "total_revenue": float(product_data['Revenue'].sum()),
                "average_sales_units_per_week": float(product_data['Sales_Units'].mean()),
                "average_revenue_per_week": float(product_data['Revenue'].mean()),
                "average_price_per_unit": float(product_data['Price_Per_Unit'].mean())
            }
        
        # Add monthly trends
        monthly_sales = sales_data.groupby(['Year', 'Month', 'Product'])['Sales_Units'].sum().reset_index()
        summary["monthly_trends"] = {}
        
        for year in monthly_sales['Year'].unique():
            summary["monthly_trends"][int(year)] = {}
            for month in range(1, 13):
                month_data = monthly_sales[(monthly_sales['Year'] == year) & (monthly_sales['Month'] == month)]
                if not month_data.empty:
                    summary["monthly_trends"][int(year)][int(month)] = {}
                    for product in summary["products"]:
                        product_month_data = month_data[month_data['Product'] == product]
                        if not product_month_data.empty:
                            summary["monthly_trends"][int(year)][int(month)][product] = int(product_month_data['Sales_Units'].values[0])
        
        # Add quarterly trends
        quarterly_sales = sales_data.groupby(['Year', 'Quarter', 'Product'])['Sales_Units'].sum().reset_index()
        summary["quarterly_trends"] = {}
        
        for year in quarterly_sales['Year'].unique():
            summary["quarterly_trends"][int(year)] = {}
            for quarter in range(1, 5):
                quarter_data = quarterly_sales[(quarterly_sales['Year'] == year) & (quarterly_sales['Quarter'] == quarter)]
                if not quarter_data.empty:
                    summary["quarterly_trends"][int(year)][int(quarter)] = {}
                    for product in summary["products"]:
                        product_quarter_data = quarter_data[quarter_data['Product'] == product]
                        if not product_quarter_data.empty:
                            summary["quarterly_trends"][int(year)][int(quarter)][product] = int(product_quarter_data['Sales_Units'].values[0])
        
        logger.info("Sales data summary generated successfully")
        logger.info(f"Sales data summary: {json.dumps(summary, indent=2)}")

        return summary
        
    except Exception as e:
        logger.error(f"Error generating sales data summary: {str(e)}")
        raise