# AI-Powered Sales Forecasting Chatbot

This application is an AI-driven sales forecasting chatbot that allows users to query historical sales data using natural language. It uses OpenAI's GPT-4o model to process and respond to user queries about sales data.

## Features

- Load and preprocess sales data from a CSV file
- Query sales data using natural language
- Get AI-powered insights and forecasts
- Chat-like interface for user interaction

## Tech Stack

- **Python**: Main programming language
- **Pandas**: Data handling and analysis
- **Pydantic**: Data validation and settings management
- **OpenAI API**: Natural language processing and AI responses
- **Streamlit**: User interface

## Project Structure

```
sales-forecasting-case/
├── app/
│   ├── api/
│   │   └── openai_client.py    # OpenAI API integration
│   ├── data/
│   │   └── sales_data.csv      # Sample sales data
│   ├── models/
│   │   └── schema.py           # Pydantic models
│   ├── ui/
│   │   └── chat_interface.py   # Streamlit UI components
│   ├── utils/
│   │   ├── data_loader.py      # Data loading and preprocessing
│   │   └── logger.py           # Logging setup
│   └── main.py                 # Application main logic
├── main.py                     # Application entry point
├── .env.example                # Example environment variables
└── requirements.txt            # Project dependencies
```

## Setup and Installation

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Create a `.env` file based on `.env.example` and add your OpenAI API key:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ```
5. Run the application:
   ```bash
   streamlit run main.py
   ```

## Usage

1. Enter queries about the sales data in the chat interface, such as:
   - "What were the top-selling products last month?"
   - "Predict sales for Energy Bars next week."
   - "Show me the average sales of Nut & Seed Bars in the last 3 months."
2. View the AI-generated responses in the conversation format

## Future Enhancements

- File uploader for new sales data
- Graph-based visualizations for trends & insights 