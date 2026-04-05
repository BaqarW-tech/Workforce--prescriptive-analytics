import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from scipy.optimize import linprog
import os

# --- PRE-FLIGHT CHECK ---
if not os.path.exists("saudi_workforce_data.csv"):
    st.error("Missing Data! Please run 'python generate_data.py' first or upload the CSV.")
    st.stop()

# --- OPTIMIZER LOGIC (Updated for MILP) ---
def run_lp_optimizer(sector, current_saudi, current_total, monthly_budget, 
                     target_pct, hiring_horizon_months, roles_available):
    
    # 1. Early Exit if already compliant
    current_pct = (current_saudi / current_total) * 100
    if current_pct >= target_pct:
        return "COMPLIANT", None

    roles = []
    # Filter roles based on the job profile dictionary provided in the app
    for role in roles_available:
        p = JOB_ROLE_PROFILES[role]
        salary = (p["salary_min"] + p["salary_max"]) / 2
        roles.append({"role": role, "salary": salary, "saudibility": p["saudibility"]})

    n = len(roles)
    c = np.array([r["salary"] for r in roles]) # Minimise salary cost

    # Constraint: (S + sum(x)) / (T + sum(x)) >= ratio
    # x(1-ratio) >= ratio*T - S
    ratio = target_pct / 100
    needed_rhs = ratio * current_total - current_saudi
    A_ub = [-(1 - ratio) * np.ones(n)]
    b_ub = [-max(needed_rhs, 0.01)]

    # Budget Constraint: sum(x * salary) <= monthly_budget
    A_ub.append(c)
    b_ub.append(monthly_budget)

    # Bounds & Integrality (Force whole numbers for hiring)
    bounds = [(0, 50) for _ in range(n)] 
    integrality = np.ones(n) # 1 for integer, 0 for continuous

    res = linprog(c, A_ub=A_ub, b_ub=b_ub, bounds=bounds, integrality=integrality, method="highs")

    if not res.success:
        return "INFEASIBLE", "Increase budget or timeline."

    # Build Plan
    plan = []
    for i, count in enumerate(res.x):
        if count > 0:
            plan.append({
                "Role": roles[i]["role"],
                "Hire Count": int(count),
                "Monthly Cost": int(count * roles[i]["salary"])
            })
    
    return "SUCCESS", plan

# [Keep your existing JOB_ROLE_PROFILES and UI code from previous prompt]
# Ensure you use the run_lp_optimizer function above in the main loop.
