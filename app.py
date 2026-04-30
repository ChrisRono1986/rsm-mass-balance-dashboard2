import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="RSM Dashboard", layout="wide")

SLURRY_FLOW_M3H = 1950
WADCN_TARGET = 0.5

st.markdown("""
<style>
.stApp {
    background-color: #dff3ff;
}
.infographic-card {
    border-radius: 16px;
    margin-bottom: 1rem;
    background: linear-gradient(180deg, rgba(255,255,255,0.98), rgba(245,250,255,0.94));
    box-shadow: 0 6px 18px rgba(0,0,0,0.13);
    border: 2px solid #ddd;
}
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
.dose-box {
    border-radius: 8px;
    padding: 0.6rem;
    text-align: center;
    font-weight: 900;
    color: white;
}
.flow-arrow {
    font-size: 24px;
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

def calc_from_mgl(smbs, cuso4):
    smbs_kgh = smbs * SLURRY_FLOW_M3H / 1000
    cuso4_kgh = cuso4 * SLURRY_FLOW_M3H / 1000
    return smbs_kgh, cuso4_kgh

def dose_pills(smbs, cuso4):
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"<div class='dose-box' style='background:#0B6B2B;'>SMBS<br>{smbs} mg/L</div><div class='flow-arrow'>↘</div>", unsafe_allow_html=True)
    with c2:
        st.markdown(f"<div class='dose-box' style='background:#D55E00;'>CuSO₄<br>{cuso4} mg/L</div><div class='flow-arrow'>↙</div>", unsafe_allow_html=True)

def process_visual():
    a,b,c = st.columns([1,1.5,1])
    with a:
        st.write("Slurry ➜")
    with b:
        st.write("DETOX TANK")
    with c:
        st.write("➜ Treated ≤0.5 ppm")

def show_panel(title, subtitle, key):
    header = {"warehouse":"header-green","pumps":"header-blue","rsm":"header-purple"}[key]
    icon = {"warehouse":"📦","pumps":"⚙️","rsm":"🧪"}[key]

    st.markdown(f"""
    <div class='infographic-card'>
        <div class='card-header {header}'>
            {icon} {title}<br><small>{subtitle}</small>
        </div>
        <div class='card-body'>
    """, unsafe_allow_html=True)

    smbs = st.slider(f"SMBS {key}",0.0,150.0,50.0)
    cuso4 = st.slider(f"CuSO4 {key}",0.0,80.0,20.0)

    smbs_kgh, cuso4_kgh = calc_from_mgl(smbs, cuso4)

    dose_pills(smbs, cuso4)
    process_visual()

    st.write(f"SMBS kg/h: {smbs_kgh:.1f}")
    st.write(f"CuSO4 kg/h: {cuso4_kgh:.1f}")

    st.markdown("</div></div>", unsafe_allow_html=True)

st.title("RSM Mass Balance Dashboard")

c1,c2,c3 = st.columns(3)
with c1:
    show_panel("Warehouse","Actual consumption","warehouse")
with c2:
    show_panel("Pumps","Calculated","pumps")
with c3:
    show_panel("RSM","Optimized","rsm")

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
