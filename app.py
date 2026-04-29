import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="RSM Mass Balance Dashboard", page_icon="⚗️", layout="wide")

# Constants
SLURRY_FLOW_M3H = 1950.0
ANNUAL_UPTIME_H = 7536.37
EFFECTIVE_HOURS_JAN_NOV = 6908.3
ANNUALIZATION_FACTOR = 12 / 11

SMBS_STRENGTH_KG_M3 = 3600 / 70
CUSO4_STRENGTH_KG_M3 = 2000 / 16

SMBS_PRICE_KG = 489.76 / 1250
CUSO4_PRICE_KG = 2790.24 / 1250
PUMP_UNCERTAINTY = 0.10

# Formal RSM WADCN uncertainty results from 8003-line recalculation
RSM = {
    "smbs_m3h_low": 2.916, "smbs_m3h_central": 2.932, "smbs_m3h_high": 2.950,
    "cuso4_m3h_low": 0.163, "cuso4_m3h_central": 0.165, "cuso4_m3h_high": 0.166,
    "smbs_m3_low": 23339.34498, "smbs_m3_central": 23468.79088, "smbs_m3_high": 23609.71207,
    "cuso4_m3_low": 1308.155157, "cuso4_m3_central": 1317.045773, "cuso4_m3_high": 1326.497179,
    "smbs_tons_low": 1200.30917, "smbs_tons_central": 1206.966388, "smbs_tons_high": 1214.213764,
    "cuso4_tons_low": 163.5193946, "cuso4_tons_central": 164.6307217, "cuso4_tons_high": 165.8121474,
    "smbs_cost_low": 470290.74, "smbs_cost_central": 472899.09, "smbs_cost_high": 475738.67,
    "cuso4_cost_low": 365006.68, "cuso4_cost_central": 367487.38, "cuso4_cost_high": 370124.55,
}
RSM["total_cost_low"] = RSM["smbs_cost_low"] + RSM["cuso4_cost_low"]
RSM["total_cost_central"] = RSM["smbs_cost_central"] + RSM["cuso4_cost_central"]
RSM["total_cost_high"] = RSM["smbs_cost_high"] + RSM["cuso4_cost_high"]

def money(x):
    return f"${x:,.0f}"

def num(x, d=1):
    return f"{x:,.{d}f}"

def calc_from_mgl(smbs_mgl, cuso4_mgl):
    smbs_kgh = smbs_mgl * SLURRY_FLOW_M3H / 1000
    cuso4_kgh = cuso4_mgl * SLURRY_FLOW_M3H / 1000
    smbs_m3h = smbs_kgh / SMBS_STRENGTH_KG_M3
    cuso4_m3h = cuso4_kgh / CUSO4_STRENGTH_KG_M3
    smbs_tons = smbs_kgh * EFFECTIVE_HOURS_JAN_NOV / 1000
    cuso4_tons = cuso4_kgh * EFFECTIVE_HOURS_JAN_NOV / 1000
    smbs_cost = smbs_tons * 1000 * SMBS_PRICE_KG
    cuso4_cost = cuso4_tons * 1000 * CUSO4_PRICE_KG
    return {
        "smbs_mgl": smbs_mgl, "cuso4_mgl": cuso4_mgl,
        "smbs_kgh": smbs_kgh, "cuso4_kgh": cuso4_kgh,
        "smbs_m3h": smbs_m3h, "cuso4_m3h": cuso4_m3h,
        "smbs_tons": smbs_tons, "cuso4_tons": cuso4_tons,
        "smbs_cost": smbs_cost, "cuso4_cost": cuso4_cost,
        "total_cost": smbs_cost + cuso4_cost,
    }

def output_table(r):
    rows = [
        ["SMBS dosing", r["smbs_mgl"], "mg/L"],
        ["CuSO₄ dosing", r["cuso4_mgl"], "mg/L"],
        ["SMBS mass flow", r["smbs_kgh"], "kg/h"],
        ["CuSO₄ mass flow", r["cuso4_kgh"], "kg/h"],
        ["SMBS solution flow", r["smbs_m3h"], "m³/h"],
        ["CuSO₄ solution flow", r["cuso4_m3h"], "m³/h"],
        ["SMBS consumption", r["smbs_tons"], "tons"],
        ["CuSO₄ consumption", r["cuso4_tons"], "tons"],
        ["SMBS cost", r["smbs_cost"], "$"],
        ["CuSO₄ cost", r["cuso4_cost"], "$"],
        ["Total cost", r["total_cost"], "$"],
    ]
    return pd.DataFrame(rows, columns=["Parameter", "Value", "Unit"])

def show_section(title, subtitle, smbs_default, cuso4_default, key, uncertainty=None):
    st.markdown(f"### {title}")
    st.caption(subtitle)

    smbs = st.slider(f"{title}: SMBS dosing (mg/L)", 0.0, 150.0, float(smbs_default), 0.1, key=f"{key}_smbs")
    cuso4 = st.slider(f"{title}: CuSO₄ dosing (mg/L)", 0.0, 80.0, float(cuso4_default), 0.1, key=f"{key}_cuso4")

    r = calc_from_mgl(smbs, cuso4)

    a, b = st.columns(2)
    with a:
        st.metric("SMBS kg/h", num(r["smbs_kgh"], 1))
        st.metric("SMBS tons", num(r["smbs_tons"], 1))
        st.metric("SMBS cost", money(r["smbs_cost"]))
    with b:
        st.metric("CuSO₄ kg/h", num(r["cuso4_kgh"], 1))
        st.metric("CuSO₄ tons", num(r["cuso4_tons"], 1))
        st.metric("CuSO₄ cost", money(r["cuso4_cost"]))

    st.metric("Total cost, Jan–Nov 2025", money(r["total_cost"]))

    with st.expander("Full calculation table"):
        st.dataframe(output_table(r), use_container_width=True, hide_index=True)

    if uncertainty == "pump":
        st.info("±10% pump uncertainty is applied only to this pump-derived dataset.")
        unc = pd.DataFrame({
            "Parameter": ["SMBS mg/L", "CuSO₄ mg/L", "SMBS kg/h", "CuSO₄ kg/h", "SMBS tons", "CuSO₄ tons", "Total cost"],
            "Lower (-10%)": [r["smbs_mgl"]*0.9, r["cuso4_mgl"]*0.9, r["smbs_kgh"]*0.9, r["cuso4_kgh"]*0.9, r["smbs_tons"]*0.9, r["cuso4_tons"]*0.9, r["total_cost"]*0.9],
            "Central": [r["smbs_mgl"], r["cuso4_mgl"], r["smbs_kgh"], r["cuso4_kgh"], r["smbs_tons"], r["cuso4_tons"], r["total_cost"]],
            "Upper (+10%)": [r["smbs_mgl"]*1.1, r["cuso4_mgl"]*1.1, r["smbs_kgh"]*1.1, r["cuso4_kgh"]*1.1, r["smbs_tons"]*1.1, r["cuso4_tons"]*1.1, r["total_cost"]*1.1],
        })
        st.dataframe(unc, use_container_width=True, hide_index=True)

    if uncertainty == "rsm":
        st.info("The sliders show the central RSM scenario. The formal WADCN ±0.57 ppm uncertainty results from the 8003-line recalculation are shown below.")

    return r

st.title("⚗️ RSM Mass Balance Interactive Dashboard")
st.write("Interactive dashboard for warehouse consumption, pump-derived dosing, and RSM optimized dosing.")

with st.expander("Global constants"):
    st.dataframe(pd.DataFrame({
        "Parameter": [
            "Slurry flow rate", "Annual mill uptime 2025", "Effective operating hours Jan–Nov",
            "SMBS solution strength", "CuSO₄ solution strength", "SMBS price", "CuSO₄ price",
            "Pump uncertainty", "WADCN uncertainty"
        ],
        "Value": [
            f"{SLURRY_FLOW_M3H:,.1f} m³/h", f"{ANNUAL_UPTIME_H:,.2f} h", f"{EFFECTIVE_HOURS_JAN_NOV:,.1f} h",
            f"{SMBS_STRENGTH_KG_M3:.2f} kg/m³", f"{CUSO4_STRENGTH_KG_M3:.2f} kg/m³",
            f"${SMBS_PRICE_KG:.6f}/kg", f"${CUSO4_PRICE_KG:.6f}/kg",
            "±10% applied only to Actual Dosing Pumps", "±0.57 ppm applied only to RSM WADCN-feed uncertainty"
        ]
    }), use_container_width=True, hide_index=True)

col1, col2, col3 = st.columns(3)
with col1:
    warehouse = show_section("Warehouse (Actual Consumption)", "Physical reagent consumption reference.", 106.3, 12.8, "warehouse")
with col2:
    pumps = show_section("Actual Dosing Pumps (Calculated)", "Pump flow integration with ±10% uncertainty.", 16.9, 43.0, "pumps", "pump")
with col3:
    rsm = show_section("Alternative Method (RSM Optimized)", "Model-based optimized dosing strategy.", 89.4, 12.2, "rsm", "rsm")

st.divider()
st.subheader("📊 Comparison of Consumption and Cost")

comparison = pd.DataFrame({
    "Method": ["Warehouse", "Pumps", "RSM Optimized"],
    "SMBS tons": [warehouse["smbs_tons"], pumps["smbs_tons"], rsm["smbs_tons"]],
    "CuSO₄ tons": [warehouse["cuso4_tons"], pumps["cuso4_tons"], rsm["cuso4_tons"]],
    "Total cost ($)": [warehouse["total_cost"], pumps["total_cost"], rsm["total_cost"]],
})

c1, c2 = st.columns(2)
with c1:
    fig = go.Figure()
    fig.add_bar(x=comparison["Method"], y=comparison["SMBS tons"], name="SMBS")
    fig.add_bar(x=comparison["Method"], y=comparison["CuSO₄ tons"], name="CuSO₄")
    fig.update_layout(title="Reagent Consumption, Jan–Nov 2025", barmode="group", yaxis_title="tons")
    st.plotly_chart(fig, use_container_width=True)

with c2:
    fig2 = go.Figure()
    fig2.add_bar(x=comparison["Method"], y=comparison["Total cost ($)"], name="Total cost")
    fig2.update_layout(title="Total Reagent Cost, Jan–Nov 2025", yaxis_title="USD")
    st.plotly_chart(fig2, use_container_width=True)

st.dataframe(comparison, use_container_width=True, hide_index=True)

st.subheader("🟪 Formal RSM WADCN Uncertainty Results")
rsm_unc = pd.DataFrame({
    "Result": ["Average dosing (m³/h)", "Total consumption (m³)", "Total consumption (tons)", "Cost estimate ($)"],
    "SMBS lower": [RSM["smbs_m3h_low"], RSM["smbs_m3_low"], RSM["smbs_tons_low"], RSM["smbs_cost_low"]],
    "SMBS central": [RSM["smbs_m3h_central"], RSM["smbs_m3_central"], RSM["smbs_tons_central"], RSM["smbs_cost_central"]],
    "SMBS upper": [RSM["smbs_m3h_high"], RSM["smbs_m3_high"], RSM["smbs_tons_high"], RSM["smbs_cost_high"]],
    "CuSO₄ lower": [RSM["cuso4_m3h_low"], RSM["cuso4_m3_low"], RSM["cuso4_tons_low"], RSM["cuso4_cost_low"]],
    "CuSO₄ central": [RSM["cuso4_m3h_central"], RSM["cuso4_m3_central"], RSM["cuso4_tons_central"], RSM["cuso4_cost_central"]],
    "CuSO₄ upper": [RSM["cuso4_m3h_high"], RSM["cuso4_m3_high"], RSM["cuso4_tons_high"], RSM["cuso4_cost_high"]],
})
st.dataframe(rsm_unc, use_container_width=True, hide_index=True)

st.subheader("💰 Cost Savings Range")
warehouse_cost = warehouse["total_cost"]
savings_lower = warehouse_cost - RSM["total_cost_high"]
savings_upper = warehouse_cost - RSM["total_cost_central"]
annual_lower = savings_lower * ANNUALIZATION_FACTOR
annual_upper = savings_upper * ANNUALIZATION_FACTOR

a, b, c, d = st.columns(4)
a.metric("Savings lower, Jan–Nov", money(savings_lower))
b.metric("Savings upper, Jan–Nov", money(savings_upper))
c.metric("Annualized lower", money(annual_lower))
d.metric("Annualized upper", money(annual_upper))

st.caption("Lower savings = Warehouse cost − RSM upper-bound cost. Upper savings = Warehouse cost − RSM central cost.")

st.subheader("✅ Final Interpretation")
st.write(
    "This dashboard separates warehouse consumption, pump-derived calculations, and RSM model-based predictions. "
    "Pump uncertainty is applied only to the pump-derived dataset. WADCN uncertainty is applied only to the RSM evaluation. "
    "Warehouse data are treated as the physical consumption reference. The RSM strategy reduces SMBS demand while maintaining comparable CuSO₄ demand, and the formal WADCN uncertainty propagation shows limited impact on total reagent demand and cost."
)
