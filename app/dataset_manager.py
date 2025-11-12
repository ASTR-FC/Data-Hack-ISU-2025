# =====================================================
# DATASET MANAGER
# ====================================================

from pathlib import Path
import pandas as pd
import streamlit as st


class DatasetManager:
    """Responsible for discovering and loading all dataset folders."""

    def __init__(self, base_data_folder: Path):
        self.base_data_folder = base_data_folder

    def list_available_events(self):
        """Return all subfolders under processed_datasets."""
        return [f for f in self.base_data_folder.iterdir() if f.is_dir()]

    def load_datasets_from_folder(self, folder: Path):
        """Load all CSVs from a given folder into a dict."""
        dataset_map = {}
        for csv_file in folder.glob("*.csv"):
            try:
                df = pd.read_csv(csv_file)
                if "Unnamed: 0" in df.columns:
                    df = df.drop(columns=["Unnamed: 0"])
                dataset_map[csv_file.stem.lower()] = df
            except Exception as e:
                st.warning(f"Could not load {csv_file.name}: {e}")
        return dataset_map

