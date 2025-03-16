import streamlit.web.cli as stcli
import sys
import os

# Add the current directory to the Python path
sys.path.insert(0, os.path.abspath("."))

if __name__ == "__main__":
    sys.argv = ["streamlit", "run", "app/main.py"]
    sys.exit(stcli.main()) 