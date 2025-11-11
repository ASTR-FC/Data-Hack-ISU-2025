import streamlit as st
from pathlib import Path
from dashboard import Dashboard

st.set_page_config(page_title="ISU Short Track Analytics", layout="wide")

def main():
    data_folder = Path(__file__).resolve().parent.parent / "processed_datasets" / "seoul_man"
    dashboard = Dashboard(data_folder)
    dashboard.run()

if __name__ == "__main__":
    main()
