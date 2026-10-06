# 🌾 AgriPlan: Digital Crop Calendar & Action Scheduler

AgriPlan is a responsive, modern Streamlit web application designed for farmers, agronomists, and agricultural extension officers. It automatically turns a sowing or planting date into an actionable, stage-by-stage farming timeline covering fertilization, irrigation, weeding, pest scouting, and harvesting.

---

## ✨ Features

- **Dynamic Date Scheduling**: Computes exact calendar dates for every crop growth stage relative to sowing date.
- **Real-Time Stage Status**: Automatic task status badges (`🟢 Completed`, `🟠 Due Today`, `🔵 Upcoming`) based on current date.
- **Interactive Gantt Chart**: Built with Plotly to visualize overlapping agricultural operations across months, with a live reference marker for **Today**.
- **Bonus Fertilizer & Seed Estimator**:
  - Calculates certified seed requirement for user's acreage.
  - Computes elemental N-P-K nutrient requirements.
  - Automatically breaks down commercial fertilizer purchase counts (number of standard 50kg bags of **Urea**, **DAP**, and **MOP**).
- **Multi-Crop Database**: Preconfigured with agronomic templates for **Tomato**, **Paddy (Rice)**, **Wheat**, **Maize (Corn)**, and **Potato**.
- **Search & Filtering**: Filter activities by operational category (Fertilizer, Irrigation, Sowing, Maintenance, etc.) or task status.
- **Spreadsheet & CSV Export**: Download the customized crop calendar with one click for offline use or printing.

---

## 📁 Directory Structure

```text
agri_crop_calendar/
├── data/
│   └── crops.json             # Crop database (growth duration, stages, offsets, seed & NPK rates)
├── utils/
│   ├── calculator.py          # Date math & timeline schedule generator
│   └── fertilizer.py          # Fertilizer & seed estimator logic
├── app.py                     # Main Streamlit dashboard UI
├── requirements.txt           # Python package dependencies
└── README.md                  # Project documentation & run guide
```

---

## 🚀 Quickstart Guide

### 1. Prerequisites
- Python 3.10+ installed.

### 2. Setup Virtual Environment

**Windows (PowerShell):**
```powershell
# Navigate to the project directory
cd "C:\Users\ASUS\.gemini\antigravity\scratch\agri_crop_calendar"

# Create a virtual environment
python -m venv .venv

# Activate the virtual environment
.\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

**macOS / Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Launch the Application

```bash
streamlit run app.py
```

The app will open automatically in your browser at `http://localhost:8501`.

---

## 🛠️ Adding New Crops

To add custom crops or regional varieties, simply edit [crops.json](file:///C:/Users/ASUS/.gemini/antigravity/scratch/agri_crop_calendar/data/crops.json) by adding an entry:

```json
"Cotton": {
  "growth_duration_days": 160,
  "seed_rate_kg_per_acre": 2.5,
  "seed_unit": "kg",
  "npk_kg_per_acre": { "N": 50, "P": 25, "K": 25 },
  "description": "Long-duration cash crop requiring warm temperatures and pest scouting.",
  "stages": [
    {
      "stage": "Land Prep & Sowing",
      "day_offset": 0,
      "duration_days": 7,
      "action": "Sow seeds at 90x60cm spacing with basal fertilizer.",
      "category": "Sowing",
      "details": "Ensure soil temperature exceeds 18°C."
    }
  ]
}
```

---

## 📜 License
Open-source under the MIT License.
