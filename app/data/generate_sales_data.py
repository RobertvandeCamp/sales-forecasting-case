import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

def generate_sales_data():
    # Set seed for reproducibility
    np.random.seed(42)
    
    # Define products
    products = ['Nut & Seed Bars', 'Raw & Fruit Bars', 'Energy Bars']
    
    # Base prices per unit for each product
    base_prices = {
        'Nut & Seed Bars': 5.0,
        'Raw & Fruit Bars': 4.5,
        'Energy Bars': 4.5
    }
    
    # Base weekly sales for each product (starting point)
    base_sales = {
        'Nut & Seed Bars': 800,
        'Raw & Fruit Bars': 1000,
        'Energy Bars': 1200
    }
    
    # Define seasonal factors (quarterly influence)
    # Q1: Winter, Q2: Spring, Q3: Summer, Q4: Fall
    seasonal_factors = {
        'Nut & Seed Bars':  [1.0, 1.1, 0.9, 1.2],  # Higher in Spring and Fall
        'Raw & Fruit Bars': [0.8, 1.2, 1.3, 0.9],  # Higher in Summer
        'Energy Bars':      [1.1, 1.0, 1.2, 0.9]   # Higher in Winter and Summer
    }
    
    # Create date range for 52 weeks (starting from Jan 1, 2024)
    start_date = datetime(2024, 1, 1)
    dates = [start_date + timedelta(days=i*7) for i in range(52)]
    
    # Prepare data lists
    data = []
    
    # Generate sales data with trends
    for product in products:
        # Create a linear growth trend (annual growth)
        growth_trend = np.linspace(1.0, 1.15, 52)  # 15% growth over the year
        
        for i, date in enumerate(dates):
            # Determine quarter (0-based)
            quarter = (date.month - 1) // 3
            
            # Calculate base sales with seasonal adjustment and growth trend
            base = base_sales[product]
            seasonal = seasonal_factors[product][quarter]
            trend = growth_trend[i]
            
            # Add some randomness (±10%)
            randomness = random.uniform(0.9, 1.1)
            
            # Calculate final sales units
            sales_units = int(base * seasonal * trend * randomness)
            
            # Calculate revenue with small random price variation
            price_variation = random.uniform(0.98, 1.02)
            unit_price = base_prices[product] * price_variation
            revenue = int(sales_units * unit_price)
            
            # Add to data
            data.append([date.strftime('%Y-%m-%d'), product, sales_units, revenue])
    
    # Create DataFrame
    df = pd.DataFrame(data, columns=['Date', 'Product', 'Sales_Units', 'Revenue'])
    
    # Sort by date
    df = df.sort_values(['Date', 'Product'])
    
    # Save to CSV
    df.to_csv('sales_data.csv', index=False)
    print(f"Generated sales data with {len(df)} records for {len(products)} products over {len(dates)} weeks")
    
    return df

if __name__ == "__main__":
    df = generate_sales_data()
    # Display sample
    print("\nSample data:")
    print(df.head(15)) 