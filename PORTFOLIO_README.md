# 🇸🇦 Saudi Workforce Analytics Suite
## A 4-Tier Analytics Portfolio on KSA Labour Market & Nitaqat Compliance

> **Built for the KSA job market.** Four production-ready Streamlit apps covering the complete analytics stack — from descriptive dashboards to LP optimization — applied to Saudi Arabia's most consequential HR policy framework.

---

## 🗺️ The Suite at a Glance

| App | Tier | Question Answered | Key Tech | Live Demo |
|---|---|---|---|---|
| [App 1 — Workforce Intelligence](./saudi-workforce-descriptive/) | **Descriptive** | *What* does the Saudi workforce look like? | Plotly, Pandas | [![Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](#) |
| [App 2 — Root Cause Analyzer](./saudi-workforce-diagnostic/) | **Diagnostic** | *Why* are companies failing Nitaqat? | Root-cause scoring, heatmaps | [![Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](#) |
| [App 3 — Breach Predictor](./saudi-workforce-predictive/) | **Predictive** | *Will* a company breach compliance? | Random Forest, Gradient Boosting, LR | [![Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](#) |
| [App 4 — Hiring Optimizer](./saudi-workforce-prescriptive/) | **Prescriptive** | *What* should a company hire? | Linear Programming (scipy HiGHS) | [![Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](#) |

---

## 🎯 Why This Portfolio Stands Out

### The Domain Angle
Most analytics portfolios: Titanic survival, Iris classification, Netflix recommendations.

This portfolio: **Saudi Nitaqat compliance** — a live, billion-riyal regulatory framework that every HR director, HRSD official, and management consultant in the GCC works with daily. Domain relevance signals that you understand the *context* of data, not just the mechanics.

### The Full Analytics Stack
The four apps demonstrate all four maturity levels of analytics:

```
Descriptive  → "What happened?"     → Dashboards, KPIs, distributions
Diagnostic   → "Why did it happen?" → Root cause scoring, decomposition
Predictive   → "What will happen?"  → ML classifiers, ROC/PR curves
Prescriptive → "What should we do?" → Linear programming, scenario analysis
```

Most candidates show 1–2 levels. This suite shows all four, on the same domain.

### Technical Breadth
- **Data Engineering**: Synthetic dataset calibrated to real GASTAT/HRSD statistics
- **Visualisation**: 35+ interactive Plotly charts across 4 apps
- **Machine Learning**: 3-model comparison with stratified CV, threshold analysis, feature importance
- **Operations Research**: Constrained LP with HiGHS solver — rare in data analytics portfolios
- **Deployment**: All 4 apps Streamlit-Cloud-ready with one-click deploy

---

## 📁 Repository Structure

```
saudi-workforce-analytics/
│
├── README.md                          ← this file
│
├── saudi-workforce-descriptive/       ← App 1
│   ├── app.py
│   ├── generate_data.py               ← run once to create the shared CSV
│   ├── saudi_workforce_data.csv       ← 5,000 employees, 47 companies
│   ├── requirements.txt
│   └── README.md
│
├── saudi-workforce-diagnostic/        ← App 2
│   ├── app.py
│   ├── saudi_workforce_data.csv       ← shared dataset (copy from App 1)
│   ├── requirements.txt
│   └── README.md
│
├── saudi-workforce-predictive/        ← App 3
│   ├── app.py
│   ├── saudi_workforce_data.csv
│   ├── requirements.txt
│   └── README.md
│
└── saudi-workforce-prescriptive/      ← App 4
    ├── app.py
    ├── saudi_workforce_data.csv
    ├── requirements.txt
    └── README.md
```

---

## 🚀 Deploy All 4 Apps to Streamlit Cloud

Each app deploys independently — you get 4 separate live URLs.

### Step 1 — Push to GitHub
```bash
git init saudi-workforce-analytics
cd saudi-workforce-analytics
# copy all 4 app folders in
git add .
git commit -m "Initial commit: 4-tier Saudi workforce analytics suite"
git remote add origin https://github.com/YOUR_USERNAME/saudi-workforce-analytics.git
git push -u origin main
```

### Step 2 — Deploy each app on Streamlit Cloud
1. Go to [share.streamlit.io](https://share.streamlit.io)
2. "New app" → select repo → set **Main file path** to e.g. `saudi-workforce-descriptive/app.py`
3. Repeat for all 4 apps → get 4 live URLs

### Step 3 — Add to CV
```
Saudi Workforce Analytics Suite (4 Streamlit apps)
  ├── [Descriptive] share.streamlit.io/...
  ├── [Diagnostic]  share.streamlit.io/...
  ├── [Predictive]  share.streamlit.io/...
  └── [Prescriptive] share.streamlit.io/...
GitHub: github.com/YOUR_USERNAME/saudi-workforce-analytics
```

---

## 🏃 Run Locally (All Apps)

```bash
# Clone
git clone https://github.com/YOUR_USERNAME/saudi-workforce-analytics.git
cd saudi-workforce-analytics

# Generate dataset (only needed once)
cd saudi-workforce-descriptive
pip install -r requirements.txt
python generate_data.py

# Copy CSV to other apps
cp saudi_workforce_data.csv ../saudi-workforce-diagnostic/
cp saudi_workforce_data.csv ../saudi-workforce-predictive/
cp saudi_workforce_data.csv ../saudi-workforce-prescriptive/

# Run any app
streamlit run app.py                          # App 1
cd ../saudi-workforce-diagnostic && streamlit run app.py   # App 2
# etc.
```

---

## 📊 Dataset Overview

| Attribute | Value |
|---|---|
| Records | 5,000 employees |
| Companies | 47 across 10 sectors |
| Regions | 10 Saudi regions |
| Nationalities | 12 |
| Date range | 2015–2023 |
| Calibration | GASTAT Labour Force Survey + HRSD Nitaqat targets |

---

## 🔗 Vision 2030 Alignment

| V2030 Pillar | How This Suite Contributes |
|---|---|
| **Thriving Economy** | Labour market efficiency analysis, Saudization optimisation |
| **Vibrant Society** | Female workforce participation tracking |
| **Ambitious Nation** | Data-driven governance tools for regulatory bodies |

---

## 📄 License

MIT — open for use, adaptation, and extension.

---

*All data is synthetic. Generated to reflect the structural patterns of the Saudi labour market based on publicly available GASTAT and HRSD statistics. No real company, employee, or salary data is used.*
