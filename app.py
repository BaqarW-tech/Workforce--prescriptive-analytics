import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from scipy.optimize import linprog

# ── PAGE CONFIG ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Nitaqat Compliance Suite",
    page_icon="🇸🇦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── CONSTANTS ─────────────────────────────────────────────────────────────────
SECTORS = [
    "Construction", "Education", "Energy & Utilities", "Financial Services",
    "Healthcare", "Information Technology", "Manufacturing",
    "Retail", "Tourism & Hospitality", "Transport & Logistics"
]
REGIONS = ["Abha", "Dammam", "Jeddah", "Makkah", "Medina", "Riyadh", "Tabuk"]

# Nitaqat thresholds vary by sector (simplified MLHR bands)
NITAQAT_THRESHOLDS = {
    "Construction": 6,
    "Education": 35,
    "Energy & Utilities": 35,
    "Financial Services": 60,
    "Healthcare": 35,
    "Information Technology": 20,
    "Manufacturing": 10,
    "Retail": 30,
    "Tourism & Hospitality": 20,
    "Transport & Logistics": 10,
}

JOB_ROLE_PROFILES = {
    "Accountant":         {"salary_min": 8000,  "salary_max": 18000, "saudibility": 0.85},
    "HR Specialist":      {"salary_min": 7000,  "salary_max": 15000, "saudibility": 0.90},
    "IT Analyst":         {"salary_min": 10000, "salary_max": 22000, "saudibility": 0.70},
    "Sales Executive":    {"salary_min": 6000,  "salary_max": 14000, "saudibility": 0.80},
    "Operations Coord.":  {"salary_min": 7000,  "salary_max": 16000, "saudibility": 0.75},
    "Engineer":           {"salary_min": 12000, "salary_max": 28000, "saudibility": 0.65},
    "Customer Service":   {"salary_min": 5000,  "salary_max": 10000, "saudibility": 0.95},
    "Project Manager":    {"salary_min": 15000, "salary_max": 35000, "saudibility": 0.60},
    "Data Analyst":       {"salary_min": 10000, "salary_max": 24000, "saudibility": 0.70},
    "Admin Assistant":    {"salary_min": 5000,  "salary_max": 9000,  "saudibility": 0.95},
}

# ── SYNTHETIC DATA GENERATOR ──────────────────────────────────────────────────
@st.cache_data
def build_company_features():
    """
    Generates synthetic but realistic employee + company-level data.
    Mirrors the structure of the original saudi_workforce_data.csv
    so no external file is needed on Streamlit Cloud.
    """
    rng = np.random.default_rng(42)
    records = []
    company_id = 1001

    for i, sector in enumerate(SECTORS):
        n_companies = 4 if sector in ["Financial Services", "Education"] else 5
        for j in range(n_companies):
            region = REGIONS[(i * n_companies + j) % len(REGIONS)]
            n_emp = int(rng.integers(40, 200))
            base_salary = rng.integers(14000, 22000)
            threshold = NITAQAT_THRESHOLDS[sector]

            # Intentionally mix compliant and failing companies
            if (i + j) % 3 == 0:
                saudi_frac = rng.uniform(0.03, threshold / 100 - 0.02)  # Failing
            else:
                saudi_frac = rng.uniform(threshold / 100 + 0.01, 0.75)  # Compliant

            for k in range(n_emp):
                is_saudi = rng.random() < saudi_frac
                salary = int(rng.integers(
                    int(base_salary * 0.4),
                    int(base_salary * 1.6)
                ))
                salary = max(3500, min(35000, salary))
                records.append({
                    "employee_id": f"EMP-{rng.integers(100000,999999)}",
                    "company_id":  f"CO-{company_id}",
                    "company_name": f"Saudi {sector} Group {company_id - 1000}",
                    "sector":      sector,
                    "region":      region,
                    "nationality": "Saudi" if is_saudi else "Expatriate",
                    "monthly_salary_sar": salary,
                    "nitaqat_status": "",  # filled below
                })
            company_id += 1

    df = pd.DataFrame(records)

    # Company-level aggregation
    co = (
        df.groupby(["company_id", "company_name", "sector", "region"])
        .agg(
            total_employees=("employee_id", "count"),
            saudi_employees=("nationality", lambda x: (x == "Saudi").sum()),
            avg_salary_sar=("monthly_salary_sar", "mean"),
        )
        .reset_index()
    )
    co["saudi_pct"] = (co["saudi_employees"] / co["total_employees"] * 100).round(1)
    co["threshold_pct"] = co["sector"].map(NITAQAT_THRESHOLDS)
    co["nitaqat_status"] = np.where(
        co["saudi_pct"] >= co["threshold_pct"], "Compliant", "Failing"
    )
    co["gap_pct"] = (co["threshold_pct"] - co["saudi_pct"]).clip(lower=0).round(1)
    co["avg_salary_sar"] = co["avg_salary_sar"].round(0).astype(int)

    # Back-fill status into employee df
    status_map = co.set_index("company_id")["nitaqat_status"].to_dict()
    df["nitaqat_status"] = df["company_id"].map(status_map)

    return df, co


# ── LP OPTIMIZER ──────────────────────────────────────────────────────────────
def run_lp_optimizer(
    sector, current_saudi, current_total,
    monthly_budget, target_pct, roles_available
):
    current_pct = (current_saudi / current_total) * 100
    if current_pct >= target_pct:
        return "COMPLIANT", None

    roles = []
    for role in roles_available:
        p = JOB_ROLE_PROFILES[role]
        salary = (p["salary_min"] + p["salary_max"]) / 2
        roles.append({"role": role, "salary": salary, "saudibility": p["saudibility"]})

    n = len(roles)
    if n == 0:
        return "INFEASIBLE", "No roles selected."

    c = np.array([r["salary"] for r in roles])
    ratio = target_pct / 100
    needed_rhs = ratio * current_total - current_saudi

    A_ub = [-(1 - ratio) * np.ones(n)]        # Compliance constraint
    b_ub = [-max(needed_rhs, 0.01)]

    A_ub.append(c)                             # Budget constraint
    b_ub.append(monthly_budget)

    bounds = [(0, 100) for _ in range(n)]
    integrality = np.ones(n)

    res = linprog(
        c, A_ub=A_ub, b_ub=b_ub,
        bounds=bounds, integrality=integrality, method="highs"
    )

    if not res.success:
        return "INFEASIBLE", "Budget too low or target unreachable. Increase budget or relax target."

    plan = []
    for i, count in enumerate(res.x):
        if round(count) > 0:
            plan.append({
                "Role":          roles[i]["role"],
                "Hire Count":    int(round(count)),
                "Monthly Cost (SAR)": int(round(count) * roles[i]["salary"]),
            })

    if not plan:
        return "INFEASIBLE", "Optimizer returned zero hires — try a higher budget."

    return "SUCCESS", plan


# ── LOAD DATA ─────────────────────────────────────────────────────────────────
df, co = build_company_features()

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
st.sidebar.image(
    "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0d/Flag_of_Saudi_Arabia.svg/320px-Flag_of_Saudi_Arabia.svg.png",
    width=120,
)
st.sidebar.title("🏢 Nitaqat Suite")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigate",
    ["📊 Dashboard", "🔍 Company Explorer", "⚙️ Hiring Optimizer", "📈 Sector Analytics"],
)

st.sidebar.markdown("---")
st.sidebar.caption(
    f"**Dataset:** {len(df):,} employees · {co['company_id'].nunique()} companies · "
    f"{df['sector'].nunique()} sectors"
)

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 1 — DASHBOARD
# ═══════════════════════════════════════════════════════════════════════════════
if page == "📊 Dashboard":
    st.title("📊 Nitaqat Compliance Dashboard")
    st.markdown("Kingdom-wide Saudization snapshot across all sectors and regions.")

    # KPI row
    total_emp     = len(df)
    saudi_emp     = (df["nationality"] == "Saudi").sum()
    compliant_cos = (co["nitaqat_status"] == "Compliant").sum()
    failing_cos   = (co["nitaqat_status"] == "Failing").sum()
    overall_pct   = saudi_emp / total_emp * 100

    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("Total Employees",    f"{total_emp:,}")
    k2.metric("Saudi Nationals",    f"{saudi_emp:,}", f"{overall_pct:.1f}%")
    k3.metric("Companies",          f"{co.shape[0]}")
    k4.metric("✅ Compliant",        f"{compliant_cos}",  f"{compliant_cos/co.shape[0]*100:.0f}%")
    k5.metric("❌ Failing",          f"{failing_cos}",   f"-{failing_cos/co.shape[0]*100:.0f}%", delta_color="inverse")

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Compliance by Sector")
        sector_summary = (
            co.groupby("sector")
            .agg(
                Companies=("company_id", "count"),
                Compliant=("nitaqat_status", lambda x: (x == "Compliant").sum()),
                Avg_Saudi_Pct=("saudi_pct", "mean"),
            )
            .reset_index()
        )
        sector_summary["Compliance Rate %"] = (
            sector_summary["Compliant"] / sector_summary["Companies"] * 100
        ).round(1)
        fig = px.bar(
            sector_summary.sort_values("Compliance Rate %"),
            x="Compliance Rate %", y="sector",
            orientation="h",
            color="Compliance Rate %",
            color_continuous_scale="RdYlGn",
            range_color=[0, 100],
            labels={"sector": "Sector"},
            height=400,
        )
        fig.update_layout(margin=dict(l=0, r=10, t=10, b=0), coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Compliant vs Failing by Region")
        region_summary = (
            co.groupby(["region", "nitaqat_status"])
            .size()
            .reset_index(name="count")
        )
        fig2 = px.bar(
            region_summary,
            x="region", y="count", color="nitaqat_status",
            barmode="group",
            color_discrete_map={"Compliant": "#2ecc71", "Failing": "#e74c3c"},
            labels={"count": "Companies", "region": "Region", "nitaqat_status": "Status"},
            height=400,
        )
        fig2.update_layout(margin=dict(l=0, r=0, t=10, b=0), legend_title_text="")
        st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Saudi % vs Sector Threshold")
    fig3 = px.scatter(
        co,
        x="threshold_pct", y="saudi_pct",
        color="nitaqat_status",
        size="total_employees",
        hover_data=["company_name", "sector", "region"],
        color_discrete_map={"Compliant": "#2ecc71", "Failing": "#e74c3c"},
        labels={
            "threshold_pct": "Sector Threshold (%)",
            "saudi_pct": "Company Saudi % (Actual)",
        },
        height=420,
    )
    # Diagonal reference line
    fig3.add_shape(
        type="line", x0=0, y0=0, x1=80, y1=80,
        line=dict(color="gray", dash="dash", width=1)
    )
    fig3.update_layout(margin=dict(l=0, r=0, t=10, b=0), legend_title_text="")
    st.plotly_chart(fig3, use_container_width=True)
    st.caption("Points **above** the dashed line = compliant. Size = headcount.")


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 2 — COMPANY EXPLORER
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "🔍 Company Explorer":
    st.title("🔍 Company Explorer")
    st.markdown("Filter and drill into individual company compliance profiles.")

    f1, f2, f3 = st.columns(3)
    sel_sector = f1.multiselect("Sector", SECTORS, default=SECTORS[:3])
    sel_region = f2.multiselect("Region", REGIONS, default=REGIONS)
    sel_status = f3.selectbox("Status", ["All", "Compliant", "Failing"])

    filtered = co[
        co["sector"].isin(sel_sector) &
        co["region"].isin(sel_region)
    ]
    if sel_status != "All":
        filtered = filtered[filtered["nitaqat_status"] == sel_status]

    st.markdown(f"**{len(filtered)} companies** match filters")

    # Styled table
    def colour_status(val):
        return "color: #2ecc71; font-weight:bold" if val == "Compliant" else "color: #e74c3c; font-weight:bold"

    display_cols = ["company_name", "sector", "region",
                    "total_employees", "saudi_employees",
                    "saudi_pct", "threshold_pct", "gap_pct", "nitaqat_status"]
    styled = (
        filtered[display_cols]
        .rename(columns={
            "company_name": "Company", "sector": "Sector", "region": "Region",
            "total_employees": "Total Emp.", "saudi_employees": "Saudi Emp.",
            "saudi_pct": "Saudi %", "threshold_pct": "Threshold %",
            "gap_pct": "Gap %", "nitaqat_status": "Status"
        })
        .style.applymap(colour_status, subset=["Status"])
        .format({"Saudi %": "{:.1f}", "Threshold %": "{:.0f}", "Gap %": "{:.1f}"})
    )
    st.dataframe(styled, use_container_width=True, height=400)

    # Company detail card
    st.markdown("---")
    st.subheader("Company Deep-Dive")
    chosen = st.selectbox(
        "Select a company",
        filtered.sort_values("company_name")["company_name"].tolist()
    )
    row = co[co["company_name"] == chosen].iloc[0]
    emp_detail = df[df["company_name"] == chosen]

    d1, d2, d3, d4 = st.columns(4)
    d1.metric("Total Employees",  f"{row['total_employees']}")
    d2.metric("Saudi Employees",  f"{row['saudi_employees']}")
    d3.metric("Saudi %",          f"{row['saudi_pct']:.1f}%",
              delta=f"{'✅' if row['nitaqat_status']=='Compliant' else '❌'} {row['nitaqat_status']}")
    d4.metric("Required Threshold", f"{row['threshold_pct']:.0f}%")

    pie_data = emp_detail["nationality"].value_counts().reset_index()
    pie_data.columns = ["Nationality", "Count"]
    fig_pie = px.pie(
        pie_data, values="Count", names="Nationality",
        color="Nationality",
        color_discrete_map={"Saudi": "#2ecc71", "Expatriate": "#3498db"},
        height=300,
    )
    fig_pie.update_layout(margin=dict(l=0, r=0, t=20, b=0))
    st.plotly_chart(fig_pie, use_container_width=True)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 3 — HIRING OPTIMIZER
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "⚙️ Hiring Optimizer":
    st.title("⚙️ Saudization Hiring Optimizer")
    st.markdown(
        "Use Mixed-Integer Linear Programming (MILP) to find the **minimum-cost** "
        "hiring plan that brings a company into Nitaqat compliance."
    )

    st.markdown("### Company Parameters")
    c1, c2 = st.columns(2)

    company_names = co.sort_values("company_name")["company_name"].tolist()
    chosen_co = c1.selectbox("Select Company (or enter manually below)", company_names)
    use_manual = c2.checkbox("Enter figures manually")

    co_row = co[co["company_name"] == chosen_co].iloc[0]

    if use_manual:
        m1, m2, m3 = st.columns(3)
        current_total  = m1.number_input("Total Employees",   value=int(co_row["total_employees"]),  min_value=1)
        current_saudi  = m2.number_input("Current Saudi Emp", value=int(co_row["saudi_employees"]),  min_value=0)
        sel_sector_opt = m3.selectbox("Sector", SECTORS, index=SECTORS.index(co_row["sector"]))
    else:
        current_total  = int(co_row["total_employees"])
        current_saudi  = int(co_row["saudi_employees"])
        sel_sector_opt = co_row["sector"]
        st.info(
            f"**{chosen_co}** — {current_saudi}/{current_total} Saudi employees "
            f"({co_row['saudi_pct']:.1f}%) in **{sel_sector_opt}** | "
            f"Status: {'✅ Compliant' if co_row['nitaqat_status']=='Compliant' else '❌ Failing'}"
        )

    st.markdown("### Optimizer Settings")
    o1, o2, o3 = st.columns(3)
    monthly_budget = o1.number_input(
        "Monthly Hiring Budget (SAR)",
        value=200_000, min_value=10_000, step=10_000, format="%d"
    )
    target_pct = o2.number_input(
        "Target Saudi % (compliance threshold)",
        value=float(NITAQAT_THRESHOLDS[sel_sector_opt]),
        min_value=1.0, max_value=99.0, step=0.5
    )
    roles_selected = st.multiselect(
        "Roles Available to Hire",
        list(JOB_ROLE_PROFILES.keys()),
        default=["Accountant", "HR Specialist", "Sales Executive", "Admin Assistant"],
    )

    if st.button("🚀 Run Optimizer", type="primary"):
        if not roles_selected:
            st.warning("Please select at least one role.")
        else:
            status, result = run_lp_optimizer(
                sel_sector_opt, current_saudi, current_total,
                monthly_budget, target_pct, roles_selected
            )

            if status == "COMPLIANT":
                st.success(
                    f"✅ **Already Compliant!** Current Saudi % "
                    f"({current_saudi/current_total*100:.1f}%) ≥ target ({target_pct:.1f}%). "
                    f"No action needed."
                )
            elif status == "INFEASIBLE":
                st.error(f"❌ **Infeasible:** {result}")
                st.markdown(
                    "**Suggestions:** Increase monthly budget, reduce target %, "
                    "add more roles, or extend hiring timeline."
                )
            else:
                plan_df = pd.DataFrame(result)
                total_hires = plan_df["Hire Count"].sum()
                total_cost  = plan_df["Monthly Cost (SAR)"].sum()
                new_saudi   = current_saudi + total_hires
                new_total   = current_total + total_hires
                new_pct     = new_saudi / new_total * 100

                st.success(f"✅ **Optimal hiring plan found!**")
                r1, r2, r3, r4 = st.columns(4)
                r1.metric("Total New Hires",      f"{total_hires}")
                r2.metric("Monthly Cost (SAR)",   f"{total_cost:,}")
                r3.metric("New Saudi %",           f"{new_pct:.1f}%",
                          delta=f"+{new_pct - current_saudi/current_total*100:.1f}pp")
                r4.metric("Target Met",            "✅ Yes")

                st.dataframe(
                    plan_df.style.format({"Monthly Cost (SAR)": "{:,}"}),
                    use_container_width=True,
                )

                fig_bar = px.bar(
                    plan_df, x="Role", y="Hire Count",
                    color="Monthly Cost (SAR)",
                    color_continuous_scale="Blues",
                    text="Hire Count",
                    height=320,
                    title="Hiring Plan Breakdown",
                )
                fig_bar.update_layout(margin=dict(l=0, r=0, t=40, b=0))
                st.plotly_chart(fig_bar, use_container_width=True)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 4 — SECTOR ANALYTICS
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "📈 Sector Analytics":
    st.title("📈 Sector Analytics")
    st.markdown("Deep-dive into Saudization patterns, salary distributions, and compliance gaps by sector.")

    sel_s = st.selectbox("Choose Sector", SECTORS)
    sector_df    = df[df["sector"] == sel_s]
    sector_co    = co[co["sector"] == sel_s]
    threshold    = NITAQAT_THRESHOLDS[sel_s]

    s1, s2, s3, s4 = st.columns(4)
    s1.metric("Companies",        f"{len(sector_co)}")
    s2.metric("Total Employees",  f"{len(sector_df):,}")
    s3.metric("Avg Saudi %",      f"{sector_co['saudi_pct'].mean():.1f}%")
    s4.metric("Threshold",        f"{threshold}%")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Saudi % Distribution")
        fig_hist = px.histogram(
            sector_co, x="saudi_pct", nbins=15,
            color="nitaqat_status",
            color_discrete_map={"Compliant": "#2ecc71", "Failing": "#e74c3c"},
            labels={"saudi_pct": "Saudi %", "nitaqat_status": "Status"},
            height=320,
        )
        fig_hist.add_vline(
            x=threshold, line_dash="dash", line_color="orange",
            annotation_text=f"Threshold {threshold}%",
            annotation_position="top right",
        )
        fig_hist.update_layout(margin=dict(l=0, r=0, t=10, b=0), legend_title_text="")
        st.plotly_chart(fig_hist, use_container_width=True)

    with col2:
        st.subheader("Salary Distribution by Nationality")
        fig_box = px.box(
            sector_df, x="nationality", y="monthly_salary_sar",
            color="nationality",
            color_discrete_map={"Saudi": "#2ecc71", "Expatriate": "#3498db"},
            labels={"monthly_salary_sar": "Monthly Salary (SAR)", "nationality": ""},
            height=320,
        )
        fig_box.update_layout(margin=dict(l=0, r=0, t=10, b=0), showlegend=False)
        st.plotly_chart(fig_box, use_container_width=True)

    st.subheader("Company-Level Compliance Table")
    table_cols = ["company_name", "region", "total_employees",
                  "saudi_pct", "threshold_pct", "gap_pct", "nitaqat_status"]

    def colour_status(val):
        return "color: #2ecc71; font-weight:bold" if val == "Compliant" else "color: #e74c3c; font-weight:bold"

    st.dataframe(
        sector_co[table_cols]
        .rename(columns={
            "company_name": "Company", "region": "Region",
            "total_employees": "Employees", "saudi_pct": "Saudi %",
            "threshold_pct": "Required %", "gap_pct": "Gap %",
            "nitaqat_status": "Status"
        })
        .style.applymap(colour_status, subset=["Status"])
        .format({"Saudi %": "{:.1f}", "Required %": "{:.0f}", "Gap %": "{:.1f}"}),
        use_container_width=True,
    )

    # Compliance gap waterfall
    st.subheader("Compliance Gap per Company")
    gap_df = sector_co[sector_co["nitaqat_status"] == "Failing"].sort_values("gap_pct", ascending=False)
    if gap_df.empty:
        st.success("All companies in this sector are compliant! 🎉")
    else:
        fig_gap = px.bar(
            gap_df, x="company_name", y="gap_pct",
            color="gap_pct",
            color_continuous_scale="Reds",
            labels={"company_name": "Company", "gap_pct": "Gap to Threshold (pp)"},
            height=350,
            title=f"Failing Companies — Percentage Points Below {threshold}% Threshold",
        )
        fig_gap.update_layout(margin=dict(l=0, r=0, t=40, b=20),
                              xaxis_tickangle=-30, coloraxis_showscale=False)
        st.plotly_chart(fig_gap, use_container_width=True)
