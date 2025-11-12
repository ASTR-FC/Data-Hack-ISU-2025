import streamlit as st
import pandas as pd
from pathlib import Path
import altair as alt
from app.ai_explainer import ask_qwen


from dataset_manager import DatasetManager

from data_loader import (
    clean_events_dataframe,
    clean_rounds_dataframe,
    clean_heats_dataframe,
    prepare_heat_results,
    prepare_lap_results,
)



# =====================================================
# DASHBOARD
# =====================================================
class Dashboard:
    """Streamlit dashboard for ISU Short Track Analytics."""

    def __init__(self, data_folder: Path):
        self.manager = DatasetManager(data_folder)
        self.datasets = {}

    # ---------------- ENTRY POINT ----------------
    def run(self):
        st.sidebar.title("Event Selection")

        # Automatically detect all event folders
        available_folders = self.manager.list_available_events()
        if not available_folders:
            st.error("No event datasets found under processed_datasets/.")
            return

        # Sidebar: select which dataset to explore
        selected_folder_name = st.sidebar.selectbox(
            "Select the event!",
            [f.name for f in available_folders]
        )

        selected_folder_path = next(
            (f for f in available_folders if f.name == selected_folder_name), None
        )
        if selected_folder_path is None:
            st.error("Invalid dataset folder selected.")
            return

        # Load datasets dynamically
        self.datasets = self.manager.load_datasets_from_folder(selected_folder_path)

        # Continue as before
        self._show_events_overview(selected_folder_name)

    # ---------------- EVENTS OVERVIEW ----------------
    def _show_events_overview(self, folder_name: str):
        st.header(f"Events — {folder_name.replace('_', ' ').title()}")

        events_df = self.datasets.get("events")
        if events_df is None:
            st.error("events.csv not found.")
            return

        cleaned_events = clean_events_dataframe(events_df)
        st.dataframe(cleaned_events, use_container_width=True)

        if len(cleaned_events) == 0:
            st.info("No events available.")
            return

        event = cleaned_events.iloc[0]
        event_name = event.get("Event Name", "Unknown Event")
        event_location = event.get("Location", "")
        event_discipline = event.get("Discipline", "")
        
        if st.button(f"View Details for {event_name} ({event_discipline}) in {event_location}"):
            st.session_state["selected_event"] = event_name

        if "selected_event" in st.session_state:
            self._show_event_details(st.session_state["selected_event"])


    # ---------------- EVENT DETAILS ----------------
    def _show_event_details(self, event_name: str):
        st.subheader(f"Event Details: {event_name}")

        tabs = st.tabs(["Insights", "Rounds", "Heats", "Heat Competitors", "Laps"])

        # -------------- INSIGHTS --------------
        with tabs[0]:
            self._show_event_insights()

        # -------------- ROUNDS --------------
        with tabs[1]:
            rounds_df = self.datasets.get("rounds")
            if rounds_df is not None:
                cleaned_rounds = clean_rounds_dataframe(rounds_df)
                st.dataframe(cleaned_rounds, use_container_width=True)
            else:
                st.info("No rounds data available.")

        # -------------- HEATS --------------
        with tabs[2]:
            heats_df = self.datasets.get("heats")
            if heats_df is not None:
                cleaned_heats = clean_heats_dataframe(heats_df)
                st.dataframe(cleaned_heats, use_container_width=True)
            else:
                st.info("No heats data available.")

        # -------------- HEAT COMPETITORS --------------
        with tabs[3]:
            heat_competitors_df = self.datasets.get("heat_competitors")
            competitors_df = self.datasets.get("competitors")

            if heat_competitors_df is not None and competitors_df is not None:
                prepared_heat_results = prepare_heat_results(
                    heat_competitors_df, competitors_df
                )
                st.dataframe(prepared_heat_results, use_container_width=True)
            else:
                st.info("Missing either heat_competitors.csv or competitors.csv.")

        # -------------- LAPS --------------
        with tabs[4]:
            laps_df = self.datasets.get("laps")
            competitors_df = self.datasets.get("competitors")

            if laps_df is not None and competitors_df is not None:
                prepared_laps = prepare_lap_results(laps_df, competitors_df)
                st.dataframe(prepared_laps, use_container_width=True)
            else:
                st.info("Missing laps.csv or competitors.csv.")

       
        # ---------------- AI EXPLAINER ----------------
        with st.expander("🤖 Ask Qwen to Explain or Summarize"):
            from app.ai_explainer import ask_qwen

        st.caption("💡 Tip: To let Qwen use real event data, include this phrase in your message:")

        st.caption("💡 use match stats - allows the bot to access the match stats, and you can do miracles later!")
        st.code("use match stats", language="text")

        st.caption("💡 summarize match stats   → gives you structured summar of the match")
        st.code("summarize match stats", language="text")

        user_query = st.text_area("Ask about the event, heats, or athletes, or whatever else you want!:")

        if st.button("Ask Qwen"):
            query_lower = user_query.lower()

            # Determine if we should attach data
            attach_data = any(key in query_lower for key in ["use match stats", "summarize match stats"])

            if attach_data:
                heat_df = self.datasets.get("heat_competitors")
                competitors_df = self.datasets.get("competitors")

                if heat_df is not None and competitors_df is not None:
                    combined_df = heat_df.merge(
                        competitors_df,
                        how="left",
                        left_on="competition_competitor_id",
                        right_on="competition_competitor_id"
                    )

                    # Limit to top 10 rows for performance
                    combined_df = combined_df.head(10)

                    # Convert dataset into readable natural text (not hardcoded instructions)
                    summary_lines = []
                    for _, row in combined_df.iterrows():
                        summary_lines.append(
                            f"{row.get('first_name', '')} {row.get('last_name', '')} from "
                            f"{row.get('started_for_nf_country_name', 'N/A')} ranked {row.get('final_rank', '?')} "
                            f"with {row.get('final_result', '—')} seconds in {row.get('round_name', '—')} "
                            f"({row.get('heat_name', '—')})."
                        )
                    text_data = "\n".join(summary_lines)

                    # Inject event data only — no extra system guidance
                    prompt = f"""
    {user_query}

    Here is event data (top 10 rows) you can use to answer the question naturally:
    {text_data}
    """
                    st.write(ask_qwen(prompt))
                else:
                    st.warning("Event data not available for this view.")
            else:
                # No data context — regular chat
                st.write(ask_qwen(user_query))


                
                
    # =====================================================
    # INSIGHTS TAB
    # =====================================================
    def _show_event_insights(self):
        """Interactive statistics and filters for event overview."""

        heat_competitors_df = self.datasets.get("heat_competitors")
        competitors_df = self.datasets.get("competitors")

        if heat_competitors_df is None or competitors_df is None:
            st.info("Insights require both competitors and heat_competitors datasets.")
            return

        df_heat_results = prepare_heat_results(heat_competitors_df, competitors_df)

        # -------- OVERVIEW METRICS --------
        st.markdown("### General Overview")
        total_competitors = competitors_df.shape[0]
        total_heats = heat_competitors_df["heat_name"].nunique()
        total_rounds = heat_competitors_df["round_name"].nunique()

        col1, col2, col3 = st.columns(3)
        col1.metric("Total Competitors", total_competitors)
        col2.metric("Total Heats", total_heats)
        col3.metric("Total Rounds", total_rounds)

        st.divider()

        # -------- AVERAGE & BEST TIMES --------
        st.subheader("Average and Best Race Time per Round")
        df_heat_results["Result (s)"] = pd.to_numeric(df_heat_results["Result (s)"], errors="coerce")
        round_stats = (
            df_heat_results.groupby("Round Name", as_index=False)
            .agg(Average_Time=("Result (s)", "mean"),
                 Best_Time=("Result (s)", "min"),
                 Heats=("Heat Name", "nunique"))
        )
        st.dataframe(
            round_stats.style.format({"Average_Time": "{:.3f}", "Best_Time": "{:.3f}"}),
            use_container_width=True
        )

        st.divider()

        # -------- FILTER BY COUNTRY --------
        st.subheader("Filter by Country")
        countries = sorted(competitors_df["started_for_nf_country_name"].dropna().unique())
        selected_country = st.selectbox("Select a Country", countries)

        filtered_by_country = df_heat_results.query("Country == @selected_country").reset_index(drop=True)  

        st.dataframe(filtered_by_country, use_container_width=True)

        st.divider()

        # -------- FILTER BY ATHLETE --------
        st.subheader("Filter by Athlete")
        athletes = sorted(df_heat_results["Athlete"].dropna().unique())
        selected_athletes = st.multiselect("Select Athlete(s)", athletes)

        if selected_athletes:
            filtered_by_athlete = df_heat_results.query("Athlete in @selected_athletes")
            st.dataframe(
                filtered_by_athlete.sort_values(["Round Name", "Heat Name", "Rank"]),
                use_container_width=True
            )

        st.divider()

        # -------- QUALIFICATION & PENALTY --------
        st.subheader("Qualification & Penalty Summary")
        col1, col2 = st.columns(2)

        qual_counts = df_heat_results["Qualification"].value_counts().reset_index()
        qual_counts.columns = ["Qualification", "Count"]
        status_counts = df_heat_results["Status"].value_counts().reset_index()
        status_counts.columns = ["Status", "Count"]

        with col1:
            st.markdown("**Qualification Codes**")
            st.dataframe(qual_counts, use_container_width=True)
        with col2:
            st.markdown("**Result Status / Penalties**")
            st.dataframe(status_counts, use_container_width=True)

    
        # ---------------- INSIGHTS ----------------
        st.subheader("Event Insights")

        heat_competitors_df = self.datasets.get("heat_competitors")
        competitors_df = self.datasets.get("competitors")

        if heat_competitors_df is not None and competitors_df is not None:
            df_heat_results = prepare_heat_results(heat_competitors_df, competitors_df)

            # Convert numeric results safely
            df_heat_results["Result (s)"] = pd.to_numeric(df_heat_results["Result (s)"], errors="coerce")
            df_heat_results["Rank"] = pd.to_numeric(df_heat_results["Rank"], errors="coerce")

            # =====================================================
            # Winner Summary
            # =====================================================
            best_result = df_heat_results.sort_values("Result (s)", ascending=True).dropna(subset=["Result (s)"]).head(1)
            if not best_result.empty:
                winner = best_result.iloc[0]
                st.markdown(
                    f"🏆 **Winner:** {winner['Athlete']} ({winner['Country']}) — "
                    f"**{winner['Result (s)']:.3f} seconds**, Rank {int(winner['Rank'])}"
                )
            else:
                st.info("No valid results found to identify winner.")

            # =====================================================
            # Athlete Leaderboard (Top 10 Fastest)
            # =====================================================
            st.markdown("### Top 10 Fastest Athletes")
            top_athletes = (
                df_heat_results.dropna(subset=["Result (s)"])
                .sort_values("Result (s)", ascending=True)
                .head(10)
                .reset_index(drop=True)
            )

            st.dataframe(
                top_athletes[["Athlete", "Country", "Result (s)", "Rank", "Round Name", "Heat Name"]].reset_index(drop=True),
                use_container_width=True
            )


            # =====================================================
            #  Country Leaderboard (Average Rank)
            # =====================================================
            st.markdown("### Country Leaderboard — Average Rank")
            country_rank = (
                df_heat_results.dropna(subset=["Rank"])
                .groupby("Country", as_index=False)
                .agg(Average_Rank=("Rank", "mean"), Participants=("Athlete", "count"))
                .sort_values("Average_Rank", ascending=True)
            )

            st.dataframe(
                 country_rank.reset_index(drop=True),
                 use_container_width=True
                )


        else:
            st.info("Insights unavailable: missing competitors or heat data.")



