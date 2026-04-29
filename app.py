import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# ============================================================
# RSM MASS BALANCE DASHBOARD — INFOGRAPHIC STYLE VERSION
# ============================================================

st.set_page_config(
    page_title="RSM Mass Balance Dashboard",
    page_icon="⚗️",
    layout="wide"
)

# ============================================================
# GLOBAL CONSTANTS
# ============================================================

SLURRY_FLOW_M3H = 1950.0
ANNUAL_UPTIME_H = 7536.37
EFFECTIVE_HOURS_JAN_NOV = 6908.3
ANNUALIZATION_FACTOR = 12 / 11

SMBS_STRENGTH_KG_M3 = 3600 / 70      # 51.43 kg/m3
CUSO4_STRENGTH_KG_M3 = 2000 / 16     # 125 kg/m3

SMBS_PRICE_KG = 489.76 / 1250        # $/kg
CUSO4_PRICE_KG = 2790.24 / 1250      # $/kg

PUMP_UNCERTAINTY = 0.10
WADCN_TARGET = 0.5
WADCN_FEED_U = 0.57

# Formal RSM uncertainty results from 8003-line recalculation
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

# Baseline central values from infographic
DEFAULTS = {
    "warehouse_smbs": 106.3,
    "warehouse_cuso4": 12.8,
    "pumps_smbs": 16.9,
    "pumps_cuso4": 43.0,
    "rsm_smbs": 89.4,
    "rsm_cuso4": 12.2,
}

COLORS = {
    "green": "#0B6B2B",
    "blue": "#064A9B",
    "purple": "#5A168D",
    "orange": "#D55E00",
    "navy": "#071B4D",
    "light_green": "#EAF5EA",
    "light_blue": "#EAF2FF",
    "light_purple": "#F3EAFB",
    "gray": "#F7F7F7",
    "red": "#B00020",
    "amber": "#F5A623"
}

# ============================================================
# CSS FOR INFOGRAPHIC STYLE
# ============================================================

st.markdown(
    f"""
    <style>
        .block-container {{
            padding-top: 1.5rem;
            padding-bottom: 1rem;
        }}
        .main-title {{
            text-align: center;
            color: {COLORS["navy"]};
            font-size: 2.35rem;
            font-weight: 900;
            line-height: 1.05;
            margin-bottom: 0.15rem;
        }}
        .subtitle {{
            text-align: center;
            color: #444;
            font-size: 1.05rem;
            font-style: italic;
            margin-bottom: 1rem;
        }}
        .panel {{
            border: 1.5px solid #d9d9d9;
            border-radius: 14px;
            background: white;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
            padding: 0.9rem 0.9rem 1rem 0.9rem;
            min-height: 610px;
        }}
        .panel-header {{
            color: white;
            border-radius: 10px 10px 0 0;
            padding: 0.55rem;
            text-align: center;
            font-weight: 800;
            font-size: 1.05rem;
            margin: -0.9rem -0.9rem 0.45rem -0.9rem;
        }}
        .panel-subtitle {{
            text-align: center;
            font-style: italic;
            font-size: 0.82rem;
            color: #ffffff;
            opacity: 0.95;
            margin-top: -0.25rem;
        }}
        .detox-box {{
            border: 2px solid #6f6f6f;
            border-radius: 18px;
            background: linear-gradient(#f4f5f6, #cbd0d4);
            text-align: center;
            font-weight: 800;
            padding: 1rem 0.3rem;
            margin: 0.65rem auto;
            width: 68%;
            color: #111;
        }}
        .dose-pill {{
            border-radius: 8px;
            color: white;
            font-weight: 800;
            padding: 0.55rem;
            text-align: center;
            margin-bottom: 0.35rem;
            font-size: 0.9rem;
        }}
        .small-card {{
            border: 1px solid #d3d3d3;
            border-radius: 10px;
            background: #fafafa;
            padding: 0.5rem;
            text-align:center;
            font-weight: 700;
            font-size: 0.85rem;
        }}
        .compliance {{
            border-radius: 8px;
            background: #178A3B;
            color: white;
            font-weight: 800;
            text-align: center;
            padding: 0.55rem;
            margin-top: 0.3rem;
        }}
        .section-title {{
            text-align: center;
            font-weight: 900;
            padding: 0.35rem;
            border-radius: 8px;
            margin: 0.65rem 0 0.3rem 0;
        }}
        .note {{
            border: 1px dashed #888;
            border-radius: 8px;
            padding: 0.55rem;
            font-size: 0.78rem;
            background: #fbfbfb;
        }}
        .zone-optimal {{
            background:#EAF5EA;
            border-left: 7px solid #178A3B;
            border-radius: 9px;
            padding:0.7rem;
            font-weight:700;
        }}
        .zone-warning {{
            background:#FFF6E5;
            border-left: 7px solid #F5A623;
            border-radius: 9px;
            padding:0.7rem;
            font-weight:700;
        }}
        .zone-overdose {{
            background:#FDEBEE;
            border-left: 7px solid #B00020;
            border-radius: 9px;
            padding:0.7rem;
            font-weight:700;
        }}
        .big-money {{
            font-size: 2rem;
            color:#0B6B2B;
            font-weight:900;
            text-align:center;
        }}
        .table-note {{
            font-size: 0.78rem;
            color:#555;
        }}
        div[data-testid="stMetricValue"] {{
            font-size: 1.25rem;
        }}
    </style>
    """,
    unsafe_allow_html=True
)

# ============================================================
# HELPERS
# ============================================================

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
        "total_tons": smbs_tons + cuso4_tons,
        "smbs_cost": smbs_cost, "cuso4_cost": cuso4_cost,
        "total_cost": smbs_cost + cuso4_cost,
    }

def zone_label(value, low, high, unit):
    """Color-coded zone relative to recommended operating region."""
    if value < low:
        status = "LOW / POSSIBLE UNDERDOSING"
        cls = "zone-warning"
    elif value > high:
        status = "HIGH / CONSERVATIVE OR OVERDOSING"
        cls = "zone-overdose"
    else:
        status = "OPTIMAL / WITHIN TARGET REGION"
        cls = "zone-optimal"
    st.markdown(
        f"<div class='{cls}'>{status}<br><span style='font-weight:500;'>Current value: {value:.1f} {unit} | Target region: {low:.1f}–{high:.1f} {unit}</span></div>",
        unsafe_allow_html=True
    )

def display_process_visual(color, smbs, cuso4):
    left, center, right = st.columns([1, 2, 1])
    with left:
        st.markdown("<div class='small-card'>Slurry Inflow<br><b>1950 m³/h</b></div>", unsafe_allow_html=True)
    with center:
        st.markdown(
            f"""
            <div style="display:flex; gap:0.4rem; justify-content:center;">
                <div class="dose-pill" style="background:{color};">SMBS<br>{smbs:.1f} mg/L</div>
                <div class="dose-pill" style="background:{COLORS["orange"]};">CuSO₄<br>{cuso4:.1f} mg/L</div>
            </div>
            <div class="detox-box">DETOX TANK<br>2880 m³</div>
            """,
            unsafe_allow_html=True
        )
    with right:
        st.markdown(f"<div class='compliance'>Treated Slurry<br>WADCN ≤ {WADCN_TARGET} ppm</div>", unsafe_allow_html=True)

def result_tables(r, color, uncertainty=None):
    dosing_df = pd.DataFrame({
        "Parameter": ["Slurry flow", "Effective hours", "SMBS dosing", "SMBS mass flow", "CuSO₄ dosing", "CuSO₄ mass flow"],
        "Value": [
            f"{SLURRY_FLOW_M3H:,.0f} m³/h",
            f"{EFFECTIVE_HOURS_JAN_NOV:,.1f} h",
            f"{r['smbs_mgl']:.1f} mg/L",
            f"{r['smbs_kgh']:.1f} kg/h",
            f"{r['cuso4_mgl']:.1f} mg/L",
            f"{r['cuso4_kgh']:.1f} kg/h",
        ],
    })
    st.markdown(f"<div class='section-title' style='background:#f3f3f3;color:{color};'>DOSING SUMMARY</div>", unsafe_allow_html=True)
    st.dataframe(dosing_df, use_container_width=True, hide_index=True)

    consumption_df = pd.DataFrame({
        "Reagent": ["SMBS", "CuSO₄", "TOTAL"],
        "Consumption (tons)": [round(r["smbs_tons"], 1), round(r["cuso4_tons"], 1), round(r["total_tons"], 1)],
        "Mass flow (kg/h avg.)": [round(r["smbs_kgh"], 1), round(r["cuso4_kgh"], 1), round(r["smbs_kgh"] + r["cuso4_kgh"], 1)],
    })
    st.markdown(f"<div class='section-title' style='background:{color};color:white;'>TOTAL REAGENT CONSUMPTION (JAN–NOV 2025)</div>", unsafe_allow_html=True)
    st.dataframe(consumption_df, use_container_width=True, hide_index=True)

    cost_df = pd.DataFrame({
        "Item": ["SMBS cost", "CuSO₄ cost", "TOTAL COST"],
        "Value": [money(r["smbs_cost"]), money(r["cuso4_cost"]), money(r["total_cost"])],
    })
    st.markdown(f"<div class='section-title' style='background:#f3f3f3;color:{color};'>COST SUMMARY (INDICATIVE)</div>", unsafe_allow_html=True)
    st.dataframe(cost_df, use_container_width=True, hide_index=True)

    if uncertainty == "pump":
        st.markdown("<div class='note'>All pump-derived values include ±10% pump uncertainty. These ranges do not reconcile with warehouse consumption.</div>", unsafe_allow_html=True)
    elif uncertainty == "warehouse":
        st.markdown("<div class='note'>Warehouse data represent physically consumed reagents and are treated as the reference baseline. Pump uncertainty is not applied.</div>", unsafe_allow_html=True)
    elif uncertainty == "rsm":
        st.markdown("<div class='note'>RSM values incorporate WADCN feed uncertainty separately. Pump measurement uncertainty is not included in this method.</div>", unsafe_allow_html=True)

def show_panel(title, subtitle, color, default_smbs, default_cuso4, key, uncertainty_note):
    st.markdown(f"<div class='panel'>", unsafe_allow_html=True)
    st.markdown(
        f"<div class='panel-header' style='background:{color};'>{title}<div class='panel-subtitle'>{subtitle}</div></div>",
        unsafe_allow_html=True
    )
    smbs = st.slider("SMBS dosing (mg/L)", 0.0, 150.0, float(default_smbs), 0.1, key=f"{key}_smbs")
    cuso4 = st.slider("CuSO₄ dosing (mg/L)", 0.0, 80.0, float(default_cuso4), 0.1, key=f"{key}_cuso4")

    r = calc_from_mgl(smbs, cuso4)
    display_process_visual(color, smbs, cuso4)

    # Color zones relative to RSM central target bands
    st.markdown("**Operational zone vs RSM target region**")
    zone_label(smbs, 83.7, 95.1, "mg/L SMBS")
    zone_label(cuso4, 11.4, 13.0, "mg/L CuSO₄")

    result_tables(r, color, uncertainty_note)
    st.markdown("</div>", unsafe_allow_html=True)
    return r

# ============================================================
# HEADER
# ============================================================

st.markdown("<div class='main-title'>MASS BALANCE TRANSLATION: FROM LABORATORY OPTIMIZATION TO PLANT OPERATION</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Validation of reagent efficiency based on real plant data | Effective operating hours: 6908.3 h | Slurry flow rate: 1950 m³/h</div>", unsafe_allow_html=True)

with st.expander("Constants and uncertainty rules used in this dashboard"):
    const_df = pd.DataFrame({
        "Parameter": [
            "Slurry flow rate",
            "Annual mill uptime 2025",
            "Effective operating hours Jan–Nov",
            "Annualization factor",
            "SMBS stock solution strength",
            "CuSO₄ stock solution strength",
            "SMBS price",
            "CuSO₄ price",
            "Pump uncertainty",
            "WADCN DETOXFEED expanded uncertainty",
            "Internal WADCN target"
        ],
        "Value": [
            f"{SLURRY_FLOW_M3H:,.0f} m³/h",
            f"{ANNUAL_UPTIME_H:,.2f} h",
            f"{EFFECTIVE_HOURS_JAN_NOV:,.1f} h",
            f"{ANNUALIZATION_FACTOR:.4f}",
            f"{SMBS_STRENGTH_KG_M3:.2f} kg/m³",
            f"{CUSO4_STRENGTH_KG_M3:.2f} kg/m³",
            f"${SMBS_PRICE_KG:.6f}/kg",
            f"${CUSO4_PRICE_KG:.6f}/kg",
            "±10% applied only to actual dosing pumps",
            "±0.57 ppm applied only to RSM WADCN-feed recalculation",
            f"WADCN ≤ {WADCN_TARGET} ppm",
        ]
    })
    st.dataframe(const_df, use_container_width=True, hide_index=True)

# ============================================================
# THREE-PANEL DASHBOARD
# ============================================================

col1, col2, col3 = st.columns(3)

with col1:
    warehouse = show_panel(
        "1. WAREHOUSE (ACTUAL CONSUMPTION)",
        "Reference: Physically consumed reagents",
        COLORS["green"],
        DEFAULTS["warehouse_smbs"],
        DEFAULTS["warehouse_cuso4"],
        "warehouse",
        "warehouse"
    )

with col2:
    pumps = show_panel(
        "2. ACTUAL DOSING PUMPS (CALCULATED)",
        "Based on pump flow integration and solution concentration",
        COLORS["blue"],
        DEFAULTS["pumps_smbs"],
        DEFAULTS["pumps_cuso4"],
        "pumps",
        "pump"
    )
    st.markdown("<div class='section-title' style='background:#EAF2FF;color:#064A9B;'>PUMP ±10% UNCERTAINTY</div>", unsafe_allow_html=True)
    pump_unc = pd.DataFrame({
        "Parameter": ["SMBS dosing", "CuSO₄ dosing", "SMBS kg/h", "CuSO₄ kg/h", "Total cost"],
        "Lower": [
            f"{pumps['smbs_mgl']*0.9:.1f} mg/L",
            f"{pumps['cuso4_mgl']*0.9:.1f} mg/L",
            f"{pumps['smbs_kgh']*0.9:.1f} kg/h",
            f"{pumps['cuso4_kgh']*0.9:.1f} kg/h",
            money(pumps["total_cost"]*0.9)
        ],
        "Central": [
            f"{pumps['smbs_mgl']:.1f} mg/L",
            f"{pumps['cuso4_mgl']:.1f} mg/L",
            f"{pumps['smbs_kgh']:.1f} kg/h",
            f"{pumps['cuso4_kgh']:.1f} kg/h",
            money(pumps["total_cost"])
        ],
        "Upper": [
            f"{pumps['smbs_mgl']*1.1:.1f} mg/L",
            f"{pumps['cuso4_mgl']*1.1:.1f} mg/L",
            f"{pumps['smbs_kgh']*1.1:.1f} kg/h",
            f"{pumps['cuso4_kgh']*1.1:.1f} kg/h",
            money(pumps["total_cost"]*1.1)
        ],
    })
    st.dataframe(pump_unc, use_container_width=True, hide_index=True)

with col3:
    rsm = show_panel(
        "3. ALTERNATIVE METHOD (RSM OPTIMIZED)",
        "Model-based optimized dosing strategy",
        COLORS["purple"],
        DEFAULTS["rsm_smbs"],
        DEFAULTS["rsm_cuso4"],
        "rsm",
        "rsm"
    )

# ============================================================
# FORMAL RSM WADCN UNCERTAINTY TABLE
# ============================================================

st.divider()
st.markdown("<div class='section-title' style='background:#5A168D;color:white;'>FORMAL RSM UNCERTAINTY RESULTS: WADCN ±0.57 ppm APPLIED TO 8003 DATA POINTS</div>", unsafe_allow_html=True)

rsm_unc = pd.DataFrame({
    "Result": [
        "Average dosing (m³/h)",
        "Total consumption (m³)",
        "Total consumption (tons)",
        "Cost estimate (USD)"
    ],
    "SMBS lower": [RSM["smbs_m3h_low"], RSM["smbs_m3_low"], RSM["smbs_tons_low"], RSM["smbs_cost_low"]],
    "SMBS central": [RSM["smbs_m3h_central"], RSM["smbs_m3_central"], RSM["smbs_tons_central"], RSM["smbs_cost_central"]],
    "SMBS upper": [RSM["smbs_m3h_high"], RSM["smbs_m3_high"], RSM["smbs_tons_high"], RSM["smbs_cost_high"]],
    "CuSO₄ lower": [RSM["cuso4_m3h_low"], RSM["cuso4_m3_low"], RSM["cuso4_tons_low"], RSM["cuso4_cost_low"]],
    "CuSO₄ central": [RSM["cuso4_m3h_central"], RSM["cuso4_m3_central"], RSM["cuso4_tons_central"], RSM["cuso4_cost_central"]],
    "CuSO₄ upper": [RSM["cuso4_m3h_high"], RSM["cuso4_m3_high"], RSM["cuso4_tons_high"], RSM["cuso4_cost_high"]],
})
st.dataframe(rsm_unc, use_container_width=True, hide_index=True)

# ============================================================
# COMPARISON & SAVINGS
# ============================================================

st.markdown("<div class='section-title' style='background:#0B6B2B;color:white;'>COMPARISON: RSM OPTIMIZED vs WAREHOUSE (ACTUAL)</div>", unsafe_allow_html=True)

comparison = pd.DataFrame({
    "Reagent": ["SMBS", "CuSO₄", "TOTAL"],
    "Warehouse (tons)": [warehouse["smbs_tons"], warehouse["cuso4_tons"], warehouse["total_tons"]],
    "RSM central (tons)": [RSM["smbs_tons_central"], RSM["cuso4_tons_central"], RSM["smbs_tons_central"] + RSM["cuso4_tons_central"]],
})
comparison["Savings (tons)"] = comparison["Warehouse (tons)"] - comparison["RSM central (tons)"]
comparison["Reduction (%)"] = comparison["Savings (tons)"] / comparison["Warehouse (tons)"] * 100
st.dataframe(comparison, use_container_width=True, hide_index=True)

# Cost savings range
warehouse_cost = warehouse["total_cost"]
savings_lower = warehouse_cost - RSM["total_cost_high"]
savings_upper = warehouse_cost - RSM["total_cost_central"]
annual_lower = savings_lower * ANNUALIZATION_FACTOR
annual_upper = savings_upper * ANNUALIZATION_FACTOR

c1, c2, c3 = st.columns([1.2, 1.2, 1.4])
with c1:
    st.markdown("<div class='section-title' style='background:#EAF5EA;color:#0B6B2B;'>COST SAVINGS RANGE (JAN–NOV 2025)</div>", unsafe_allow_html=True)
    st.metric("Lower / Conservative", money(savings_lower))
    st.metric("Upper / Central", money(savings_upper))
with c2:
    st.markdown("<div class='section-title' style='background:#EAF2FF;color:#064A9B;'>ANNUALIZED COST SAVINGS RANGE</div>", unsafe_allow_html=True)
    st.metric("Lower / Conservative", f"{money(annual_lower)} / year")
    st.metric("Upper / Central", f"{money(annual_upper)} / year")
with c3:
    st.markdown("<div class='section-title' style='background:#F3EAFB;color:#5A168D;'>WADCN COMPLIANCE VISUAL</div>", unsafe_allow_html=True)
    wadcn_margin = st.slider("Illustrative treated WADCN result (ppm)", 0.0, 2.0, 0.45, 0.01)
    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=wadcn_margin,
        delta={"reference": WADCN_TARGET, "increasing": {"color": COLORS["red"]}, "decreasing": {"color": COLORS["green"]}},
        gauge={
            "axis": {"range": [0, 2.0]},
            "bar": {"color": COLORS["purple"]},
            "steps": [
                {"range": [0, WADCN_TARGET], "color": "#DFF3E3"},
                {"range": [WADCN_TARGET, 1.0], "color": "#FFF1CC"},
                {"range": [1.0, 2.0], "color": "#FAD4D8"},
            ],
            "threshold": {"line": {"color": "red", "width": 4}, "thickness": 0.75, "value": WADCN_TARGET},
        },
        title={"text": "Treated WADCN vs 0.5 ppm Target"}
    ))
    fig_gauge.update_layout(height=260, margin=dict(l=20, r=20, t=50, b=10))
    st.plotly_chart(fig_gauge, use_container_width=True)
    if wadcn_margin <= WADCN_TARGET:
        st.success("Compliant with internal target (≤ 0.5 ppm).")
    else:
        st.error("Above internal target: operational action required.")

# ============================================================
# CHARTS
# ============================================================

st.divider()
chart_df = pd.DataFrame({
    "Method": ["Warehouse", "Pump central", "RSM central"],
    "SMBS tons": [warehouse["smbs_tons"], pumps["smbs_tons"], RSM["smbs_tons_central"]],
    "CuSO₄ tons": [warehouse["cuso4_tons"], pumps["cuso4_tons"], RSM["cuso4_tons_central"]],
    "Total cost": [warehouse["total_cost"], pumps["total_cost"], RSM["total_cost_central"]],
})

left, right = st.columns(2)
with left:
    fig = go.Figure()
    fig.add_bar(x=chart_df["Method"], y=chart_df["SMBS tons"], name="SMBS")
    fig.add_bar(x=chart_df["Method"], y=chart_df["CuSO₄ tons"], name="CuSO₄")
    fig.update_layout(title="Total Reagent Consumption", barmode="group", yaxis_title="tons", height=380)
    st.plotly_chart(fig, use_container_width=True)
with right:
    fig2 = go.Figure()
    fig2.add_bar(x=chart_df["Method"], y=chart_df["Total cost"], name="Total cost")
    fig2.update_layout(title="Total Reagent Cost", yaxis_title="USD", height=380)
    st.plotly_chart(fig2, use_container_width=True)

# ============================================================
# FINAL VERDICT
# ============================================================

st.markdown("<div class='section-title' style='background:#071B4D;color:white;'>FINAL VERDICT</div>", unsafe_allow_html=True)
st.markdown(
    """
    The dashboard distinguishes between three fundamentally different evidence streams: physical consumption records,
    pump-derived calculations, and model-based RSM predictions. Pump uncertainty is applied only to the pump-derived
    dataset, while WADCN analytical uncertainty is applied only to the RSM uncertainty evaluation. Warehouse data are
    treated as the physical consumption baseline.

    The optimized RSM dosing strategy reduces SMBS consumption while maintaining a comparable CuSO₄ requirement and
    compliance target basis. Even when WADCN uncertainty is propagated through the full 8003-line dataset, the impact
    on total reagent demand and cost remains small. The conservative savings range remains positive, supporting the
    RSM strategy as a technically robust and economically meaningful decision-support tool.
    """
)
