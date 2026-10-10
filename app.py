import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Public GitHub version: commercial prices and absolute cost values are not included.
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
PUMP_UNCERTAINTY = 0.10
WADCN_TARGET = 0.5

RSM = {
    "smbs_m3h_low": 2.916, "smbs_m3h_central": 2.932, "smbs_m3h_high": 2.950,
    "cuso4_m3h_low": 0.163, "cuso4_m3h_central": 0.165, "cuso4_m3h_high": 0.166,
    "smbs_m3_low": 23339.34498, "smbs_m3_central": 23468.79088, "smbs_m3_high": 23609.71207,
    "cuso4_m3_low": 1308.155157, "cuso4_m3_central": 1317.045773, "cuso4_m3_high": 1326.497179,
    "smbs_tons_low": 1200.30917, "smbs_tons_central": 1206.966388, "smbs_tons_high": 1214.213764,
    "cuso4_tons_low": 163.5193946, "cuso4_tons_central": 164.6307217, "cuso4_tons_high": 165.8121474,
}

COLORS = {
    "green": "#0B6B2B", "blue": "#064A9B", "purple": "#5A168D",
    "orange": "#D55E00", "navy": "#071B4D", "red": "#B00020", "amber": "#F5A623",
}

DEFAULTS = {
    "warehouse_smbs": 106.3, "warehouse_cuso4": 12.8,
    "pumps_smbs": 16.9, "pumps_cuso4": 43.0,
    "rsm_smbs": 89.4, "rsm_cuso4": 12.2,
}

# =========================
# CSS
# =========================
st.markdown(
    """
    <style>
    .stApp {
        background:
            linear-gradient(rgba(20,20,20,0.55), rgba(20,20,20,0.55)),
            url("Contourmap.png");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }

    .block-container {
        padding-top: 2.4rem;
        padding-bottom: 1rem;
        padding-left: 1.25rem;
        padding-right: 1.25rem;
        max-width: 98%;
        background: rgba(255,255,255,0.94);
        border: 1px solid rgba(212,175,55,0.45);
        border-radius: 24px;
        box-shadow: 0 8px 30px rgba(0,0,0,0.32), 0 0 24px rgba(212,175,55,0.12);
        margin-top: 1rem;
        margin-bottom: 1rem;
    }

    /* Mining-themed hero banner */
    .title-card {
        position:relative;overflow:hidden;border:3px solid #D4AF37;border-radius:24px;
        padding:1.25rem 1.6rem 1.35rem;margin-bottom:1.15rem;
        background:
            radial-gradient(circle at 15% 25%,rgba(212,175,55,.22),transparent 24%),
            radial-gradient(circle at 88% 75%,rgba(0,112,230,.28),transparent 30%),
            linear-gradient(135deg,#041434 0%,#071B4D 42%,#064A9B 100%);
        box-shadow:0 14px 32px rgba(0,0,0,.32),0 0 0 1px rgba(255,255,255,.15) inset,0 0 26px rgba(212,175,55,.22);
    }
    .title-card:before {
        content:"";position:absolute;left:-4%;right:-4%;bottom:-22px;height:90px;
        background:linear-gradient(165deg,transparent 0,transparent 22%,rgba(212,175,55,.10) 22.5%,rgba(212,175,55,.10) 30%,transparent 30.5%,transparent 44%,rgba(255,255,255,.06) 44.5%,rgba(255,255,255,.06) 52%,transparent 52.5%);
        pointer-events:none;
    }
    .title-card:after {content:"";position:absolute;top:-65%;left:-15%;width:45%;height:220%;background:linear-gradient(90deg,transparent,rgba(255,255,255,.08),transparent);transform:rotate(18deg);pointer-events:none;}
    .mining-process-strip {position:relative;z-index:2;display:flex;justify-content:center;align-items:center;flex-wrap:wrap;gap:.42rem;margin-bottom:.75rem;}
    .mining-step {display:inline-flex;justify-content:center;align-items:center;min-width:48px;height:43px;padding:0 .65rem;font-size:1.45rem;background:rgba(255,255,255,.12);border:1px solid rgba(255,255,255,.22);border-radius:12px;box-shadow:0 4px 10px rgba(0,0,0,.20);}
    .mining-flow-arrow {color:#F4CF57;font-size:1.35rem;font-weight:900;text-shadow:0 2px 4px rgba(0,0,0,.45);}
    .mining-kicker {position:relative;z-index:2;text-align:center;color:#F4CF57;font-size:.78rem;font-weight:900;letter-spacing:.20rem;text-transform:uppercase;margin-bottom:.35rem;}
    .title {position:relative;z-index:2;text-align:center;color:#fff;font-weight:900;font-size:clamp(1.55rem,2.3vw,2.45rem);line-height:1.12;margin:0;text-shadow:0 3px 7px rgba(0,0,0,.58),0 0 18px rgba(6,74,155,.55);}
    .title-accent {position:relative;z-index:2;width:min(460px,72%);height:4px;margin:.75rem auto .55rem;border-radius:999px;background:linear-gradient(90deg,transparent,#D4AF37 20%,#F7DF7B 50%,#D4AF37 80%,transparent);box-shadow:0 0 12px rgba(212,175,55,.45);}
    .subtitle {position:relative;z-index:2;text-align:center;color:#EAF3FF;font-size:.98rem;line-height:1.45;margin:.2rem 0 0;}
    .title-data-row {position:relative;z-index:2;display:flex;justify-content:center;align-items:stretch;flex-wrap:wrap;gap:.55rem;margin-top:.85rem;}
    .title-data-pill {color:#fff;background:rgba(255,255,255,.11);border:1px solid rgba(255,255,255,.22);border-radius:999px;padding:.36rem .75rem;font-size:.78rem;font-weight:750;box-shadow:0 3px 9px rgba(0,0,0,.16);}
    .title-data-pill b {color:#F7DF7B;}

    .header-box {color:white;padding:.6rem;border-radius:12px;text-align:center;font-size:1rem;font-weight:900;margin-bottom:.25rem;}
    .subheader-small {font-size:.82rem;font-style:italic;font-weight:600;opacity:.95;}
    .uncertainty-banner {border:1px solid #cfcfcf;border-radius:10px;padding:.65rem;margin:.45rem 0 .65rem;background:#fbfbfb;font-size:.86rem;line-height:1.25;}
    .section-label {padding:.32rem;border-radius:8px;text-align:center;font-weight:900;margin-top:.65rem;margin-bottom:.25rem;}
    .dose-box {color:white;border-radius:8px;padding:.6rem;text-align:center;font-weight:900;margin-bottom:.15rem;min-height:105px;}
    .flow-arrow-wrap {height:48px;margin-top:-4px;margin-bottom:4px;}
    .flow-arrow-svg {width:100%;height:48px;overflow:visible;}
    .flow-arrow-path-smbs,.flow-arrow-path-cuso4 {fill:none;stroke-width:5;stroke-linecap:round;stroke-dasharray:12 10;animation:flowDash 1.2s linear infinite;}
    .flow-arrow-path-smbs {stroke:#0B6B2B}.flow-arrow-path-cuso4 {stroke:#D55E00}.flow-arrow-head-smbs{fill:#0B6B2B}.flow-arrow-head-cuso4{fill:#D55E00}
    @keyframes flowDash {from{stroke-dashoffset:22}to{stroke-dashoffset:0}}
    .detox {border:2px solid #666;border-radius:18px;background:linear-gradient(#f5f6f7,#cdd2d6);padding:1rem;text-align:center;color:#111;font-weight:900;margin:.3rem 0;}
    .flow-box {border:1px solid #bbb;border-radius:8px;background:#fafafa;padding:.55rem;text-align:center;font-weight:800;}
    .compliance {border-radius:8px;background:linear-gradient(135deg,#00B050,#20C997);color:white;padding:.55rem;text-align:center;font-weight:900;box-shadow:0 2px 8px rgba(0,176,80,.30);}
    .note {border:1px dashed #999;border-radius:8px;padding:.55rem;background:#fbfbfb;font-size:.82rem;margin-top:.4rem;}
    .zone-optimal,.zone-warning,.zone-overdose {border-radius:9px;padding:.55rem;font-weight:700;margin-bottom:.35rem;color:#000!important;}
    .zone-optimal {background:#EAF5EA;border-left:7px solid #178A3B}.zone-warning{background:#FFF6E5;border-left:7px solid #F5A623}.zone-overdose{background:#FDEBEE;border-left:7px solid #B00020}
    div[data-testid="stMetricValue"] {font-size:1.15rem;}
    div[data-testid="stVerticalBlockBorderWrapper"]:has(.header-box) {border-width:9px!important;border-radius:22px!important;box-shadow:0 10px 28px rgba(0,0,0,.32),0 0 0 3px rgba(255,255,255,.85) inset!important;background:rgba(255,255,255,.96)!important;}
    div[data-testid="stVerticalBlockBorderWrapper"]:has(.header-box[style*="#0B6B2B"]){border-color:#008C3A!important}
    div[data-testid="stVerticalBlockBorderWrapper"]:has(.header-box[style*="#064A9B"]){border-color:#006FE6!important}
    div[data-testid="stVerticalBlockBorderWrapper"]:has(.header-box[style*="#5A168D"]){border-color:#8A2BE2!important}
    div[data-testid="stExpander"] {background:rgba(255,255,255,.96)!important;border-radius:10px!important;}
    div[data-testid="stExpander"] * {color:#000!important;}
    .stMarkdown,.stMarkdown p,.stCaptionContainer,label,div[data-testid="stMarkdownContainer"],div[data-testid="stWidgetLabel"],div[data-testid="stMetric"] {color:#000!important;}
    .header-box,.header-box *,.dose-box,.dose-box *,.compliance,.compliance *,.section-label[style*="color:white"] {color:#fff!important;}
    div[data-testid="stAlert"] * {color:inherit!important;}
    @media(max-width:900px){.title-card{padding:1rem .75rem 1.1rem;border-radius:18px}.mining-step{min-width:40px;height:38px;padding:0 .45rem;font-size:1.2rem}.mining-flow-arrow{font-size:1rem}.mining-kicker{font-size:.65rem;letter-spacing:.12rem}.subtitle{font-size:.86rem}}
    </style>
    """,
    unsafe_allow_html=True,
)

# =========================
# HELPERS
# =========================
def confidential_value():
    return "████████"


def calc_from_mgl(smbs_mgl, cuso4_mgl):
    smbs_kgh = smbs_mgl * SLURRY_FLOW_M3H / 1000
    cuso4_kgh = cuso4_mgl * SLURRY_FLOW_M3H / 1000
    smbs_m3h = smbs_kgh / SMBS_STRENGTH_KG_M3
    cuso4_m3h = cuso4_kgh / CUSO4_STRENGTH_KG_M3
    smbs_tons = smbs_kgh * EFFECTIVE_HOURS_JAN_NOV / 1000
    cuso4_tons = cuso4_kgh * EFFECTIVE_HOURS_JAN_NOV / 1000
    return {"smbs_mgl":smbs_mgl,"cuso4_mgl":cuso4_mgl,"smbs_kgh":smbs_kgh,"cuso4_kgh":cuso4_kgh,"smbs_m3h":smbs_m3h,"cuso4_m3h":cuso4_m3h,"smbs_tons":smbs_tons,"cuso4_tons":cuso4_tons,"total_tons":smbs_tons+cuso4_tons}


def section_title(text, bg, fg="white"):
    st.markdown(f"<div class='section-label' style='background:{bg};color:{fg};'>{text}</div>", unsafe_allow_html=True)


def panel_header(title, subtitle, color):
    st.markdown(f"<div class='header-box' style='background:{color};'>{title}<br><span class='subheader-small'>{subtitle}</span></div>", unsafe_allow_html=True)


def uncertainty_banner(note_type, color):
    if note_type == "pump":
        text = "<b>PUMP MEASUREMENT UNCERTAINTY: ±10%</b><br>All pump-derived values are reported as a range (min–max).<br>Ranges reflect the uncertainty of dosing pumps."
    elif note_type == "rsm":
        text = "<b>MODEL-BASED VALUES (WADCN UNCERTAINTY APPLIED)</b><br>WADCN expanded uncertainty: ±0.57 ppm.<br>Results shown as lower–central–upper estimates."
    else:
        return
    st.markdown(f"<div class='uncertainty-banner' style='border-left:7px solid {color};'>{text}</div>", unsafe_allow_html=True)


def arrow_svg(kind):
    color_class = "smbs" if kind == "smbs" else "cuso4"
    path = "M70 5 C95 25,125 38,155 50" if kind == "smbs" else "M150 5 C125 25,95 38,65 50"
    return f"""<div class='flow-arrow-wrap'><svg class='flow-arrow-svg' viewBox='0 0 220 60'><defs><marker id='arrowhead-{color_class}' markerWidth='10' markerHeight='10' refX='8' refY='3' orient='auto'><polygon points='0 0,8 3,0 6' class='flow-arrow-head-{color_class}'/></marker></defs><path class='flow-arrow-path-{color_class}' d='{path}' marker-end='url(#arrowhead-{color_class})'/></svg></div>"""


def dose_pills(smbs, cuso4, main_color, note_type, r):
    a, b = st.columns(2)
    if note_type == "pump":
        smbs_text = f"<b>SMBS Dosing</b><br>{smbs:.1f} ±10% mg/L<br>({smbs*.9:.1f} – {smbs*1.1:.1f} mg/L)<br>({r['smbs_kgh']*.9:.1f} – {r['smbs_kgh']*1.1:.1f} kg/h)"
        cu_text = f"<b>CuSO₄ Dosing</b><br>{cuso4:.1f} ±10% mg/L<br>({cuso4*.9:.1f} – {cuso4*1.1:.1f} mg/L)<br>({r['cuso4_kgh']*.9:.1f} – {r['cuso4_kgh']*1.1:.1f} kg/h)"
    elif note_type == "rsm":
        smbs_text = "<b>SMBS Dosing</b><br>2.916 – 2.932 – 2.950 m³/hr<br>(89.4 mg/L)<br>(174.3 kg/h)"
        cu_text = "<b>CuSO₄ Dosing</b><br>0.163 – 0.165 – 0.166 m³/hr<br>(12.2 mg/L)<br>(23.8 kg/h)"
    else:
        smbs_text = f"<b>SMBS Dosing</b><br>{smbs:.1f} mg/L<br>({r['smbs_kgh']:.1f} kg/h)"
        cu_text = f"<b>CuSO₄ Dosing</b><br>{cuso4:.1f} mg/L<br>({r['cuso4_kgh']:.1f} kg/h)"
    with a:
        st.markdown(f"<div class='dose-box' style='background:{main_color};'>{smbs_text}</div>{arrow_svg('smbs')}", unsafe_allow_html=True)
    with b:
        st.markdown(f"<div class='dose-box' style='background:{COLORS['orange']};'>{cu_text}</div>{arrow_svg('cuso4')}", unsafe_allow_html=True)


def process_visual():
    a,b,c=st.columns([1,1.5,1])
    with a: st.markdown("<div class='flow-box'>Slurry Inflow<br>1950 m³/h ➜</div>", unsafe_allow_html=True)
    with b: st.markdown("<div class='detox'>DETOX TANK<br>2880 m³</div>", unsafe_allow_html=True)
    with c: st.markdown("<div class='compliance'>Treated Slurry<br>WADCN ≤ 0.5 ppm ➜</div>", unsafe_allow_html=True)


def zone_label(value, low, high, unit):
    if value < low: cls,status="zone-warning","LOW / POSSIBLE UNDERDOSING"
    elif value > high: cls,status="zone-overdose","HIGH / CONSERVATIVE OR OVERDOSING"
    else: cls,status="zone-optimal","OPTIMAL / WITHIN TARGET REGION"
    st.markdown(f"<div class='{cls}'>{status}<br><span style='font-weight:500'>Value: {value:.1f} {unit} | Target: {low:.1f}–{high:.1f}</span></div>", unsafe_allow_html=True)


def tables(r, color, note_type):
    section_title("DOSING SUMMARY", "#F2F2F2", color)
    dosing=pd.DataFrame({"Parameter":["Slurry flow","Effective hours","SMBS dosing","SMBS mass flow","CuSO₄ dosing","CuSO₄ mass flow"],"Value":[f"{SLURRY_FLOW_M3H:,.0f} m³/h",f"{EFFECTIVE_HOURS_JAN_NOV:,.1f} h",f"{r['smbs_mgl']:.1f} mg/L",f"{r['smbs_kgh']:.1f} kg/h",f"{r['cuso4_mgl']:.1f} mg/L",f"{r['cuso4_kgh']:.1f} kg/h"]})
    st.dataframe(dosing,use_container_width=True,hide_index=True)
    section_title("TOTAL REAGENT CONSUMPTION (JAN–NOV 2025)",color)
    cons=pd.DataFrame({"Reagent":["SMBS","CuSO₄","TOTAL"],"Consumption (tons)":[round(r['smbs_tons'],1),round(r['cuso4_tons'],1),round(r['total_tons'],1)],"Mass flow (kg/h avg.)":[round(r['smbs_kgh'],1),round(r['cuso4_kgh'],1),round(r['smbs_kgh']+r['cuso4_kgh'],1)]})
    st.dataframe(cons,use_container_width=True,hide_index=True)
    section_title("COST SUMMARY","#F2F2F2",color)
    st.dataframe(pd.DataFrame({"Item":["SMBS cost","CuSO₄ cost","TOTAL COST"],"Value":[confidential_value(),confidential_value(),"CONFIDENTIAL"]}),use_container_width=True,hide_index=True)
    notes={"warehouse":"Warehouse data represent physically consumed reagents and are treated as the reference baseline. Pump uncertainty is not applied.","pump":"Pump-derived values include ±10% pump uncertainty. These ranges do not reconcile with warehouse consumption.","rsm":"RSM values incorporate WADCN uncertainty separately. Pump measurement uncertainty is not included in this method."}
    st.markdown(f"<div class='note'>{notes[note_type]}</div>",unsafe_allow_html=True)


def show_panel(title,subtitle,color,default_smbs,default_cuso4,key,note_type):
    with st.container(border=True):
        panel_header(title,subtitle,color); uncertainty_banner(note_type,color)
        smbs=st.slider("SMBS dosing (mg/L)",0.0,150.0,float(default_smbs),0.1,key=f"{key}_smbs")
        cuso4=st.slider("CuSO₄ dosing (mg/L)",0.0,80.0,float(default_cuso4),0.1,key=f"{key}_cuso4")
        r=calc_from_mgl(smbs,cuso4); dose_pills(smbs,cuso4,color,note_type,r); process_visual()
        st.markdown("**Operational zone vs RSM target region**")
        zone_label(smbs,83.7,95.1,"mg/L SMBS"); zone_label(cuso4,11.4,13.0,"mg/L CuSO₄")
        tables(r,color,note_type)
        return r

# =========================
# APP
# =========================
truck_col, title_col = st.columns([1.15, 4.85], gap="medium")

with truck_col:
    st.markdown("<div style='height:0.35rem'></div>", unsafe_allow_html=True)
    st.image("Haul truck.png", use_container_width=True)

with title_col:
    st.markdown(f"""
    <div class="title-card">
      <div class="mining-process-strip">
        <div class="mining-step" title="Mining">⛏️</div><div class="mining-flow-arrow">➜</div>
        <div class="mining-step" title="Ore haulage">🚛</div><div class="mining-flow-arrow">➜</div>
        <div class="mining-step" title="Crushing and grinding">⚙️</div><div class="mining-flow-arrow">➜</div>
        <div class="mining-step" title="Metallurgical processing">🏭</div><div class="mining-flow-arrow">➜</div>
        <div class="mining-step" title="Laboratory optimization">⚗️</div><div class="mining-flow-arrow">➜</div>
        <div class="mining-step" title="Detoxification">💧</div>
      </div>
      <div class="mining-kicker">Mining • Metallurgy • Detoxification • Optimization</div>
      <div class="title">MASS BALANCE TRANSLATION:<br>FROM LABORATORY OPTIMIZATION TO PLANT OPERATION</div>
      <div class="title-accent"></div>
      <div class="subtitle">Validation of reagent efficiency based on real plant data</div>
      <div class="title-data-row">
        <div class="title-data-pill">🕒 Effective operating hours: <b>{EFFECTIVE_HOURS_JAN_NOV:,.1f} h</b></div>
        <div class="title-data-pill">🌊 Slurry flow: <b>{SLURRY_FLOW_M3H:,.0f} m³/h</b></div>
        <div class="title-data-pill">🎯 Internal WADCN target: <b>≤ {WADCN_TARGET:.1f} ppm</b></div>
      </div>
    </div>""",unsafe_allow_html=True)

with st.expander("Constants and uncertainty rules used in this dashboard"):
    constants=pd.DataFrame({"Parameter":["Slurry flow rate","Annual mill uptime 2025","Effective operating hours Jan–Nov","Annualization factor","SMBS stock solution strength","CuSO₄ stock solution strength","SMBS price","CuSO₄ price","Pump uncertainty","WADCN DETOXFEED expanded uncertainty","Internal WADCN target"],"Value":[f"{SLURRY_FLOW_M3H:,.0f} m³/h",f"{ANNUAL_UPTIME_H:,.2f} h",f"{EFFECTIVE_HOURS_JAN_NOV:,.1f} h",f"{ANNUALIZATION_FACTOR:.4f}",f"{SMBS_STRENGTH_KG_M3:.2f} kg/m³",f"{CUSO4_STRENGTH_KG_M3:.2f} kg/m³","CONFIDENTIAL","CONFIDENTIAL","±10% applied only to actual dosing pumps","±0.57 ppm applied only to RSM WADCN-feed recalculation",f"WADCN ≤ {WADCN_TARGET} ppm"]})
    st.dataframe(constants,use_container_width=True,hide_index=True)

col1,col2,col3=st.columns(3)
with col1:
    warehouse=show_panel("1. WAREHOUSE (ACTUAL CONSUMPTION)","Reference: physically consumed reagents",COLORS['green'],DEFAULTS['warehouse_smbs'],DEFAULTS['warehouse_cuso4'],"warehouse","warehouse")
with col2:
    pumps=show_panel("2. ACTUAL DOSING PUMPS (CALCULATED)","Based on pump flow integration and solution concentration",COLORS['blue'],DEFAULTS['pumps_smbs'],DEFAULTS['pumps_cuso4'],"pumps","pump")
    section_title("PUMP ±10% UNCERTAINTY","#EAF2FF",COLORS['blue'])
    pump_unc=pd.DataFrame({"Parameter":["SMBS dosing","CuSO₄ dosing","SMBS kg/h","CuSO₄ kg/h"],"Lower":[f"{pumps['smbs_mgl']*.9:.1f} mg/L",f"{pumps['cuso4_mgl']*.9:.1f} mg/L",f"{pumps['smbs_kgh']*.9:.1f} kg/h",f"{pumps['cuso4_kgh']*.9:.1f} kg/h"],"Central":[f"{pumps['smbs_mgl']:.1f} mg/L",f"{pumps['cuso4_mgl']:.1f} mg/L",f"{pumps['smbs_kgh']:.1f} kg/h",f"{pumps['cuso4_kgh']:.1f} kg/h"],"Upper":[f"{pumps['smbs_mgl']*1.1:.1f} mg/L",f"{pumps['cuso4_mgl']*1.1:.1f} mg/L",f"{pumps['smbs_kgh']*1.1:.1f} kg/h",f"{pumps['cuso4_kgh']*1.1:.1f} kg/h"]})
    st.dataframe(pump_unc,use_container_width=True,hide_index=True)
with col3:
    rsm=show_panel("3. ALTERNATIVE METHOD (RSM OPTIMIZED)","Model-based optimized dosing strategy",COLORS['purple'],DEFAULTS['rsm_smbs'],DEFAULTS['rsm_cuso4'],"rsm","rsm")

st.divider(); section_title("FORMAL RSM UNCERTAINTY RESULTS: WADCN ±0.57 ppm APPLIED TO 8003 DATA POINTS",COLORS['purple'])
rsm_unc=pd.DataFrame({"Result":["Average dosing (m³/h)","Total consumption (m³)","Total consumption (tons)"],"SMBS lower":[RSM['smbs_m3h_low'],RSM['smbs_m3_low'],RSM['smbs_tons_low']],"SMBS central":[RSM['smbs_m3h_central'],RSM['smbs_m3_central'],RSM['smbs_tons_central']],"SMBS upper":[RSM['smbs_m3h_high'],RSM['smbs_m3_high'],RSM['smbs_tons_high']],"CuSO₄ lower":[RSM['cuso4_m3h_low'],RSM['cuso4_m3_low'],RSM['cuso4_tons_low']],"CuSO₄ central":[RSM['cuso4_m3h_central'],RSM['cuso4_m3_central'],RSM['cuso4_tons_central']],"CuSO₄ upper":[RSM['cuso4_m3h_high'],RSM['cuso4_m3_high'],RSM['cuso4_tons_high']]})
st.dataframe(rsm_unc,use_container_width=True,hide_index=True)

st.divider(); section_title("COMPARISON: RSM OPTIMIZED vs WAREHOUSE (ACTUAL)",COLORS['green'])
comparison=pd.DataFrame({"Reagent":["SMBS","CuSO₄","TOTAL"],"Warehouse (tons)":[warehouse['smbs_tons'],warehouse['cuso4_tons'],warehouse['total_tons']],"RSM central (tons)":[RSM['smbs_tons_central'],RSM['cuso4_tons_central'],RSM['smbs_tons_central']+RSM['cuso4_tons_central']]})
comparison['Savings (tons)']=comparison['Warehouse (tons)']-comparison['RSM central (tons)']
comparison['Reduction (%)']=comparison['Savings (tons)']/comparison['Warehouse (tons)']*100
st.dataframe(comparison,use_container_width=True,hide_index=True)

smbs_reduction_pct=(warehouse['smbs_tons']-RSM['smbs_tons_central'])/warehouse['smbs_tons']*100
cuso4_reduction_pct=(warehouse['cuso4_tons']-RSM['cuso4_tons_central'])/warehouse['cuso4_tons']*100
total_reduction_pct=(warehouse['total_tons']-(RSM['smbs_tons_central']+RSM['cuso4_tons_central']))/warehouse['total_tons']*100

c1,c2,c3=st.columns([1.1,1.1,1.4])
with c1:
    with st.container(border=True):
        section_title("REAGENT REDUCTION (%)","#EAF5EA",COLORS['green']); st.metric("SMBS Reduction",f"{smbs_reduction_pct:.1f}%"); st.metric("CuSO₄ Reduction",f"{cuso4_reduction_pct:.1f}%")
with c2:
    with st.container(border=True):
        section_title("TOTAL REAGENT REDUCTION","#EAF2FF",COLORS['blue']); st.metric("Overall Reduction",f"{total_reduction_pct:.1f}%"); st.metric("Cost Data","CONFIDENTIAL"); st.caption("Public version: absolute prices and currency savings are intentionally hidden.")
with c3:
    with st.container(border=True):
        section_title("WADCN COMPLIANCE VISUAL","#F3EAFB",COLORS['purple'])
        wadcn=st.slider("Illustrative treated WADCN result (ppm)",0.0,2.0,0.45,0.01)
        fig_gauge=go.Figure(go.Indicator(mode="gauge+number+delta",value=wadcn,delta={"reference":WADCN_TARGET,"increasing":{"color":COLORS['red']},"decreasing":{"color":COLORS['green']}},gauge={"axis":{"range":[0,2.0]},"bar":{"color":COLORS['purple']},"steps":[{"range":[0,WADCN_TARGET],"color":"#20C997"},{"range":[WADCN_TARGET,1.0],"color":"#FFC107"},{"range":[1.0,2.0],"color":"#FF3B30"}],"threshold":{"line":{"color":"#8B0000","width":6},"thickness":.9,"value":WADCN_TARGET}},title={"text":"<b>Treated WADCN vs 0.5 ppm Target</b>"},number={"font":{"size":42,"color":"#071B4D"}}))
        fig_gauge.update_layout(height=285,margin=dict(l=20,r=20,t=60,b=10),paper_bgcolor="rgba(255,255,255,0)",plot_bgcolor="rgba(255,255,255,0)",font=dict(color="#071B4D",size=14))
        st.plotly_chart(fig_gauge,use_container_width=True)

with st.expander("Live Reduction Percentages"):
    live_df=pd.DataFrame({"Metric":["SMBS Reduction","CuSO₄ Reduction","Cost Data"],"Value":[f"{smbs_reduction_pct:.1f}%",f"{cuso4_reduction_pct:.1f}%","CONFIDENTIAL"]})
    st.dataframe(live_df,use_container_width=True,hide_index=True)

st.divider(); left,right=st.columns(2)
chart_df=pd.DataFrame({"Method":["Warehouse","Pump central","RSM central"],"SMBS tons":[warehouse['smbs_tons'],pumps['smbs_tons'],RSM['smbs_tons_central']],"CuSO₄ tons":[warehouse['cuso4_tons'],pumps['cuso4_tons'],RSM['cuso4_tons_central']]})
with left:
    fig=go.Figure(); fig.add_bar(x=chart_df['Method'],y=chart_df['SMBS tons'],name='SMBS'); fig.add_bar(x=chart_df['Method'],y=chart_df['CuSO₄ tons'],name='CuSO₄'); fig.update_layout(title='Total Reagent Consumption',barmode='group',yaxis_title='tons',height=380); st.plotly_chart(fig,use_container_width=True)
with right:
    fig2=go.Figure(); fig2.add_bar(x=['SMBS','CuSO₄','Overall'],y=[smbs_reduction_pct,cuso4_reduction_pct,total_reduction_pct],text=[f"{smbs_reduction_pct:.1f}%",f"{cuso4_reduction_pct:.1f}%",f"{total_reduction_pct:.1f}%"],textposition='outside',marker_color=[COLORS['green'],COLORS['orange'],COLORS['blue']],name='Reduction'); fig2.update_layout(title='Reagent Reduction Relative to Warehouse Baseline',yaxis_title='Reduction (%)',height=380,showlegend=False); st.plotly_chart(fig2,use_container_width=True)

st.divider(); section_title("FINAL VERDICT",COLORS['navy'])
st.write("The dashboard distinguishes between physical consumption records, pump-derived calculations, and model-based RSM predictions. Pump uncertainty is applied only to the pump-derived dataset, while WADCN analytical uncertainty is applied only to the RSM uncertainty evaluation. Warehouse data are treated as the physical consumption baseline. The optimized RSM dosing strategy reduces SMBS consumption while maintaining comparable CuSO₄ requirements and the WADCN compliance target. The public dashboard reports percentage reductions while withholding commercial pricing and absolute savings. This preserves the technical comparison without disclosing confidential financial information.")
