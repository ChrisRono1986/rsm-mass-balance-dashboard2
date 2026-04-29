import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="RSM Mass Balance Dashboard", page_icon="⚗️", layout="wide")

# =========================
# CONSTANTS
# =========================
SLURRY_FLOW_M3H = 1950.0
ANNUAL_UPTIME_H = 7536.37
EFFECTIVE_HOURS_JAN_NOV = 6908.3
ANNUALIZATION_FACTOR = 12 / 11

SMBS_STRENGTH_KG_M3 = 3600 / 70
CUSO4_STRENGTH_KG_M3 = 2000 / 16

SMBS_PRICE_KG = 489.76 / 1250
CUSO4_PRICE_KG = 2790.24 / 1250

PUMP_UNCERTAINTY = 0.10
WADCN_TARGET = 0.5

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

COLORS = {
    "green": "#0B6B2B",
    "blue": "#064A9B",
    "purple": "#5A168D",
    "orange": "#D55E00",
    "navy": "#071B4D",
    "red": "#B00020",
    "amber": "#F5A623",
}

DEFAULTS = {
    "warehouse_smbs": 106.3,
    "warehouse_cuso4": 12.8,
    "pumps_smbs": 16.9,
    "pumps_cuso4": 43.0,
    "rsm_smbs": 89.4,
    "rsm_cuso4": 12.2,
}

# Validated infographic/thesis baseline values for the headline savings range.
# Lower savings = Warehouse actual cost - RSM upper-bound cost.
# Upper savings = Warehouse actual cost - RSM central cost.
WAREHOUSE_ACTUAL_COST_BASELINE = 945000.00
RSM_CENTRAL_COST_BASELINE = 840386.47
RSM_UPPER_COST_BASELINE = 845863.22

# =========================
# CSS
# =========================
st.markdown(
    """
    <style>
    .stApp {
        background-color: #dff3ff;
        background-image:
            radial-gradient(ellipse at 20% 20%, rgba(6, 74, 155, 0.18) 0%, rgba(6, 74, 155, 0.18) 1px, transparent 2px),
            radial-gradient(ellipse at 80% 10%, rgba(6, 74, 155, 0.14) 0%, rgba(6, 74, 155, 0.14) 1px, transparent 2px),
            repeating-radial-gradient(ellipse at 15% 35%, transparent 0px, transparent 32px, rgba(6, 74, 155, 0.10) 33px, transparent 35px),
            repeating-radial-gradient(ellipse at 85% 75%, transparent 0px, transparent 38px, rgba(6, 74, 155, 0.09) 39px, transparent 42px),
            repeating-radial-gradient(ellipse at 50% 50%, transparent 0px, transparent 54px, rgba(6, 74, 155, 0.055) 55px, transparent 58px);
        background-attachment: fixed;
    }
    .block-container {
        padding-top: 2.4rem;
        padding-bottom: 1rem;
        max-width: 98%;
    }
    .title-card {
        background: rgba(255,255,255,0.92);
        border: 1px solid #d9d9d9;
        border-radius: 14px;
        padding: 1rem 1.2rem 0.85rem 1.2rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    }
    .title {
        text-align:center;
        color:#071B4D;
        font-weight:900;
        font-size:2rem;
        line-height:1.15;
        margin:0;
        padding:0;
    }
    .subtitle {
        text-align:center;
        color:#555;
        font-style:italic;
        font-size:1rem;
        margin-top:0.35rem;
        margin-bottom:0;
    }
    .header-box {
        color:white;
        padding:0.6rem;
        border-radius:12px;
        text-align:center;
        font-size:1rem;
        font-weight:900;
        margin-bottom:0.25rem;
    }
    .subheader-small {
        font-size:0.82rem;
        font-style:italic;
        font-weight:600;
        opacity:0.95;
    }
    .pump-wrap {
        display:flex;
        align-items:center;
        justify-content:center;
        margin:0.45rem 0 0.6rem 0;
    }
    .pump-card {
        border: 1px solid #d0d0d0;
        border-radius: 12px;
        background: rgba(255,255,255,0.92);
        padding: 0.55rem;
        text-align:center;
        box-shadow: 0 2px 5px rgba(0,0,0,0.06);
        width:100%;
    }
    .pump-label {
        font-size:0.82rem;
        font-weight:800;
        color:#333;
        margin-top:0.25rem;
    }
    .uncertainty-banner {
        border:1px solid #cfcfcf;
        border-radius:10px;
        padding:0.65rem;
        margin:0.45rem 0 0.65rem 0;
        background:#fbfbfb;
        font-size:0.86rem;
        line-height:1.25;
    }
    .section-label {
        padding:0.32rem;
        border-radius:8px;
        text-align:center;
        font-weight:900;
        margin-top:0.65rem;
        margin-bottom:0.25rem;
    }
    .dose-box {
        color:white;
        border-radius:8px;
        padding:0.6rem;
        text-align:center;
        font-weight:900;
        margin-bottom:0.45rem;
        min-height:92px;
    }
    .detox {
        border:2px solid #666;
        border-radius:18px;
        background:linear-gradient(#f5f6f7,#cdd2d6);
        padding:1rem;
        text-align:center;
        color:#111;
        font-weight:900;
        margin:0.3rem 0;
    }
    .flow-box {
        border:1px solid #bbb;
        border-radius:8px;
        background:#fafafa;
        padding:0.55rem;
        text-align:center;
        font-weight:800;
    }
    .compliance {
        border-radius:8px;
        background:#178A3B;
        color:white;
        padding:0.55rem;
        text-align:center;
        font-weight:900;
    }
    .note {
        border:1px dashed #999;
        border-radius:8px;
        padding:0.55rem;
        background:#fbfbfb;
        font-size:0.82rem;
        margin-top:0.4rem;
    }
    .zone-optimal {
        background:#EAF5EA;
        border-left:7px solid #178A3B;
        border-radius:9px;
        padding:0.55rem;
        font-weight:700;
        margin-bottom:0.35rem;
    }
    .zone-warning {
        background:#FFF6E5;
        border-left:7px solid #F5A623;
        border-radius:9px;
        padding:0.55rem;
        font-weight:700;
        margin-bottom:0.35rem;
    }
    .zone-overdose {
        background:#FDEBEE;
        border-left:7px solid #B00020;
        border-radius:9px;
        padding:0.55rem;
        font-weight:700;
        margin-bottom:0.35rem;
    }
    div[data-testid="stMetricValue"] {
        font-size:1.15rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# =========================
# HELPERS
# =========================
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

def section_title(text, bg, fg="white"):
    st.markdown(
        f"<div class='section-label' style='background:{bg};color:{fg};'>{text}</div>",
        unsafe_allow_html=True,
    )

def panel_header(title, subtitle, color):
    st.markdown(
        f"""
        <div class="header-box" style="background:{color};">
            {title}<br><span class="subheader-small">{subtitle}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

def pump_svg(main_color, accent_color="#D55E00"):
    """Inline SVG pump illustration used as a lightweight dashboard visual."""
    return f"""
    <svg width="100%" height="92" viewBox="0 0 420 150" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="dosing pump">
        <defs>
            <linearGradient id="tankGrad" x1="0" x2="1">
                <stop offset="0%" stop-color="#f9fbfc"/>
                <stop offset="100%" stop-color="#cfd8df"/>
            </linearGradient>
        </defs>
        <!-- skid base -->
        <rect x="35" y="118" width="350" height="12" rx="6" fill="#6b7780"/>
        <rect x="55" y="128" width="55" height="9" rx="3" fill="#46515a"/>
        <rect x="310" y="128" width="55" height="9" rx="3" fill="#46515a"/>
        <!-- pump motor -->
        <rect x="60" y="55" width="115" height="58" rx="14" fill="{main_color}" opacity="0.95"/>
        <circle cx="92" cy="84" r="18" fill="#ffffff" opacity="0.25"/>
        <rect x="82" y="34" width="48" height="24" rx="5" fill="#30363b"/>
        <!-- pump head -->
        <circle cx="195" cy="83" r="32" fill="url(#tankGrad)" stroke="#4c5963" stroke-width="4"/>
        <circle cx="195" cy="83" r="14" fill="{accent_color}" opacity="0.85"/>
        <!-- suction/discharge tubing -->
        <path d="M226 83 C262 83, 262 45, 303 45" stroke="{accent_color}" stroke-width="10" fill="none" stroke-linecap="round"/>
        <path d="M226 88 C270 95, 290 108, 350 108" stroke="{main_color}" stroke-width="8" fill="none" stroke-linecap="round" opacity="0.85"/>
        <rect x="303" y="34" width="70" height="22" rx="8" fill="{accent_color}" opacity="0.9"/>
        <rect x="348" y="98" width="45" height="20" rx="7" fill="{main_color}" opacity="0.9"/>
        <!-- flow arrows -->
        <polygon points="282,37 296,45 282,53" fill="#ffffff"/>
        <polygon points="330,100 344,108 330,116" fill="#ffffff"/>
        <!-- label plate -->
        <rect x="70" y="94" width="92" height="12" rx="4" fill="#ffffff" opacity="0.7"/>
    </svg>
    """

def pump_visual(label, main_color, accent_color="#D55E00"):
    st.markdown(
        f"""
        <div class="pump-wrap">
            <div class="pump-card">
                {pump_svg(main_color, accent_color)}
                <div class="pump-label">{label}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

def uncertainty_banner(note_type, color):
    if note_type == "pump":
        st.markdown(
            f"""
            <div class="uncertainty-banner" style="border-left:7px solid {color};">
                <b>PUMP MEASUREMENT UNCERTAINTY: ±10%</b><br>
                All pump-derived values are reported as a range (min–max).<br>
                Ranges reflect the uncertainty of dosing pumps.
            </div>
            """,
            unsafe_allow_html=True,
        )
    elif note_type == "rsm":
        st.markdown(
            f"""
            <div class="uncertainty-banner" style="border-left:7px solid {color};">
                <b>MODEL-BASED VALUES (WADCN UNCERTAINTY APPLIED)</b><br>
                WADCN expanded uncertainty: ±0.57 ppm.<br>
                Results shown as lower–central–upper estimates.
            </div>
            """,
            unsafe_allow_html=True,
        )

def dose_pills(smbs, cuso4, main_color, note_type, r):
    a, b = st.columns(2)

    with a:
        if note_type == "pump":
            text = f"""
            <b>SMBS Dosing</b><br>
            {smbs:.1f} ±10% mg/L<br>
            ({smbs*0.9:.1f} – {smbs*1.1:.1f} mg/L)<br>
            ({r['smbs_kgh']*0.9:.1f} – {r['smbs_kgh']*1.1:.1f} kg/h)
            """
        elif note_type == "rsm":
            text = """
            <b>SMBS Dosing</b><br>
            2.916 – 2.932 – 2.950 m³/hr<br>
            (89.4 mg/L)<br>
            (174.3 kg/h)
            """
        else:
            text = f"""
            <b>SMBS Dosing</b><br>
            {smbs:.1f} mg/L<br>
            ({r['smbs_kgh']:.1f} kg/h)
            """
        st.markdown(f"<div class='dose-box' style='background:{main_color};'>{text}</div>", unsafe_allow_html=True)

    with b:
        if note_type == "pump":
            text = f"""
            <b>CuSO₄ Dosing</b><br>
            {cuso4:.1f} ±10% mg/L<br>
            ({cuso4*0.9:.1f} – {cuso4*1.1:.1f} mg/L)<br>
            ({r['cuso4_kgh']*0.9:.1f} – {r['cuso4_kgh']*1.1:.1f} kg/h)
            """
        elif note_type == "rsm":
            text = """
            <b>CuSO₄ Dosing</b><br>
            0.163 – 0.165 – 0.166 m³/hr<br>
            (12.2 mg/L)<br>
            (23.8 kg/h)
            """
        else:
            text = f"""
            <b>CuSO₄ Dosing</b><br>
            {cuso4:.1f} mg/L<br>
            ({r['cuso4_kgh']:.1f} kg/h)
            """
        st.markdown(f"<div class='dose-box' style='background:{COLORS['orange']};'>{text}</div>", unsafe_allow_html=True)

def process_visual():
    a, b, c = st.columns([1, 1.5, 1])
    with a:
        st.markdown("<div class='flow-box'>Slurry Inflow<br>1950 m³/h</div>", unsafe_allow_html=True)
    with b:
        st.markdown("<div class='detox'>DETOX TANK<br>2880 m³</div>", unsafe_allow_html=True)
    with c:
        st.markdown("<div class='compliance'>Treated Slurry<br>WADCN ≤ 0.5 ppm</div>", unsafe_allow_html=True)

def zone_label(value, low, high, unit):
    if value < low:
        cls, status = "zone-warning", "LOW / POSSIBLE UNDERDOSING"
    elif value > high:
        cls, status = "zone-overdose", "HIGH / CONSERVATIVE OR OVERDOSING"
    else:
        cls, status = "zone-optimal", "OPTIMAL / WITHIN TARGET REGION"
    st.markdown(
        f"<div class='{cls}'>{status}<br><span style='font-weight:500;'>Value: {value:.1f} {unit} | Target: {low:.1f}–{high:.1f}</span></div>",
        unsafe_allow_html=True,
    )

def tables(r, color, note_type):
    section_title("DOSING SUMMARY", "#F2F2F2", color)
    dosing = pd.DataFrame({
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
    st.dataframe(dosing, use_container_width=True, hide_index=True)

    section_title("TOTAL REAGENT CONSUMPTION (JAN–NOV 2025)", color)
    cons = pd.DataFrame({
        "Reagent": ["SMBS", "CuSO₄", "TOTAL"],
        "Consumption (tons)": [round(r["smbs_tons"], 1), round(r["cuso4_tons"], 1), round(r["total_tons"], 1)],
        "Mass flow (kg/h avg.)": [round(r["smbs_kgh"], 1), round(r["cuso4_kgh"], 1), round(r["smbs_kgh"] + r["cuso4_kgh"], 1)],
    })
    st.dataframe(cons, use_container_width=True, hide_index=True)

    section_title("COST SUMMARY (INDICATIVE)", "#F2F2F2", color)
    costs = pd.DataFrame({
        "Item": ["SMBS cost", "CuSO₄ cost", "TOTAL COST"],
        "Value": [money(r["smbs_cost"]), money(r["cuso4_cost"]), money(r["total_cost"])],
    })
    st.dataframe(costs, use_container_width=True, hide_index=True)

    if note_type == "warehouse":
        st.markdown("<div class='note'>Warehouse data represent physically consumed reagents and are treated as the reference baseline. Pump uncertainty is not applied.</div>", unsafe_allow_html=True)
    elif note_type == "pump":
        st.markdown("<div class='note'>Pump-derived values include ±10% pump uncertainty. These ranges do not reconcile with warehouse consumption.</div>", unsafe_allow_html=True)
    elif note_type == "rsm":
        st.markdown("<div class='note'>RSM values incorporate WADCN uncertainty separately. Pump measurement uncertainty is not included in this method.</div>", unsafe_allow_html=True)

def show_panel(title, subtitle, color, default_smbs, default_cuso4, key, note_type):
    with st.container(border=True):
        panel_header(title, subtitle, color)
        uncertainty_banner(note_type, color)
        pump_visual("SMBS + CuSO₄ dosing pump system", color, COLORS["orange"])

        smbs = st.slider("SMBS dosing (mg/L)", 0.0, 150.0, float(default_smbs), 0.1, key=f"{key}_smbs")
        cuso4 = st.slider("CuSO₄ dosing (mg/L)", 0.0, 80.0, float(default_cuso4), 0.1, key=f"{key}_cuso4")

        r = calc_from_mgl(smbs, cuso4)
        dose_pills(smbs, cuso4, color, note_type, r)
        process_visual()

        st.markdown("**Operational zone vs RSM target region**")
        zone_label(smbs, 83.7, 95.1, "mg/L SMBS")
        zone_label(cuso4, 11.4, 13.0, "mg/L CuSO₄")

        tables(r, color, note_type)
        return r

# =========================
# APP
# =========================
st.markdown(
    """
    <div class="title-card">
        <div class="title">MASS BALANCE TRANSLATION: FROM LABORATORY OPTIMIZATION TO PLANT OPERATION</div>
        <div class="subtitle">Validation of reagent efficiency based on real plant data | Effective operating hours: 6908.3 h | Slurry flow rate: 1950 m³/h</div>
    </div>
    """,
    unsafe_allow_html=True
)

with st.expander("Constants and uncertainty rules used in this dashboard"):
    constants = pd.DataFrame({
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
            "Internal WADCN target",
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
        ],
    })
    st.dataframe(constants, use_container_width=True, hide_index=True)

col1, col2, col3 = st.columns(3)

with col1:
    warehouse = show_panel(
        "1. WAREHOUSE (ACTUAL CONSUMPTION)",
        "Reference: physically consumed reagents",
        COLORS["green"],
        DEFAULTS["warehouse_smbs"],
        DEFAULTS["warehouse_cuso4"],
        "warehouse",
        "warehouse",
    )

with col2:
    pumps = show_panel(
        "2. ACTUAL DOSING PUMPS (CALCULATED)",
        "Based on pump flow integration and solution concentration",
        COLORS["blue"],
        DEFAULTS["pumps_smbs"],
        DEFAULTS["pumps_cuso4"],
        "pumps",
        "pump",
    )

    section_title("PUMP ±10% UNCERTAINTY", "#EAF2FF", COLORS["blue"])
    pump_unc = pd.DataFrame({
        "Parameter": ["SMBS dosing", "CuSO₄ dosing", "SMBS kg/h", "CuSO₄ kg/h", "Total cost"],
        "Lower": [
            f"{pumps['smbs_mgl']*0.9:.1f} mg/L",
            f"{pumps['cuso4_mgl']*0.9:.1f} mg/L",
            f"{pumps['smbs_kgh']*0.9:.1f} kg/h",
            f"{pumps['cuso4_kgh']*0.9:.1f} kg/h",
            money(pumps["total_cost"]*0.9),
        ],
        "Central": [
            f"{pumps['smbs_mgl']:.1f} mg/L",
            f"{pumps['cuso4_mgl']:.1f} mg/L",
            f"{pumps['smbs_kgh']:.1f} kg/h",
            f"{pumps['cuso4_kgh']:.1f} kg/h",
            money(pumps["total_cost"]),
        ],
        "Upper": [
            f"{pumps['smbs_mgl']*1.1:.1f} mg/L",
            f"{pumps['cuso4_mgl']*1.1:.1f} mg/L",
            f"{pumps['smbs_kgh']*1.1:.1f} kg/h",
            f"{pumps['cuso4_kgh']*1.1:.1f} kg/h",
            money(pumps["total_cost"]*1.1),
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
        "rsm",
    )

# Formal RSM WADCN uncertainty table
st.divider()
section_title("FORMAL RSM UNCERTAINTY RESULTS: WADCN ±0.57 ppm APPLIED TO 8003 DATA POINTS", COLORS["purple"])
rsm_unc = pd.DataFrame({
    "Result": ["Average dosing (m³/h)", "Total consumption (m³)", "Total consumption (tons)", "Cost estimate (USD)"],
    "SMBS lower": [RSM["smbs_m3h_low"], RSM["smbs_m3_low"], RSM["smbs_tons_low"], RSM["smbs_cost_low"]],
    "SMBS central": [RSM["smbs_m3h_central"], RSM["smbs_m3_central"], RSM["smbs_tons_central"], RSM["smbs_cost_central"]],
    "SMBS upper": [RSM["smbs_m3h_high"], RSM["smbs_m3_high"], RSM["smbs_tons_high"], RSM["smbs_cost_high"]],
    "CuSO₄ lower": [RSM["cuso4_m3h_low"], RSM["cuso4_m3_low"], RSM["cuso4_tons_low"], RSM["cuso4_cost_low"]],
    "CuSO₄ central": [RSM["cuso4_m3h_central"], RSM["cuso4_m3_central"], RSM["cuso4_tons_central"], RSM["cuso4_cost_central"]],
    "CuSO₄ upper": [RSM["cuso4_m3h_high"], RSM["cuso4_m3_high"], RSM["cuso4_tons_high"], RSM["cuso4_cost_high"]],
})
st.dataframe(rsm_unc, use_container_width=True, hide_index=True)

# Comparison
st.divider()
section_title("COMPARISON: RSM OPTIMIZED vs WAREHOUSE (ACTUAL)", COLORS["green"])
comparison = pd.DataFrame({
    "Reagent": ["SMBS", "CuSO₄", "TOTAL"],
    "Warehouse (tons)": [warehouse["smbs_tons"], warehouse["cuso4_tons"], warehouse["total_tons"]],
    "RSM central (tons)": [RSM["smbs_tons_central"], RSM["cuso4_tons_central"], RSM["smbs_tons_central"] + RSM["cuso4_tons_central"]],
})
comparison["Savings (tons)"] = comparison["Warehouse (tons)"] - comparison["RSM central (tons)"]
comparison["Reduction (%)"] = comparison["Savings (tons)"] / comparison["Warehouse (tons)"] * 100
st.dataframe(comparison, use_container_width=True, hide_index=True)

# Headline savings are based on the validated infographic/thesis baseline,
# not on the interactive Warehouse sliders. This keeps the formal reported
# savings range consistent with the thesis figure.
warehouse_cost = WAREHOUSE_ACTUAL_COST_BASELINE
savings_lower = WAREHOUSE_ACTUAL_COST_BASELINE - RSM_UPPER_COST_BASELINE
savings_upper = WAREHOUSE_ACTUAL_COST_BASELINE - RSM_CENTRAL_COST_BASELINE
annual_lower = savings_lower * ANNUALIZATION_FACTOR
annual_upper = savings_upper * ANNUALIZATION_FACTOR

# Optional live savings based on the current interactive Warehouse sliders.
live_savings_lower = warehouse["total_cost"] - RSM["total_cost_high"]
live_savings_upper = warehouse["total_cost"] - RSM["total_cost_central"]
live_annual_lower = live_savings_lower * ANNUALIZATION_FACTOR
live_annual_upper = live_savings_upper * ANNUALIZATION_FACTOR

c1, c2, c3 = st.columns([1.1, 1.1, 1.4])

with c1:
    with st.container(border=True):
        section_title("COST SAVINGS RANGE (JAN–NOV 2025)", "#EAF5EA", COLORS["green"])
        st.metric("Lower / Conservative", money(savings_lower))
        st.metric("Upper / Central", money(savings_upper))

with c2:
    with st.container(border=True):
        section_title("ANNUALIZED COST SAVINGS RANGE", "#EAF2FF", COLORS["blue"])
        st.metric("Lower / Conservative", f"{money(annual_lower)} / year")
        st.metric("Upper / Central", f"{money(annual_upper)} / year")
        st.caption("Uses validated baseline: Warehouse actual cost $945,000.")

with c3:
    with st.container(border=True):
        section_title("WADCN COMPLIANCE VISUAL", "#F3EAFB", COLORS["purple"])
        wadcn = st.slider("Illustrative treated WADCN result (ppm)", 0.0, 2.0, 0.45, 0.01)
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=wadcn,
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
            title={"text": "Treated WADCN vs 0.5 ppm Target"},
        ))
        fig_gauge.update_layout(height=260, margin=dict(l=20, r=20, t=50, b=10))
        st.plotly_chart(fig_gauge, use_container_width=True)
        if wadcn <= WADCN_TARGET:
            st.success("Compliant with internal target (≤ 0.5 ppm).")
        else:
            st.error("Above internal target: operational action required.")

# Optional live scenario if sliders are changed
with st.expander("Optional: live savings if Warehouse sliders are adjusted"):
    live_df = pd.DataFrame({
        "Scenario": [
            "Live Warehouse cost from sliders",
            "RSM upper-bound cost",
            "RSM central cost",
            "Live lower savings, Jan–Nov",
            "Live upper savings, Jan–Nov",
            "Live annualized lower",
            "Live annualized upper",
        ],
        "Value": [
            money(warehouse["total_cost"]),
            money(RSM["total_cost_high"]),
            money(RSM["total_cost_central"]),
            money(live_savings_lower),
            money(live_savings_upper),
            money(live_annual_lower),
            money(live_annual_upper),
        ],
    })
    st.dataframe(live_df, use_container_width=True, hide_index=True)

# Charts
st.divider()
left, right = st.columns(2)
chart_df = pd.DataFrame({
    "Method": ["Warehouse", "Pump central", "RSM central"],
    "SMBS tons": [warehouse["smbs_tons"], pumps["smbs_tons"], RSM["smbs_tons_central"]],
    "CuSO₄ tons": [warehouse["cuso4_tons"], pumps["cuso4_tons"], RSM["cuso4_tons_central"]],
    "Total cost": [warehouse["total_cost"], pumps["total_cost"], RSM["total_cost_central"]],
})
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

# Final verdict
st.divider()
section_title("FINAL VERDICT", COLORS["navy"])
st.write(
    "The dashboard distinguishes between physical consumption records, pump-derived calculations, and model-based RSM predictions. "
    "Pump uncertainty is applied only to the pump-derived dataset, while WADCN analytical uncertainty is applied only to the RSM uncertainty evaluation. "
    "Warehouse data are treated as the physical consumption baseline. The optimized RSM dosing strategy reduces SMBS consumption while maintaining comparable CuSO₄ requirements and the WADCN compliance target. "
    "Even under conservative uncertainty treatment, the savings range remains positive, supporting the RSM strategy as a technically robust and economically meaningful decision-support tool."
)
