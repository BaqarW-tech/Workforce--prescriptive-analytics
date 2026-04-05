import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy.optimize import linprog
import warnings
warnings.filterwarnings("ignore")

# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Nitaqat Hiring Optimizer | Prescriptive Analytics",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;700&family=DM+Mono:wght@400;500&display=swap');
html,body,[class*="css"]{font-family:'DM Sans',sans-serif;}
.main{background:#040a06;}
.block-container{padding:1.5rem 2rem;}
[data-testid="stSidebar"]{background:#050d07;border-right:1px solid #0d2a12;}
[data-testid="stSidebar"] *{color:#6fad7e !important;}

.pres-title{font-size:1.7rem;font-weight:700;color:#e8fded;letter-spacing:-0.03em;}
.pres-sub{font-size:0.72rem;color:#1a4020;letter-spacing:0.18em;text-transform:uppercase;}

.kpi-box{
    background:linear-gradient(135deg,#050d07,#081408);
    border:1px solid #0d2a12; border-radius:12px;
    padding:1.1rem 1.3rem; text-align:center;
}
.kpi-box .lbl{color:#1e4025;font-size:0.67rem;letter-spacing:0.14em;text-transform:uppercase;}
.kpi-box .val{font-family:'DM Mono',monospace;font-size:1.85rem;font-weight:500;color:#4ade80;}
.kpi-box .sub{font-size:0.72rem;color:#1a4020;margin-top:0.2rem;}

.sec{font-size:0.65rem;letter-spacing:0.2em;text-transform:uppercase;
     color:#166534;border-bottom:1px solid #0d2a12;
     padding-bottom:0.35rem;margin:1.5rem 0 0.9rem;}

.hire-row{
    background:#050d07;border:1px solid #0d2a12;border-radius:10px;
    padding:0.9rem 1.3rem;margin-bottom:0.5rem;
    border-left:4px solid #22c55e;
}
.hire-row.optional{border-left-color:#f59e0b;}
.hire-row.skip{border-left-color:#374151;opacity:0.55;}

.scenario-card{
    background:#050d07;border:1px solid #0d2a12;border-radius:10px;
    padding:1rem 1.2rem;text-align:center;
}
.scenario-card .sc-label{color:#166534;font-size:0.7rem;letter-spacing:0.1em;text-transform:uppercase;}
.scenario-card .sc-val{font-family:'DM Mono',monospace;font-size:1.4rem;color:#4ade80;font-weight:500;}
.scenario-card .sc-sub{font-size:0.72rem;color:#1a4020;}

.insight-box{
    background:#050d07;border:1px solid #0d2a12;border-radius:8px;
    padding:1rem 1.3rem;font-size:0.82rem;color:#4a7a58;line-height:1.75;
}
.insight-box b{color:#4ade80;}

#MainMenu,footer,header{visibility:hidden;}
</style>
""", unsafe_allow_html=True)

# ── Constants ─────────────────────────────────────────────────────────────────
NITAQAT_TARGETS = {
    "Construction":6,"Information Technology":35,"Healthcare":35,
    "Financial Services":70,"Retail":30,"Education":55,
    "Manufacturing":10,"Tourism & Hospitality":20,
    "Energy & Utilities":75,"Transport & Logistics":15,
}

# Job roles with sector mapping, typical salary bands, and Saudi hire-ability score
# (hire-ability: how willing/available Saudis are for this role, 0-1)
JOB_ROLE_PROFILES = {
    "Software Engineer":         {"sectors":["Information Technology"],        "salary_min":10000,"salary_max":22000,"saudibility":0.72},
    "Data Analyst":              {"sectors":["Information Technology","Financial Services","Energy & Utilities"], "salary_min":8000,"salary_max":18000,"saudibility":0.78},
    "IT Manager":                {"sectors":["Information Technology"],        "salary_min":15000,"salary_max":28000,"saudibility":0.65},
    "Financial Analyst":         {"sectors":["Financial Services"],            "salary_min":10000,"salary_max":20000,"saudibility":0.82},
    "Accountant":                {"sectors":["Financial Services","Retail"],   "salary_min":6000,"salary_max":14000,"saudibility":0.80},
    "Branch Manager":            {"sectors":["Financial Services","Retail"],   "salary_min":12000,"salary_max":22000,"saudibility":0.75},
    "Nurse":                     {"sectors":["Healthcare"],                    "salary_min":7000,"salary_max":14000,"saudibility":0.60},
    "Pharmacist":                {"sectors":["Healthcare"],                    "salary_min":9000,"salary_max":16000,"saudibility":0.68},
    "Medical Admin":             {"sectors":["Healthcare"],                    "salary_min":5000,"salary_max":10000,"saudibility":0.85},
    "Teacher":                   {"sectors":["Education"],                     "salary_min":7000,"salary_max":15000,"saudibility":0.75},
    "Academic Advisor":          {"sectors":["Education"],                     "salary_min":8000,"salary_max":16000,"saudibility":0.80},
    "Sales Associate":           {"sectors":["Retail"],                        "salary_min":3500,"salary_max":8000,"saudibility":0.55},
    "Store Manager":             {"sectors":["Retail"],                        "salary_min":8000,"salary_max":16000,"saudibility":0.70},
    "Petroleum Engineer":        {"sectors":["Energy & Utilities"],            "salary_min":15000,"salary_max":32000,"saudibility":0.88},
    "HSE Manager":               {"sectors":["Energy & Utilities"],            "salary_min":14000,"salary_max":26000,"saudibility":0.82},
    "Operations Analyst":        {"sectors":["Energy & Utilities","Manufacturing"],"salary_min":8000,"salary_max":16000,"saudibility":0.76},
    "Logistics Coordinator":     {"sectors":["Transport & Logistics"],         "salary_min":5000,"salary_max":12000,"saudibility":0.65},
    "Fleet Manager":             {"sectors":["Transport & Logistics"],         "salary_min":9000,"salary_max":18000,"saudibility":0.72},
    "Production Supervisor":     {"sectors":["Manufacturing"],                 "salary_min":6000,"salary_max":14000,"saudibility":0.55},
    "Quality Inspector":         {"sectors":["Manufacturing"],                 "salary_min":5000,"salary_max":11000,"saudibility":0.58},
    "Hotel Manager":             {"sectors":["Tourism & Hospitality"],         "salary_min":10000,"salary_max":20000,"saudibility":0.62},
    "Tour Guide":                {"sectors":["Tourism & Hospitality"],         "salary_min":4000,"salary_max":9000,"saudibility":0.70},
    "Site Engineer":             {"sectors":["Construction"],                  "salary_min":7000,"salary_max":16000,"saudibility":0.55},
    "Project Manager":           {"sectors":["Construction"],                  "salary_min":12000,"salary_max":24000,"saudibility":0.65},
}

# ── LP Optimizer ──────────────────────────────────────────────────────────────
def run_lp_optimizer(sector, current_saudi, current_total, monthly_budget,
                     target_pct, hiring_horizon_months, roles_available,
                     salary_preference="balanced"):
    """
    Linear program:
    Minimise: sum(cost_i * x_i)   [total monthly salary cost of new hires]
    Subject to:
      (current_saudi + sum(x_i)) / (current_total + sum(x_i)) >= target_pct/100
      sum(x_i * avg_salary_i) <= monthly_budget
      x_i >= 0  (integer relaxation)
      x_i <= max_hire_i  (market availability constraint)
    """
    if not roles_available:
        return None, "No roles selected."

    roles = []
    for role in roles_available:
        if role not in JOB_ROLE_PROFILES:
            continue
        p = JOB_ROLE_PROFILES[role]
        # Salary midpoint adjusted by preference
        if salary_preference == "cost_minimize":
            salary = p["salary_min"] * 1.05
        elif salary_preference == "quality_maximize":
            salary = p["salary_max"] * 0.95
        else:
            salary = (p["salary_min"] + p["salary_max"]) / 2
        roles.append({
            "role":        role,
            "salary":      salary,
            "saudibility": p["saudibility"],
            "max_hire":    max(1, int(current_total * 0.08 * p["saudibility"])),  # market cap
        })

    if not roles:
        return None, "No valid roles."

    n = len(roles)
    # Objective: minimise total monthly salary cost
    c = np.array([r["salary"] for r in roles])

    # Constraint 1: Saudization constraint
    # (current_saudi + sum(x_i)) / (current_total + sum(x_i)) >= target_pct/100
    # Rearranged: sum(x_i * (1 - target_pct/100)) >= target_pct/100 * current_total - current_saudi
    ratio = target_pct / 100
    needed = ratio * current_total - current_saudi
    # As inequality for linprog (Ax <= b): -sum(x_i*(1-ratio)) <= -(needed)
    A_ub = [-(1 - ratio) * np.ones(n)]
    b_ub = [-max(needed, 0.001)]

    # Constraint 2: Budget constraint
    # sum(x_i * salary_i) * horizon <= total_budget
    total_budget = monthly_budget * hiring_horizon_months
    A_ub.append(c)
    b_ub.append(total_budget)

    # Bounds: 0 <= x_i <= max_hire_i
    bounds = [(0, r["max_hire"]) for r in roles]

    result = linprog(c, A_ub=A_ub, b_ub=b_ub, bounds=bounds, method="highs")

    if result.status != 0:
        return None, f"LP infeasible (status {result.status}). Try increasing budget or horizon."

    # Round to integers
    hire_counts = np.round(result.x).astype(int)
    hire_counts = np.maximum(hire_counts, 0)

    plan = []
    total_cost = 0
    total_new_saudi = 0
    for i, r in enumerate(roles):
        n_hire = hire_counts[i]
        if n_hire > 0:
            cost = n_hire * r["salary"]
            total_cost += cost
            total_new_saudi += n_hire
            plan.append({
                "Role":           r["role"],
                "Hire Count":     n_hire,
                "Avg Salary SAR": int(r["salary"]),
                "Monthly Cost":   int(cost),
                "Saudibility":    round(r["saudibility"], 2),
                "Priority":       "Essential" if r["saudibility"] >= 0.70 else "Optional",
            })

    new_total   = current_total + total_new_saudi
    new_saudi   = current_saudi + total_new_saudi
    new_saud_pct = new_saudi / new_total * 100 if new_total > 0 else 0

    summary = {
        "plan":           plan,
        "total_new_hires":total_new_saudi,
        "total_monthly_cost": int(total_cost),
        "total_budget_used":  int(total_cost * hiring_horizon_months),
        "new_saudization_pct":round(new_saud_pct, 2),
        "target_achieved":    new_saud_pct >= target_pct,
        "gap_closed":         round(new_saud_pct - (current_saudi/current_total*100 if current_total>0 else 0), 2),
        "cost_per_saudi_pp":  int(total_cost / max(new_saud_pct - current_saudi/current_total*100, 0.01)),
    }
    return summary, None


# ── Load base data for company selector ───────────────────────────────────────
@st.cache_data
def load_companies():
    df = pd.read_csv("saudi_workforce_data.csv")
    df["nitaqat_target"] = df["sector"].map(NITAQAT_TARGETS)
    co = df.groupby("company_id").apply(lambda g: pd.Series({
        "company_name":     g["company_name"].iloc[0],
        "sector":           g["sector"].iloc[0],
        "region":           g["region"].iloc[0],
        "nitaqat_status":   g["nitaqat_status"].iloc[0],
        "nitaqat_target":   g["nitaqat_target"].iloc[0],
        "headcount":        len(g),
        "saudi_count":      (g["nationality"]=="Saudi").sum(),
        "saudization_pct":  round((g["nationality"]=="Saudi").mean()*100, 1),
        "avg_salary":       int(g["monthly_salary_sar"].mean()),
        "total_payroll":    int(g["monthly_salary_sar"].sum()),
    })).reset_index()
    return co

companies = load_companies()

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Prescriptive Module")
    st.markdown("**LP Hiring Optimizer · App 4 of 4**")
    st.markdown("---")

    mode = st.radio("Input Mode", ["Use Real Company (from dataset)", "Manual Input"])
    st.markdown("---")

    if mode == "Use Real Company (from dataset)":
        # Filter to non-compliant companies
        non_compliant = companies[companies["nitaqat_status"].isin(["Red","Yellow","Low Green","Medium Green"])]
        company_options = non_compliant.apply(
            lambda r: f"{r['company_name']} ({r['sector']}, {r['saudization_pct']:.0f}% → {r['nitaqat_target']:.0f}%)", axis=1
        ).tolist()
        sel_idx = st.selectbox("Select Company", range(len(company_options)),
                               format_func=lambda i: company_options[i])
        sel_co = non_compliant.iloc[sel_idx]
        sector          = sel_co["sector"]
        current_total   = int(sel_co["headcount"])
        current_saudi   = int(sel_co["saudi_count"])
        target_pct      = float(sel_co["nitaqat_target"])
        monthly_budget  = int(sel_co["total_payroll"] * 0.15)  # 15% payroll budget for new hires
        company_label   = sel_co["company_name"]
    else:
        sector         = st.selectbox("Sector", list(NITAQAT_TARGETS.keys()))
        current_total  = st.number_input("Current Total Headcount", 20, 5000, 100)
        current_saudi  = st.number_input("Current Saudi Employees", 0, current_total, 10)
        target_pct     = float(NITAQAT_TARGETS[sector])
        monthly_budget = st.number_input("Monthly Hiring Budget (SAR)", 10000, 5000000, 200000, step=10000)
        company_label  = f"Custom {sector} Company"

    st.markdown("---")
    hiring_horizon = st.slider("Hiring Horizon (months)", 3, 24, 12)
    salary_pref    = st.selectbox("Salary Strategy",
                                  ["balanced","cost_minimize","quality_maximize"],
                                  format_func=lambda x: {"balanced":"Balanced Mid-Range",
                                                          "cost_minimize":"Cost Minimise",
                                                          "quality_maximize":"Quality Maximise"}[x])

    # Role selection based on sector
    available_roles = [r for r, p in JOB_ROLE_PROFILES.items() if sector in p["sectors"]]
    all_roles_default = list(JOB_ROLE_PROFILES.keys())  # cross-sector hiring allowed
    selected_roles = st.multiselect("Eligible Job Roles",
                                    options=list(JOB_ROLE_PROFILES.keys()),
                                    default=available_roles)
    st.markdown("---")
    st.markdown("<div style='color:#0d2a12;font-size:0.72rem;'>Prescriptive Analytics · Vision 2030 Series</div>",
                unsafe_allow_html=True)

# ── Run LP ────────────────────────────────────────────────────────────────────
current_saud_pct = current_saudi / current_total * 100 if current_total > 0 else 0
summary, error = run_lp_optimizer(
    sector, current_saudi, current_total,
    monthly_budget, target_pct, hiring_horizon,
    selected_roles, salary_pref
)

# Run 4 scenarios for comparison
scenarios = {}
scenario_configs = {
    "Baseline":          (monthly_budget,       target_pct,       hiring_horizon),
    "Budget +30%":       (monthly_budget*1.30,  target_pct,       hiring_horizon),
    "Shorter Horizon":   (monthly_budget,        target_pct,       max(3,hiring_horizon-6)),
    "Target -5pp":       (monthly_budget,        max(1,target_pct-5), hiring_horizon),
}
for sc_name, (bud, tgt, hor) in scenario_configs.items():
    sc_sum, _ = run_lp_optimizer(sector, current_saudi, current_total,
                                  bud, tgt, hor, selected_roles, salary_pref)
    scenarios[sc_name] = sc_sum

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown('<div class="pres-title">Nitaqat Compliance Hiring Optimizer</div>', unsafe_allow_html=True)
st.markdown('<div class="pres-sub">PRESCRIPTIVE ANALYTICS · LINEAR PROGRAMMING · OPTIMAL HIRING PLAN</div>', unsafe_allow_html=True)
st.markdown("---")

# ── KPI Row ───────────────────────────────────────────────────────────────────
k1,k2,k3,k4,k5,k6 = st.columns(6)
kpis = [
    (k1, "Current Saudization", f"{current_saud_pct:.1f}%",   f"Target: {target_pct:.0f}%"),
    (k2, "Gap to Close",        f"{max(0, target_pct-current_saud_pct):.1f}pp", "Compliance shortfall"),
    (k3, "Monthly Budget",      f"SAR {monthly_budget:,}",     f"{hiring_horizon}m horizon"),
    (k4, "Roles Available",     str(len(selected_roles)),      f"{sector}"),
]
if summary:
    kpis += [
        (k5, "Optimal New Hires", str(summary["total_new_hires"]), f"→ {summary['new_saudization_pct']:.1f}% saudization"),
        (k6, "Monthly Cost",      f"SAR {summary['total_monthly_cost']:,}", "✅ Target Achieved" if summary["target_achieved"] else "⚠️ Partial"),
    ]
else:
    kpis += [(k5,"Status","⚠️ No Plan","Adjust inputs"),(k6,"Error","-","—")]

for col,label,val,sub in kpis:
    val_color = "#4ade80" if "%" in val or "SAR" in val or val.isdigit() else "#f59e0b" if "⚠" in val else "#4ade80"
    with col:
        st.markdown(f'<div class="kpi-box"><div class="lbl">{label}</div><div class="val" style="color:{val_color}">{val}</div><div class="sub">{sub}</div></div>', unsafe_allow_html=True)

st.markdown("")

if error:
    st.error(f"Optimizer: {error}. Try increasing budget, extending horizon, or adding more roles.")
    st.stop()

# ── Section 1: Optimal Hire Plan ──────────────────────────────────────────────
st.markdown('<div class="sec">Optimal Hiring Plan — Role Allocation</div>', unsafe_allow_html=True)
plan_df = pd.DataFrame(summary["plan"]) if summary["plan"] else pd.DataFrame()

p1, p2 = st.columns([1.3, 1])

with p1:
    if not plan_df.empty:
        fig_plan = px.bar(
            plan_df.sort_values("Hire Count", ascending=True),
            x="Hire Count", y="Role", orientation="h",
            color="Priority",
            color_discrete_map={"Essential":"#4ade80","Optional":"#f59e0b"},
            text="Hire Count",
            title=f"Recommended Saudi Hires by Role — {company_label}",
        )
        fig_plan.update_layout(
            height=380, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font_color="#4a7a58", title_font_color="#e8fded",
            margin=dict(l=10,r=10,t=40,b=10),
            legend=dict(font_color="#4a7a58",bgcolor="rgba(0,0,0,0)"),
            xaxis=dict(showgrid=False,color="#1a4020"),
            yaxis=dict(showgrid=False,color="#6fad7e"),
        )
        fig_plan.update_traces(textposition="outside",textfont_color="#4ade80")
        st.plotly_chart(fig_plan, use_container_width=True)
    else:
        st.info("No hires needed — already compliant.")

with p2:
    # Cost breakdown pie
    if not plan_df.empty:
        fig_cost = px.pie(
            plan_df, names="Role", values="Monthly Cost",
            hole=0.55,
            color_discrete_sequence=px.colors.sequential.Greens[2:],
            title="Monthly Payroll Cost Distribution by Role",
        )
        fig_cost.update_layout(
            height=380, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font_color="#4a7a58", title_font_color="#e8fded",
            margin=dict(l=10,r=10,t=40,b=10),
            showlegend=True,
            legend=dict(font_color="#4a7a58",bgcolor="rgba(0,0,0,0)",font_size=10),
            annotations=[dict(text="Cost Mix",x=0.5,y=0.5,font_size=12,font_color="#4a7a58",showarrow=False)],
        )
        st.plotly_chart(fig_cost, use_container_width=True)

# ── Section 2: Before/After Visualisation ─────────────────────────────────────
st.markdown('<div class="sec">Before vs After — Compliance Trajectory</div>', unsafe_allow_html=True)
ba1, ba2, ba3 = st.columns(3)

with ba1:
    # Gauge chart: before and after saudization
    fig_gauge = go.Figure()
    fig_gauge.add_trace(go.Indicator(
        mode="gauge+number+delta",
        value=summary["new_saudization_pct"],
        delta={"reference": current_saud_pct, "valueformat":".1f",
               "increasing":{"color":"#4ade80"},"decreasing":{"color":"#ef4444"}},
        title={"text":"Saudization % After Hiring","font":{"color":"#e8fded","size":13}},
        number={"suffix":"%","font":{"color":"#4ade80","family":"DM Mono","size":36}},
        gauge={
            "axis":{"range":[0,100],"tickcolor":"#1a4020","tickfont":{"color":"#4a7a58"}},
            "bar":{"color":"#4ade80"},
            "bgcolor":"#050d07",
            "bordercolor":"#0d2a12",
            "steps":[
                {"range":[0, target_pct*0.6],"color":"#1a0a0a"},
                {"range":[target_pct*0.6, target_pct],"color":"#1a2a0a"},
                {"range":[target_pct, 100],"color":"#0a1a0a"},
            ],
            "threshold":{"line":{"color":"#f59e0b","width":3},"value":target_pct},
        }
    ))
    fig_gauge.update_layout(
        height=280, paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=20,r=20,t=50,b=10),
        font_color="#4a7a58",
    )
    st.plotly_chart(fig_gauge, use_container_width=True)

with ba2:
    # Waterfall: current → new hires → target
    gap_remaining = max(0, target_pct - summary["new_saudization_pct"])
    fig_wf = go.Figure(go.Waterfall(
        orientation="v",
        measure=["absolute","relative","relative","absolute"],
        x=["Current\nSaudization","New Saudi\nHires","Remaining\nGap","Post-Plan\nSaudization"],
        y=[current_saud_pct, summary["gap_closed"], -gap_remaining, None],
        text=[f"{current_saud_pct:.1f}%",f"+{summary['gap_closed']:.1f}pp",
              f"-{gap_remaining:.1f}pp" if gap_remaining>0 else "✅ Closed",""],
        connector={"line":{"color":"#0d2a12"}},
        decreasing={"marker":{"color":"#ef4444"}},
        increasing={"marker":{"color":"#4ade80"}},
        totals={"marker":{"color":"#22c55e"}},
        textfont={"color":"#e8fded"},
    ))
    fig_wf.add_hline(y=target_pct, line_color="#f59e0b", line_dash="dash",
                     annotation_text=f"Target {target_pct:.0f}%",
                     annotation_font_color="#f59e0b")
    fig_wf.update_layout(
        title="Saudization Waterfall",
        height=280, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font_color="#4a7a58", title_font_color="#e8fded",
        margin=dict(l=10,r=10,t=40,b=10),
        xaxis=dict(showgrid=False,color="#1a4020"),
        yaxis=dict(showgrid=True,gridcolor="#050d07",color="#1a4020"),
        showlegend=False,
    )
    st.plotly_chart(fig_wf, use_container_width=True)

with ba3:
    # Hiring timeline projection
    months = list(range(1, hiring_horizon+1))
    hires_per_month = summary["total_new_hires"] / hiring_horizon
    cumulative_saudi = [current_saudi + hires_per_month * m for m in months]
    cumulative_total = [current_total + hires_per_month * m for m in months]
    saud_traj = [s/t*100 for s,t in zip(cumulative_saudi, cumulative_total)]

    fig_traj = go.Figure()
    fig_traj.add_trace(go.Scatter(
        x=months, y=saud_traj, mode="lines+markers",
        name="Projected Saudization %",
        line=dict(color="#4ade80",width=2.5),
        marker=dict(size=6,color="#4ade80"),
        fill="tozeroy", fillcolor="rgba(74,222,128,0.07)",
    ))
    fig_traj.add_hline(y=target_pct, line_color="#f59e0b", line_dash="dash",
                       annotation_text=f"Target {target_pct:.0f}%",
                       annotation_font_color="#f59e0b")
    fig_traj.add_hline(y=current_saud_pct, line_color="#374151", line_dash="dot",
                       annotation_text=f"Current {current_saud_pct:.1f}%",
                       annotation_font_color="#374151")
    fig_traj.update_layout(
        title=f"Hiring Trajectory ({hiring_horizon}m)",
        height=280, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font_color="#4a7a58", title_font_color="#e8fded",
        margin=dict(l=10,r=10,t=40,b=10),
        xaxis=dict(title="Month",showgrid=False,color="#1a4020"),
        yaxis=dict(title="Saudization %",showgrid=True,gridcolor="#050d07",color="#1a4020"),
        showlegend=False,
    )
    st.plotly_chart(fig_traj, use_container_width=True)

# ── Section 3: Role-by-Role Cards ─────────────────────────────────────────────
st.markdown('<div class="sec">Role-Level Hiring Recommendations</div>', unsafe_allow_html=True)

if plan_df.empty:
    st.success("✅ Company already meets Nitaqat target. No additional Saudi hires required.")
else:
    cols = st.columns(min(3, len(plan_df)))
    for i, (_, row) in enumerate(plan_df.sort_values("Hire Count", ascending=False).iterrows()):
        with cols[i % len(cols)]:
            bar_w   = int(row["Saudibility"] * 100)
            priority_color = "#4ade80" if row["Priority"]=="Essential" else "#f59e0b"
            st.markdown(f"""
            <div class="hire-row {'optional' if row['Priority']=='Optional' else ''}">
              <div style="color:#e8fded;font-weight:600;font-size:0.9rem;">{row['Role']}</div>
              <div style="margin:0.4rem 0;background:#0a1a0c;border-radius:4px;height:5px;">
                <div style="background:{priority_color};width:{bar_w}%;height:100%;border-radius:4px;"></div>
              </div>
              <div style="color:#1a4020;font-size:0.75rem;">
                Hire: <b style="color:#4ade80">{row['Hire Count']}</b> Saudi nationals<br>
                Salary: <b style="color:#6fad7e">SAR {row['Avg Salary SAR']:,}/mo</b><br>
                Monthly cost: SAR {row['Monthly Cost']:,}<br>
                Saudi availability: {int(row['Saudibility']*100)}%
                &nbsp;·&nbsp; <span style="color:{priority_color}">{row['Priority']}</span>
              </div>
            </div>""", unsafe_allow_html=True)

# ── Section 4: Scenario Analysis ──────────────────────────────────────────────
st.markdown('<div class="sec">Scenario Analysis — Budget & Target Sensitivity</div>', unsafe_allow_html=True)

sc_cols = st.columns(4)
for i, (sc_name, sc_sum) in enumerate(scenarios.items()):
    with sc_cols[i]:
        if sc_sum:
            achieved = "✅" if sc_sum["target_achieved"] else "⚠️"
            st.markdown(f"""
            <div class="scenario-card">
              <div class="sc-label">{sc_name}</div>
              <div class="sc-val">{sc_sum['new_saudization_pct']:.1f}%</div>
              <div class="sc-sub">{achieved} {sc_sum['total_new_hires']} hires · SAR {sc_sum['total_monthly_cost']:,}/mo</div>
              <div style="margin-top:0.4rem;font-size:0.7rem;color:#1a4020;">
                Budget used: SAR {sc_sum['total_budget_used']:,}<br>
                Cost per pp: SAR {sc_sum['cost_per_saudi_pp']:,}
              </div>
            </div>""", unsafe_allow_html=True)
        else:
            st.markdown('<div class="scenario-card"><div class="sc-label">Infeasible</div><div class="sc-val">—</div></div>', unsafe_allow_html=True)

st.markdown("")

# Scenario comparison chart
sc_chart_data = []
for sc_name, sc_sum in scenarios.items():
    if sc_sum:
        sc_chart_data.append({
            "Scenario":      sc_name,
            "Saudization %": sc_sum["new_saudization_pct"],
            "New Hires":     sc_sum["total_new_hires"],
            "Monthly Cost":  sc_sum["total_monthly_cost"],
            "Target Met":    "Yes" if sc_sum["target_achieved"] else "No",
        })

if sc_chart_data:
    sc_df = pd.DataFrame(sc_chart_data)
    sc1, sc2 = st.columns(2)

    with sc1:
        fig_sc_saud = px.bar(
            sc_df, x="Scenario", y="Saudization %",
            color="Target Met",
            color_discrete_map={"Yes":"#4ade80","No":"#f59e0b"},
            text=sc_df["Saudization %"].apply(lambda x: f"{x:.1f}%"),
            title="Post-Plan Saudization % by Scenario",
        )
        fig_sc_saud.add_hline(y=target_pct, line_color="#ef4444", line_dash="dash",
                              annotation_text=f"Target {target_pct:.0f}%",
                              annotation_font_color="#ef4444")
        fig_sc_saud.update_layout(
            height=300, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font_color="#4a7a58", title_font_color="#e8fded",
            margin=dict(l=10,r=10,t=40,b=10),
            legend=dict(font_color="#4a7a58",bgcolor="rgba(0,0,0,0)"),
            xaxis=dict(showgrid=False,color="#1a4020"),
            yaxis=dict(showgrid=False,color="#1a4020"),
        )
        fig_sc_saud.update_traces(textposition="outside",textfont_color="#4ade80")
        st.plotly_chart(fig_sc_saud, use_container_width=True)

    with sc2:
        fig_sc_cost = px.bar(
            sc_df, x="Scenario", y="Monthly Cost",
            color="New Hires",
            color_continuous_scale=["#0a1a0c","#4ade80"],
            text=sc_df["Monthly Cost"].apply(lambda x: f"SAR {x:,}"),
            title="Monthly Cost by Scenario",
        )
        fig_sc_cost.update_layout(
            height=300, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font_color="#4a7a58", title_font_color="#e8fded",
            margin=dict(l=10,r=10,t=40,b=10),
            coloraxis_showscale=False,
            xaxis=dict(showgrid=False,color="#1a4020"),
            yaxis=dict(showgrid=False,color="#1a4020"),
        )
        fig_sc_cost.update_traces(textposition="outside",textfont_color="#4ade80")
        st.plotly_chart(fig_sc_cost, use_container_width=True)

# ── Section 5: Full Hire Plan Table ───────────────────────────────────────────
st.markdown('<div class="sec">Full Hiring Plan — Exportable Table</div>', unsafe_allow_html=True)

if not plan_df.empty:
    display_df = plan_df.copy()
    display_df["Total 12m Cost (SAR)"] = display_df["Monthly Cost"] * hiring_horizon
    display_df["Cost/Hire (SAR)"] = display_df["Avg Salary SAR"]
    st.dataframe(
        display_df[["Role","Hire Count","Avg Salary SAR","Monthly Cost",
                    "Total 12m Cost (SAR)","Saudibility","Priority"]],
        use_container_width=True, hide_index=True,
    )

    # Download as CSV
    csv_bytes = display_df.to_csv(index=False).encode()
    st.download_button(
        "📥 Download Hiring Plan CSV",
        data=csv_bytes,
        file_name=f"hiring_plan_{company_label.replace(' ','_')}.csv",
        mime="text/csv",
    )

# ── Insight Box ────────────────────────────────────────────────────────────────
st.markdown('<div class="sec">Optimization Summary & Strategic Recommendations</div>', unsafe_allow_html=True)

dominant_role = plan_df.iloc[0]["Role"] if not plan_df.empty else "N/A"
efficiency    = summary["cost_per_saudi_pp"] if summary else 0
gap_closed    = summary["gap_closed"] if summary else 0
achieved_str  = "fully achieves" if summary and summary["target_achieved"] else "partially closes"

st.markdown(f"""
<div class="insight-box">
⚙️ <b>Optimization Result:</b> The linear program {achieved_str} the {target_pct:.0f}% Nitaqat target
for <b>{company_label}</b> by recommending <b>{summary['total_new_hires'] if summary else 0} new Saudi hires</b>
at a monthly payroll cost of <b>SAR {summary['total_monthly_cost']:,}</b>.
The dominant role is <b>{dominant_role}</b>, selected for its combination of high Saudi labour market
availability and cost efficiency within the {salary_pref.replace('_',' ')} salary strategy.<br><br>

💰 <b>Cost Efficiency:</b> The plan achieves a Saudization gain of <b>{gap_closed:+.1f}pp</b>
at a cost of approximately <b>SAR {efficiency:,} per percentage point</b> of Saudization improvement.
Scenario analysis shows that increasing the budget by 30% {'achieves' if scenarios.get('Budget +30%') and scenarios['Budget +30%']['target_achieved'] else 'does not achieve'} the full target,
while relaxing the target by 5pp {'reduces' if scenarios.get('Target -5pp') and scenarios['Target -5pp']['total_new_hires'] < (summary['total_new_hires'] if summary else 0) else 'does not significantly reduce'} required hiring.<br><br>

🏛️ <b>Operational Recommendation:</b> Front-load hiring in Q1 and Q3 to align with HRSD
audit cycles. Prioritise <b>Essential</b> roles (saudibility ≥ 70%) first — these have
the deepest Saudi talent pools and lowest recruitment risk. For Optional roles,
consider Saudi graduate programmes and HRDF subsidies to reduce net salary cost by 20–30%.<br><br>

📋 <b>Regulatory Note:</b> Post-hiring Saudization of <b>{summary['new_saudization_pct'] if summary else 0:.1f}%</b>
against a target of <b>{target_pct:.0f}%</b> {'places the company in compliance' if summary and summary['target_achieved'] else 'requires additional measures such as HRDF co-funding or Nitaqat Plus programmes'}.
This plan should be reviewed quarterly against actual hiring progress and updated sector targets.
</div>""", unsafe_allow_html=True)

st.markdown("---")
st.markdown(
    "<div style='text-align:center;color:#0a1a0c;font-size:0.72rem;padding:0.5rem;'>"
    "Nitaqat Hiring Optimizer · Prescriptive Analytics · Vision 2030 Portfolio Series · App 4 of 4 ✅ Complete"
    "</div>",
    unsafe_allow_html=True,
)
