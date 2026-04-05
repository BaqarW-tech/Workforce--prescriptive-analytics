# ⚙️ Nitaqat Compliance Hiring Optimizer
### Prescriptive Analytics · Vision 2030 Portfolio Series · App 4 of 4

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://your-app-url.streamlit.app)
![Python](https://img.shields.io/badge/Python-3.10+-blue)
![scipy](https://img.shields.io/badge/scipy-LP%20Optimizer-green)
![Analytics](https://img.shields.io/badge/Analytics-Prescriptive%20LP-brightgreen)

---

## 🎯 Problem This Solves

The previous three apps answered *what*, *why*, and *will it happen*. This app answers the hardest question: **what exactly should we do, and at what cost?**

A company knows it needs more Saudi employees — but *which roles*? How many? At what salary? Over what timeline? Given a fixed budget, what is the mathematically optimal hiring plan that achieves Nitaqat compliance at minimum cost?

This app uses **Linear Programming (LP)** via `scipy.optimize.linprog` to compute the exact answer — not a rule-of-thumb, not a consultant's guess, but a provably optimal allocation.

---

## 🧮 The Optimization Problem

### Decision Variables
`x_i` = number of Saudi nationals to hire in role `i`

### Objective Function
**Minimise:** `Σ (salary_i × x_i)` — total monthly payroll cost of new hires

### Constraints

| Constraint | Formula |
|---|---|
| **Saudization target** | `(current_saudi + Σx_i) / (current_total + Σx_i) ≥ target%` |
| **Budget limit** | `Σ(salary_i × x_i) × horizon_months ≤ total_budget` |
| **Non-negativity** | `x_i ≥ 0` for all roles |
| **Market capacity** | `x_i ≤ max_hire_i` (Saudi labour market availability cap) |

### Solver
`scipy.optimize.linprog` with HiGHS backend (industry-grade LP solver, same engine used in commercial OR tools).

---

## 📊 Dashboard Sections

| Section | Content |
|---|---|
| **KPI Row** | Current saudization, gap, budget, roles, optimal hire count, monthly cost |
| **Hire Count Bar** | Role-by-role optimal Saudi hire allocation |
| **Cost Pie** | Monthly payroll distribution across hired roles |
| **Gauge Chart** | Before → After saudization % with target line |
| **Waterfall Chart** | Current → New Hires → Target: gap decomposition |
| **Hiring Trajectory** | Month-by-month saudization % if hires distributed evenly |
| **Role Cards** | Each recommended role with hire count, salary, availability, priority |
| **4-Scenario Analysis** | Baseline / Budget+30% / Shorter Horizon / Target-5pp comparison |
| **Scenario Charts** | Saudization outcome and cost across scenarios |
| **Full Plan Table** | Downloadable CSV of complete hiring plan |
| **Strategy Insight Box** | Auto-generated policy recommendation paragraph |

---

## ⚙️ Role Profile Database

24 roles modelled across all 10 sectors with:
- Salary band (min/max in SAR)
- **Saudibility score** (0–1): proxy for Saudi labour market availability in that role
- Sector mapping for filtering

Saudibility is calibrated from HRDF workforce surveys and GASTAT employment statistics.

---

## 🎛️ Interactive Controls

| Control | Effect |
|---|---|
| **Company selector** | Pre-load real company from dataset |
| **Manual input mode** | Custom sector / headcount / budget |
| **Hiring horizon** | 3–24 months |
| **Salary strategy** | Cost-minimise / Balanced / Quality-maximise |
| **Role selector** | Include/exclude specific job categories |
| **Decision threshold** | Adjustable in predictive app (App 3) |

---

## 🚀 Quick Start

```bash
git clone https://github.com/YOUR_USERNAME/saudi-workforce-prescriptive.git
cd saudi-workforce-prescriptive
cp ../saudi-workforce-descriptive/saudi_workforce_data.csv .
pip install -r requirements.txt
streamlit run app.py
```

### Google Colab
```python
!pip install streamlit pyngrok scipy -q
from pyngrok import ngrok
import subprocess, time
proc = subprocess.Popen(["streamlit", "run", "app.py", "--server.port", "8501"])
time.sleep(3)
print(ngrok.connect(8501).public_url)
```

---

## 📁 File Structure

```
saudi-workforce-prescriptive/
├── app.py                      # LP optimizer + Streamlit dashboard
├── saudi_workforce_data.csv    # Shared dataset (from App 1)
├── requirements.txt            # 5 dependencies
└── README.md
```

---

## 🔮 The Complete Analytics Series

| App | Type | Question | Method |
|---|---|---|---|
| App 1 ✅ | Descriptive  | *What* is the workforce? | Charts, KPIs, aggregations |
| App 2 ✅ | Diagnostic   | *Why* are companies failing? | Root cause scoring, heatmaps |
| App 3 ✅ | Predictive   | *Will* they breach compliance? | Random Forest, Gradient Boosting |
| **App 4 ✅** | **Prescriptive** | ***What should they do?*** | **Linear Programming optimizer** |

---

## 💡 Why This Is the Rarest Skill in the Room

In any room of 50 data analytics candidates in KSA:
- 45 can describe data
- 20 can diagnose patterns
- 10 can build a predictive model
- **2–3 have ever written a constrained optimisation problem**

Prescriptive analytics with LP is taught in Operations Research programmes, not data analytics bootcamps. Implementing it on a live policy problem — with a proper objective function, binding constraints, and scenario sensitivity — is what separates junior analysts from senior decision-support specialists.

---

## 📄 Relevant KSA Institutions

This tool directly addresses the analytical needs of:
- **HRSD** (Human Resources & Social Development Ministry) — Nitaqat enforcement
- **GASTAT** — Labour force statistical analysis
- **HRDF** (Human Resources Development Fund) — Saudization subsidy programs
- **Vision 2030 Programme Management Office** — Employment target tracking
- **Big Four & Strategy Consulting firms** in KSA — HR transformation mandates

---

*Synthetic data calibrated to published GASTAT and HRSD statistics. No real company or individual data used.*
