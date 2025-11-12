import streamlit as st
from pathlib import Path
from dashboard import Dashboard

def main():
    # Set up Streamlit page configuration
    st.set_page_config(page_title="ISU Short Track Analytics", layout="wide")

    # Define the base folder where all datasets are stored
    data_folder = Path("processed_datasets")

    # Initialize and run the dashboard
    dashboard = Dashboard(data_folder)
    dashboard.run()

if __name__ == "__main__":
    main()
