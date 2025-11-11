import streamlit as st
import pandas as pd
from pathlib import Path

from data_loader import (
    clean_events_dataframe,
    clean_rounds_dataframe,
    clean_heats_dataframe,
    prepare_heat_results,
    prepare_lap_results,
)


class Dashboard:
    """Streamlit dashboard for ISU Short Track Analytics."""

    def __init__(self, data_folder: Path):
        self.data_folder = data_folder
        self.datasets = self._load_all_datasets()

    # =====================================================
    # DATA LOADING
    # =====================================================
    def _load_all_datasets(self):
        """Load all CSV datasets from the given folder."""
        dataset_map = {}
        for csv_file in self.data_folder.glob("*.csv"):
            try:
                df = pd.read_csv(csv_file)
                if "Unnamed: 0" in df.columns:
                    df = df.drop(columns=["Unnamed: 0"])
                dataset_map[csv_file.stem.lower()] = df
            except Exception as e:
                st.warning(f"Could not load {csv_file.name}: {e}")
        return dataset_map

    # =====================================================
    # ENTRY POINT
    # =====================================================
    def run(self):
        """Main entry point for the dashboard."""
        st.sidebar.title("Navigation")
        selected_tab = st.sidebar.radio("Go to:", ["Events"])

        if selected_tab == "Events":
            self._show_events_overview()

    # =====================================================
    # EVENTS OVERVIEW
    # =====================================================
    def _show_events_overview(self):
        """Display list of events and allow navigation to details."""
        st.header("Events")

        events_df = self.datasets.get("events")
        if events_df is None:
            st.error("events.csv not found in the data folder.")
            return

        cleaned_events = clean_events_dataframe(events_df)
        st.dataframe(cleaned_events, use_container_width=True)

        if len(cleaned_events) == 0:
            st.info("No events available.")
            return

        # Assume one event for now (later: clickable table)
        event = cleaned_events.iloc[0]
        event_name = event.get("Event Name", "Unknown Event")
        event_location = event.get("Location", "")
        event_discipline = event.get("Discipline", "")

        if st.button(f"View Details for {event_name} ({event_discipline}) in {event_location}"):
            self._show_event_details(event_name)

    # =====================================================
    # EVENT DETAILS (TABS)
    # =====================================================
    def _show_event_details(self, event_name: str):
        """Display detailed tabs for the selected event."""
        st.subheader(f"Event Details: {event_name}")

        tabs = st.tabs(["Rounds", "Heats", "Heat Competitors", "Laps"])

        # ---------------- ROUNDS ----------------
        with tabs[0]:
            rounds_df = self.datasets.get("rounds")
            if rounds_df is not None:
                cleaned_rounds = clean_rounds_dataframe(rounds_df)
                st.subheader("Rounds Overview")
                st.dataframe(cleaned_rounds, use_container_width=True)
                st.markdown(f"**Total Rounds:** {len(cleaned_rounds)}")
            else:
                st.info("No rounds data available.")

        # ---------------- HEATS ----------------
        with tabs[1]:
            heats_df = self.datasets.get("heats")
            if heats_df is not None:
                cleaned_heats = clean_heats_dataframe(heats_df)
                st.subheader("Heats Overview")
                st.dataframe(cleaned_heats, use_container_width=True)
                st.markdown(f"**Total Heats:** {len(cleaned_heats)}")
            else:
                st.info("No heats data available.")

        # ---------------- HEAT COMPETITORS ----------------
        with tabs[2]:
            heat_competitors_df = self.datasets.get("heat_competitors")
            competitors_df = self.datasets.get("competitors")

            if heat_competitors_df is not None and competitors_df is not None:
                prepared_heat_results = prepare_heat_results(heat_competitors_df, competitors_df)
                st.subheader("Heat Competitors Overview")
                st.dataframe(prepared_heat_results, use_container_width=True)
                st.markdown(f"**Total Heat Entries:** {len(prepared_heat_results)}")
            else:
                st.info("Missing either heat_competitors.csv or competitors.csv.")

        # ---------------- LAPS ----------------
        with tabs[3]:
            laps_df = self.datasets.get("laps")
            competitors_df = self.datasets.get("competitors")

            if laps_df is not None and competitors_df is not None:
                prepared_laps = prepare_lap_results(laps_df, competitors_df)
                st.subheader("Laps Overview")
                st.dataframe(prepared_laps, use_container_width=True)
                st.markdown(f"**Total Lap Records:** {len(prepared_laps)}")
            else:
                st.info("Missing laps.csv or competitors.csv.")

