import streamlit as st
from pathlib import Path
from dashboard import Dashboard

# Set page config
st.set_page_config(
    page_title="ISU Short Track Analytics",
    layout="wide",
    page_icon="🧊"  # Ice skate emoji as favicon
)

# --- Custom background with radial gradient (dark edges) ---
page_bg = """
<style>
    [data-testid="stAppViewContainer"] {
        background: radial-gradient(
            circle at center,
            rgba(1, 203, 217, 0.5) 0%,     /* Lighter cyan-blue at center */
            rgba(1, 203, 217, 0.4) 40%,    /* Fade to softer mid-tone */
            rgba(1, 150, 180, 0.3) 70%,    /* Darker blue-teal transition */
            rgba(15, 30, 45, 0.95) 100%    /* Dark blue-black at edges */
        );
    }
    [data-testid="stHeader"] {
        background: rgba(255, 255, 255, 0); /* Transparent header */
    }
    [data-testid="stSidebar"] {
        background: linear-gradient(
            to bottom,
            rgba(1, 203, 217, 0.15),       /* Cyan tint at top */
            rgba(15, 30, 45, 0.9)          /* Dark blue-black at bottom */
        );
    }
    
    /* Logo in top-left corner */
    .logo-container {
        position: fixed;
        top: 20px;
        left: 20px;
        z-index: 999;
        background: rgba(15, 30, 45, 0.85); /* Dark blue-black background */
        padding: 10px;
        border-radius: 10px;
        box-shadow: 0 2px 12px rgba(1, 203, 217, 0.3); /* Cyan glow */
        backdrop-filter: blur(10px);
        border: 1px solid rgba(1, 203, 217, 0.3); /* Subtle cyan border */
    }
    .logo-container img {
        width: 120px;
        height: auto;
        display: block;
    }
</style>
"""
st.markdown(page_bg, unsafe_allow_html=True)

# --- Add logo in top-left corner ---
logo_path = Path("images/think_sport_logo.jpeg")
if logo_path.exists():
    # Convert image to base64 for embedding
    import base64
    with open(logo_path, "rb") as img_file:
        logo_base64 = base64.b64encode(img_file.read()).decode()
    
    logo_html = f"""
    <div class="logo-container">
        <img src="data:image/jpeg;base64,{logo_base64}" alt="Think Sport Logo">
    </div>
    """
    st.markdown(logo_html, unsafe_allow_html=True)


def main():
    # Define the base folder where all datasets are stored
    data_folder = Path("processed_datasets")

    # Initialize and run the dashboard
    dashboard = Dashboard(data_folder)
    dashboard.run()

if __name__ == "__main__":
    main()