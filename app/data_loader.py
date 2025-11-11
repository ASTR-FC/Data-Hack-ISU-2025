import pandas as pd


# ===================== UTILITY =====================
def _format_datetime(value):
    """Format start_date as DD/MM/YYYY – HH:MM."""
    try:
        timestamp = pd.to_datetime(value)
        return timestamp.strftime("%d/%m/%Y – %H:%M")
    except Exception:
        return None


# ===================== EVENTS =====================
def clean_events_dataframe(events_df: pd.DataFrame) -> pd.DataFrame:
    """Clean and simplify events.csv."""
    df = events_df.copy()

    # Drop technical or redundant columns
    drop_columns = [
        "event_id", "discipline_distance", "sport_code",
        "gender", "status", "start_year", "start_month",
        "start_day", "start_hour", "start_minute", "time_zone"
    ]
    df = df.drop(columns=[c for c in drop_columns if c in df.columns], errors="ignore")

    # Rename columns for clarity
    df = df.rename(columns={
        "event_name": "Event Name",
        "discipline_name": "Discipline"
    })

    # Format datetime
    df["Start Time"] = df["start_date"].apply(_format_datetime)
    df = df.drop(columns=["start_date"], errors="ignore")

    # Extract location (e.g. "seoul" from "seoul_man")
    if "json_source" in df.columns:
        df["Location"] = df["json_source"].apply(
            lambda x: str(x).split("_")[0].capitalize() if pd.notna(x) else ""
        )
        df = df.drop(columns=["json_source"], errors="ignore")

    # Reorder columns
    ordered_columns = ["Event Name", "Discipline", "Start Time", "Location"]
    return df[[c for c in ordered_columns if c in df.columns]]


# ===================== ROUNDS =====================
def clean_rounds_dataframe(rounds_df: pd.DataFrame) -> pd.DataFrame:
    """Clean and simplify rounds.csv."""
    df = rounds_df.copy()

    drop_columns = [
        "state", "start_year", "start_month", "start_day",
        "start_hour", "start_minute", "time_zone"
    ]
    df = df.drop(columns=[c for c in drop_columns if c in df.columns], errors="ignore")

    # Format time
    df["Start Time"] = df["start_date"].apply(_format_datetime)
    df = df.drop(columns=["start_date"], errors="ignore")

    # Add location
    if "json_source" in df.columns:
        df["Location"] = df["json_source"].apply(
            lambda x: str(x).split("_")[0].capitalize()
        )
        df = df.drop(columns=["json_source"], errors="ignore")

    # Rename and reorder
    df = df.rename(columns={
        "round_name": "Round Name",
        "display_order": "Order",
        "num_heats": "Heats"
    })

    keep_columns = ["Round Name", "Order", "Heats", "Start Time", "Location"]
    return df[[c for c in keep_columns if c in df.columns]]


# ===================== HEATS =====================
def clean_heats_dataframe(heats_df: pd.DataFrame) -> pd.DataFrame:
    """Clean and simplify heats.csv."""
    df = heats_df.copy()

    drop_columns = [
        "heat_id", "status", "result_status", "photo",
        "start_year", "start_month", "start_day",
        "start_hour", "start_minute", "time_zone"
    ]
    df = df.drop(columns=[c for c in drop_columns if c in df.columns], errors="ignore")

    df["Start Time"] = df["start_date"].apply(_format_datetime)
    df = df.drop(columns=["start_date"], errors="ignore")

    if "json_source" in df.columns:
        df["Location"] = df["json_source"].apply(
            lambda x: str(x).split("_")[0].capitalize()
        )
        df = df.drop(columns=["json_source"], errors="ignore")

    df = df.rename(columns={
        "round_name": "Round Name",
        "heat_name": "Heat Name",
        "num_competitors": "Competitors",
        "display_order": "Order"
    })

    keep_columns = ["Round Name", "Heat Name", "Competitors", "Order", "Start Time", "Location"]
    return df[[c for c in keep_columns if c in df.columns]]



# ===================== HEAT COMPETITORS =====================
def prepare_heat_results(heat_competitors_df: pd.DataFrame, competitors_df: pd.DataFrame) -> pd.DataFrame:
    """Join heat competitors with athlete names and expand qualification codes into readable form."""

    df = heat_competitors_df.copy()
    competitors = competitors_df.copy()

    # ---- Detect correct join column ----
    possible_keys = ["competition_competitor_id", "competitor_id", "id"]
    join_key = next((key for key in possible_keys if key in df.columns and key in competitors.columns), None)

    # ---- Coerce IDs to string to avoid dtype mismatch ----
    if join_key:
        df[join_key] = df[join_key].astype(str)
        competitors[join_key] = competitors[join_key].astype(str)

    if join_key is None:
        df["Athlete"] = "Unknown"
        df["Country"] = "—"
    else:
        available_cols = [c for c in ["first_name", "last_name", "started_for_nf_country_name"] if c in competitors.columns]
        competitors_subset = competitors[[join_key] + available_cols]

        merged = df.merge(competitors_subset, on=join_key, how="left")

        # ---- Name + Country ----
        merged["Athlete"] = (
            merged["first_name"].fillna("").str.title() + " " +
            merged["last_name"].fillna("").str.upper()
        ).str.strip()
        merged["Country"] = merged.get("started_for_nf_country_name", "—")
        df = merged

    # ---- Qualification codes ----
    qualification_map = {
        "Q": "Qualified automatically (top places)",
        "QA": "Qualified as best time (fastest loser)",
        "ADV": "Advanced by referee decision",
        "PEN": "Penalized / disqualified",
        "q": "Qualified automatically (lower heat)",
        "—": "Not classified",
    }
    df["qualification_code"] = df["qualification_code"].map(qualification_map).fillna("—")

    # ---- Rename and reorder ----
    rename_map = {
        "round_name": "Round Name",
        "heat_name": "Heat Name",
        "final_rank": "Rank",
        "final_result": "Result (s)",
        "num_laps": "Laps",
        "qualification_code": "Qualification",
        "result_status": "Status",
    }
    df = df.rename(columns=rename_map)

    keep_cols = [
        "Round Name", "Heat Name", "Athlete", "Country",
        "Rank", "Result (s)", "Laps", "Qualification", "Status"
    ]
    return df[[c for c in keep_cols if c in df.columns]]

# ====================== LAPS =====================
def prepare_lap_results(laps_df: pd.DataFrame, competitors_df: pd.DataFrame) -> pd.DataFrame:
    """Join laps with competitor info for readable athlete-based lap tables."""

    if laps_df is None or competitors_df is None:
        return pd.DataFrame()

    df = laps_df.copy()
    competitors = competitors_df.copy()

    # --- Detect join key (same logic as before) ---
    possible_keys = ["competition_competitor_id", "competitor_id", "id"]
    join_key = next((key for key in possible_keys if key in df.columns and key in competitors.columns), None)

    # --- Coerce to string ---
    if join_key:
        df[join_key] = df[join_key].astype(str).replace("nan", "")
        competitors[join_key] = competitors[join_key].astype(str).replace("nan", "")

    # --- Merge and compose readable names ---
    if join_key:
        available_cols = [c for c in ["first_name", "last_name", "started_for_nf_country_name"] if c in competitors.columns]
        subset = competitors[[join_key] + available_cols]
        merged = df.merge(subset, on=join_key, how="left")

        merged["Athlete"] = (
            merged["first_name"].fillna("").str.title() + " " +
            merged["last_name"].fillna("").str.upper()
        ).str.strip()
        merged["Country"] = merged.get("started_for_nf_country_name", "—")
        df = merged
    else:
        df["Athlete"] = "Unknown"
        df["Country"] = "—"

    # --- Rename and reorder ---
    df = df.rename(columns={
        "round_name": "Round Name",
        "heat_name": "Heat Name",
        "lap_number": "Lap",
        "rank": "Rank",
        "lap_time": "Lap Time (s)",
        "total_time": "Total Time (s)",
        "result_difference": "Diff (s)"
    })

    keep_cols = [
        "Round Name", "Heat Name", "Athlete", "Country",
        "Lap", "Rank", "Lap Time (s)", "Total Time (s)", "Diff (s)"
    ]
    return df[[c for c in keep_cols if c in df.columns]]
