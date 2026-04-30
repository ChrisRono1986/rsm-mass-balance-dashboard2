import streamlit as st
import plotly.graph_objects as go

st.set_page_config(page_title="RSM Dashboard", layout="wide")

SLURRY_FLOW_M3H = 1950
WADCN_TARGET = 0.5

st.markdown("""
<style>
.stApp {
    background-color: #dff3ff;
}

/* MAIN CARD */
.infographic-card {
    border-radius: 16px;
    overflow: hidden;
    margin-bottom: 1.2rem;
    border: 3px solid rgba(0,0,0,0.25);
    box-shadow: 
        0 6px 18px rgba(0,0,0,0.18),
        0 0 0 2px rgba(255,255,255,0.6) inset;
    background: linear-gradient(
        180deg, 
        rgba(255,255,255,0.97), 
        rgba(245,250,255,0.94)
    );
}

/* COLOR BORDERS */
.section-warehouse { border-color:#0B6B2B; }
.section-pumps { border-color:#064A9B; }
.section-rsm { border-color:#5A168D; }

/* HEADERS */
.card-header {
    padding: 0.7rem;
    font-weight: 900;
    color: white;
    text-align: center;
}

.header-green { background: linear-gradient(135deg,#0B6B2B,#22A447); }
.header-blue { background: linear-gradient(135deg,#064A9B,#0A75D9); }
.header-purple { background: linear-gradient(135deg,#5A168D,#7B2CBF); }

.card-body { padding: 0.8rem; }

/* DOSE BOX */
.dose-box {
    border-radius: 8px;
    padding: 0.6rem;
    text-align: center;
    font-weight: 900;
    color: white;
}

/* ARROWS */
.flow-arrow {
    font-size: 24px;
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

def calc(smbs, cuso4):
    return smbs*SLURRY_FLOW_M3H/1000, cuso4*SLURRY_FLOW_M3H/1000

def dose_boxes(smbs, cuso4):
    c1,c2 = st.columns(2)
    with c1:
        st.markdown(f"<div class='dose-box' style='background:#0B6B2B;'>SMBS<br>{smbs} mg/L</div><div class='flow-arrow'>↘</div>", unsafe_allow_html=True)
    with c2:
        st.markdown(f"<div class='dose-box' style='background:#D55E00;'>CuSO₄<br>{cuso4} mg/L</div><div class='flow-arrow'>↙</div>", unsafe_allow_html=True)

def show_panel(title, subtitle, key):
    header = {"warehouse":"header-green","pumps":"header-blue","rsm":"header-purple"}[key]
    section = {"warehouse":"section-warehouse","pumps":"section-pumps","rsm":"section-rsm"}[key]
    icon = {"warehouse":"📦","pumps":"⚙️","rsm":"🧪"}[key]

    st.markdown(f"""
    <div class='infographic-card {section}'>
        <div class='card-header {header}'>
            {icon} {title}<br><small>{subtitle}</small>
        </div>
        <div class='card-body'>
    """, unsafe_allow_html=True)

    smbs = st.slider(f"SMBS {key}",0.0,150.0,50.0)
    cuso4 = st.slider(f"CuSO4 {key}",0.0,80.0,20.0)

    smbs_kgh, cuso4_kgh = calc(smbs, cuso4)

    dose_boxes(smbs,cuso4)

    st.write(f"SMBS kg/h: {smbs_kgh:.1f}")
    st.write(f"CuSO4 kg/h: {cuso4_kgh:.1f}")

    st.markdown("</div></div>", unsafe_allow_html=True)

st.title("RSM Mass Balance Dashboard")

c1,c2,c3 = st.columns(3)
with c1:
    show_panel("Warehouse (Actual Consumption)","Baseline","warehouse")
with c2:
    show_panel("Actual Dosing Pumps","Calculated","pumps")
with c3:
    show_panel("RSM Optimized","Model","rsm")

wadcn = st.slider("WADCN",0.0,2.0,0.4)

fig = go.Figure(go.Indicator(
    mode="gauge+number+delta",
    value=wadcn,
    delta={"reference":WADCN_TARGET},
    gauge={
        "axis":{"range":[0,2]},
        "steps":[
            {"range":[0,0.5],"color":"#20C997"},
            {"range":[0.5,1],"color":"#FFC107"},
            {"range":[1,2],"color":"#FF3B30"},
        ],
        "threshold":{"line":{"color":"red","width":4},"value":0.5}
    }
))

st.plotly_chart(fig)
