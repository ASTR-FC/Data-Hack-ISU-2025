# 🧊 ISU Short Track Analytics Dashboard

A **Streamlit-based analytics platform** for visualizing and interpreting **short-track speed skating event data**.  
The project transforms raw ISU JSON files into clean CSV datasets and provides an interactive dashboard to explore event statistics, athlete performances, and AI-generated summaries.

---

## 🚀 Features

- 📊 **Interactive Insights** — Filters by country, athlete, and round with sortable tables.
- 🏆 **Leaderboards** — Displays top-performing athletes and countries with live statistics.
- 📈 **Round & Heat Analysis** — View average and best times for each round and heat.
- 🤖 **AI Explainer (Qwen Integration)** — Generates natural-language summaries or stories using Alibaba Cloud's **Qwen LLM**.
- 💡 **Streamlit Interface** — Clean, modern, and data-driven layout with intuitive navigation.

---

## 🧱 Project Structure
```
ice_challenge/
│
├── app/
│   ├── main.py              # Entry point for Streamlit app
│   ├── dashboard.py         # Main dashboard logic
│   ├── data_loader.py       # CSV cleaning and preprocessing
│   └── ai_explainer.py      # Qwen AI integration
│   └── dataset_manager.py   # Responsible for discovering and loading all dataset folders

│
├── processed_datasets/
│   ├── seoul_man/           # Clean event data (Men's competition)
│   └── seoul_woman/         # Clean event data (Women's competition)
│
├── requirements.txt
└── README.md
```

### Dataset Structure

Each event data folder contains:
- `events.csv`
- `rounds.csv`
- `heats.csv`
- `heat_competitors.csv`
- `laps.csv`
- `competitors.csv`

*These CSVs are generated and cleaned from ISU JSON data.*

---

## ⚙️ Installation & Setup

Follow these steps to run the project locally.

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/ASTR-FC/Data-Hack-ISU-2025.git
cd Data-Hack-ISU-2025
```

### 2️⃣ Create a Virtual Environment
```bash
pip install virtualenv
python -m venv .venv
source .venv/bin/activate     # On Windows: .venv\Scripts\activate
```

### 3️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

### 4️⃣ Run the Streamlit App
```bash
streamlit run app/main.py
```

The app will open automatically in your browser at:
```
http://localhost:8501
```

---

## 🤖 AI Explainer — Qwen Integration

The AI Explainer uses **Alibaba Cloud's Qwen** large language model to provide human-like summaries of events, match analyses, or creative storytelling.

### How it works

- The model is connected via the **DashScope** (OpenAI-compatible) API.
- You must have an active **Alibaba Cloud Model Studio** API key.

### Steps to set it up

1. Go to [Model Studio Console (Singapore)](https://dashscope-intl.aliyuncs.com/)
2. Create an API key under **Key Management**
3. Export your API key as an environment variable:
```bash
export DASHSCOPE_API_KEY="your_api_key"
```

The model used by default is `qwen-plus`:
```python
client = OpenAI(
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://dashscope-intl.aliyuncs.com/compatible-mode/v1"
)
```

### Example queries

Once active, you can ask:
- *"Summarize this match."*
- *"Generate a short social media story from this event."*
- *"Who were the top athletes in the 500m race?"*

---

## 📝 License

This project is licensed under the MIT License.

