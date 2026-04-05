🇸🇦 Saudi Workforce: Nitaqat Hiring Optimizer
Prescriptive Analytics · App 4 of 4 · Vision 2030 Portfolio Series

![alt text](https://workforce--prescriptive-analytics-hb77e2xlhckfng5dn8us8t.streamlit.app/)


![alt text](https://img.shields.io/badge/Python-3.10+-blue)


![alt text](https://img.shields.io/badge/scipy-LP%20Optimizer-green)


![alt text](https://img.shields.io/badge/License-MIT-yellow)

"What should we do, and at what cost?"
This app uses Mixed-Integer Linear Programming (MILP) to calculate the mathematically optimal hiring plan for Saudi companies to reach Nitaqat compliance targets while minimizing total payroll increases.

🎯 The Problem

While Descriptive analytics shows us the current state and Predictive analytics shows us future risks, Prescriptive Analytics provides the solution.

A company failing Nitaqat compliance needs to hire Saudis, but:

Which roles? (IT, Admin, Management, Operations?)

How many? (What is the minimum to hit the % target?)

What budget? (How do we stay within financial limits?)

This tool replaces "guessing" with a provably optimal allocation using the HiGHS industry-grade solver.

🧮 The Optimization Model

The app solves the following mathematical problem:

Objective: Minimize 
∑
(
Salary
𝑖
×
𝑥
𝑖
)
∑(Salary
i
	​

×x
i
	​

)
 — Minimize the new monthly payroll.

Decision Variables (
𝑥
𝑖
x
i
	​

): The number of Saudi nationals to hire for each job role.

Constraint 1 (Compliance): 
Current Saudi
+
∑
𝑥
𝑖
Total Headcount
+
∑
𝑥
𝑖
≥
Target %
Total Headcount+∑x
i
	​

Current Saudi+∑x
i
	​

	​

≥Target %

Constraint 2 (Budget): 
∑
(
Salary
𝑖
×
𝑥
𝑖
)
≤
Monthly Budget
∑(Salary
i
	​

×x
i
	​

)≤Monthly Budget

Constraint 3 (Market): 
𝑥
𝑖
≤
Market Availability Cap
x
i
	​

≤Market Availability Cap

🚀 Quick Start (Local Setup)
1. Clone the Repository
code
Bash
download
content_copy
expand_less
git clone https://github.com/BaqarW-tech/Workforce--prescriptive-analytics.git
cd Workforce--prescriptive-analytics
2. Install Dependencies
code
Bash
download
content_copy
expand_less
pip install -r requirements.txt
3. Generate the Dataset

Since the workforce data is synthetic and calibrated to GASTAT statistics, run the generator once to create the required CSV:

code
Bash
download
content_copy
expand_less
python generate_data.py
4. Run the App
code
Bash
download
content_copy
expand_less
streamlit run app.py
📊 Dashboard Features
Feature	Description
Scenario Sensitivity	Compare the "Baseline" plan against "Budget +30%" or "Target -5pp" scenarios.
Saudization Waterfall	Visualizes the gap between current state and the optimized target.
Role-Level Cards	Detailed hiring recommendations including "Saudibility" scores (market availability).
Exportable Plan	Download the mathematically optimal hiring roadmap as a CSV for HR implementation.
Interactive Controls	Adjust hiring horizons (3–24 months) and salary strategies (Cost vs. Quality).
📁 Repository Structure
code
Code
download
content_copy
expand_less
.
├── app.py                  # Main Streamlit application & Optimizer logic
├── generate_data.py        # Script to create synthetic Saudi workforce data
├── requirements.txt        # Python dependencies (Scipy 1.11+ required)
├── saudi_workforce_data.csv# Generated dataset (created after running script)
└── README.md               # This file
🧠 Why This Portfolio Stands Out

In the data science field, Optimization (Operations Research) is a rare skill compared to standard Machine Learning. This project demonstrates:

Domain Expertise: Understanding of the KSA Nitaqat regulatory framework and Vision 2030 goals.

Technical Seniority: Moving beyond simple "charts" into "Decision Support Systems" using Scipy's MILP solvers.

Business Value: Directly addressing a multi-million riyal compliance problem faced by every private sector entity in Saudi Arabia.

🔗 The Complete Series

This app is part of the Saudi Workforce Analytics Suite:

Descriptive: What does our workforce look like?

Diagnostic: Why are we failing Nitaqat targets?

Predictive: When will we fall into the "Red" zone?

Prescriptive: (This App) The Optimal Hiring Roadmap.

📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

Disclaimer: All data used is synthetic and generated for demonstration purposes, calibrated to publicly available HRSD and GASTAT statistical ranges.
