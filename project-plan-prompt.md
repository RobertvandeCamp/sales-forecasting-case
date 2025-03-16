
### **Prompt for Cursor IDE**
**Title:** Generate an AI-Powered Sales Forecasting Chatbot Using Python, Pandas, Pydantic, OpenAI API, and Streamlit  

**Description:**  
Create a **simple AI-driven sales forecasting application** that allows users to query historical sales data using **natural language**. The application should:  
- **Load and preprocess static sales data** from a **pre-existing CSV file**.  
- **Use OpenAI API (GPT-4o) for interactive sales-related queries**.  
- **Implement Pydantic for structured data validation**.  
- **Provide a minimal Streamlit UI** with a **chat-like interface for user interaction**.  

---

### **Technical Requirements:**  
**Tech Stack:**  
✅ **Python** (Main Language)  
✅ **Pandas** (Data Handling)  
✅ **Pydantic** (Data Validation)  
✅ **OpenAI API** (LLM-Powered Queries & Forecasting Assistance)  
✅ **Streamlit** (User Interface for Interaction)  

---

### **Data Setup:**  
- **Pre-existing CSV File:** The application should load and use the following **test sales dataset**:  
  - **Products:**  
    1. Nut & Seed Bars  
    2. Raw & Fruit Bars  
    3. Energy Bars  
  - **Columns:** `Date, Product, Sales_Units, Revenue`  
  - **Sales Data Period:** 12 months of weekly sales data.  

---

### **Application Functionality (Step 1)**
✅ **Load and Preprocess Data**  
   - Read the **static CSV file** into a pandas DataFrame.  
   - Ensure correct **data types, missing value handling, and date parsing**.  

✅ **AI-Powered Chatbot for Sales Forecasting**  
   - Use **OpenAI API** to **interpret user questions** and return relevant insights.  
   - Implement structured **Pydantic models** for handling user queries and responses.  
   - Example Queries:  
     - *"What were the top-selling products last month?"*  
     - *"Predict sales for Energy Bars next week."*  
     - *"Show me the average sales of Nut & Seed Bars in the last 3 months."*  

✅ **Minimal Streamlit UI**  
   - Provide a **chat-like interface** for users to **interact with the AI model**.  
   - Display the **AI-generated responses in a conversation format**.  

**Technical requirements**
Please set up a project with the following structure:
- Use pip for dependency management
- Organize code with clear separation of concerns (UI, business logic, API clients)
- Include comprehensive documentation
- Implement logging with proper levels

---

### **Expected Output from Cursor IDE**
- **Python script to load the sales dataset from CSV**.  
- **Pandas functions to query & filter sales data**.  
- **Streamlit-based chat UI** for AI-powered sales Q&A.  
- **Integration with OpenAI API** to generate dynamic responses.  
- **Basic Pydantic models** for structured query handling.  

---

### **Example AI Chat Interaction**
**User:** *"What were the sales trends for Raw & Fruit Bars last quarter?"*  
**AI Response:** *"Raw & Fruit Bars had an average weekly sale of 1,250 units in Q4, with a peak in December due to seasonal promotions."*  

---

### **Next Steps (Future Enhancements)**
🚀 **Step 2:** Implement **a file uploader** for new sales data.  
📊 **Step 3:** Add **graph-based visualizations** for trends & insights.  

