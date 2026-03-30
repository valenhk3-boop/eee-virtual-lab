import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# ENGINEERING FUNCTIONS
def add_noise(value, noise_level=0.005):
    return value + np.random.normal(0, noise_level)

def calculate_loading(v_in, r_top, r_bottom, r_load):
    # Parallel resistance formula: (R1 * R2) / (R1 + R2)
    r_eff = (r_bottom * r_load) / (r_bottom + r_load) if r_load > 0 else r_bottom
    return v_in * (r_eff / (r_top + r_eff))

def potentiometer_tabulation(positions, v_in=10, r_pot=10000):
    data = []
    for pos_pct in positions:
        pos = pos_pct / 100
        r_top = r_pot * (1 - pos)
        r_bottom = r_pot * pos
        
        # Multiple loads: Open Circuit, 100k, 10k, 1k
        loads = [1e12, 1e5, 1e4, 1e3]  
        row = {"Position (%)": pos_pct}
        for i, r_load in enumerate(loads):
            v_ideal = v_in * pos
            v_meas = add_noise(calculate_loading(v_in, r_top, r_bottom, r_load))
            # Handle division by zero for 0% position
            error = abs((v_ideal - v_meas) / v_ideal * 100) if v_ideal != 0 else 0
            row[f"R_L{i+1} (V)"] = f"{v_meas:.3f}"
            row[f"Error{i+1} (%)"] = f"{error:.2f}"
        data.append(row)
    return pd.DataFrame(data)

st.set_page_config(page_title="EEE Sensors Virtual Lab", layout="wide")

# CRITICAL FIX: Initialize all session state keys
if 'observations' not in st.session_state:
    st.session_state.observations = {}
    st.session_state.student_info = {}
    st.session_state.tabulations = {}
    st.session_state.quiz_scores = {}  # Fixed the missing key

st.markdown("""
<div style='text-align:center; padding:20px; background:#1e40af; color:white; font-family:Georgia'>
<h1 style='margin:0'>ELECTRICAL & ELECTRONICS ENGINEERING DEPARTMENT</h1>
<h2 style='margin:0'>Sensors & Instrumentation Virtual Laboratory</h2>
<p style='margin:5px 0 0'>Academic Year 2025-26</p>
</div>
""", unsafe_allow_html=True)

# SIDEBAR
st.sidebar.header("🔬 Lab Control Panel")
st.sidebar.markdown("### Student Details")
name = st.sidebar.text_input("**Name**")
reg_no = st.sidebar.text_input("**Reg. No**")
if st.sidebar.button("**Register**"):
    st.session_state.student_info = {"Name": name, "Reg No": reg_no, "Date": datetime.now().strftime("%d/%m/%Y")}

experiments = ["📊 Dashboard", "1️⃣ Potentiometer Loading Effect", "2️⃣ Strain Gauge Bridge", "3️⃣ RTD Calibration"]
page = st.sidebar.selectbox("**Experiment**", experiments)

# DASHBOARD PAGE
if page == "📊 Dashboard":
    st.markdown("<h2 style='color:#1e293b'>LABORATORY PROGRESS MONITOR</h2>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    # Calculate experiments completed
    exp_done = len([k for k in st.session_state.quiz_scores.keys() if k != 'Final'])
    
    # Calculate Average Viva Score safely
    scores = list(st.session_state.quiz_scores.values())
    avg_viva = (sum(scores) / (len(scores) * 3)) * 100 if scores else 0

    with col1: st.metric("**Experiments Recorded**", exp_done, "of 3")
    with col2: st.metric("**Viva Average**", f"{avg_viva:.0f}%")
    with col3: st.metric("**Status**", "COMPLETE" if exp_done >= 1 else "IN PROGRESS")
    
    if st.session_state.student_info:
        st.info(f"**Student:** {st.session_state.student_info.get('Name')} | **Reg:** {st.session_state.student_info.get('Reg No')}")
    else:
        st.warning("Please register your details in the sidebar.")

# EXPERIMENT 1
elif page == "1️⃣ Potentiometer Loading Effect":
    st.markdown("<h2 style='color:#1e293b; border-bottom:3px solid #3b82f6; padding-bottom:10px'>EXPERIMENT 1: STUDY OF LOADING EFFECT IN POTENTIOMETER</h2>", unsafe_allow_html=True)
    
    st.markdown("### 🔌 **CIRCUIT DIAGRAM**")
    st.image("https://via.placeholder.com/600x200/4f46e5/ffffff?text=Potentiometer+Circuit+Diagram", caption="Circuit: Vin=10V, Rpot=10k, RL=Variable")
    
    c1, c2 = st.columns([1,1])
    with c1:
        with st.expander("**AIM**", expanded=True):
            st.markdown("To study the loading effect of a potentiometer by measuring output voltage for different wiper positions and load conditions.")
        
        with st.expander("**THEORY**"):
            # Fixed LaTeX syntax
            st.latex(r"V_{out(ideal)} = V_{in} \cdot \frac{R_{bottom}}{R_{total}}")
            st.latex(r"R_{eff} = \frac{R_{bottom} \cdot R_L}{R_{bottom} + R_L}")
            st.latex(r"Error \% = \frac{|V_{ideal} - V_{meas}|}{V_{ideal}} \times 100")
    
    with c2:
        with st.expander("**APPARATUS**"):
            st.markdown("- Linear Potentiometer (10kΩ)\n- DC Power Supply (10V)\n- Digital Multimeter\n- Decade Resistance Box (Loads)")
    
    st.markdown("### **OBSERVATION TABLE**")
    positions = st.multiselect("**Select Positions (%)**", [0,10,20,30,40,50,60,70,80,90,100], default=[0,20,50,80,100])
    
    if st.button("**GENERATE READINGS**", type="primary"):
        df = potentiometer_tabulation(positions)
        st.session_state.tabulations['Potentiometer'] = df
        st.dataframe(df, use_container_width=True)
        
        # Plotting
        fig = go.Figure()
        load_labels = { 'Error1': 'Open Circuit', 'Error2': '100kΩ Load', 'Error3': '10kΩ Load', 'Error4': '1kΩ Load' }
        for key, label in load_labels.items():
            fig.add_trace(go.Scatter(x=df['Position (%)'], y=df[f"{key} (%)"].astype(float), name=label, mode='lines+markers'))
        
        fig.update_layout(title="Loading Error vs. Position", xaxis_title="Position (%)", yaxis_title="Error (%)")
        st.plotly_chart(fig, use_container_width=True)

    # Viva Section
    st.markdown("### **VIVA VOCE**")
    q1 = st.radio("Q1: Which load causes the highest error?", ["100kΩ", "10kΩ", "1kΩ"], key="v1")
    q2 = st.radio("Q2: Ideally, a voltmeter should have:", ["Zero Resistance", "Infinite Resistance", "1kΩ Resistance"], key="v2")
    
    if st.button("Submit Viva"):
        score = 0
        if q1 == "1kΩ": score += 1.5
        if q2 == "Infinite Resistance": score += 1.5
        st.session_state.quiz_scores['Potentiometer'] = score
        st.success(f"Score Saved: {score}/3")

# Placeholders for other experiments
elif page == "2️⃣ Strain Gauge Bridge":
    st.header("Experiment 2: Strain Gauge Bridge")
    st.info("Module under construction: Logic similar to Exp 1.")

elif page == "3️⃣ RTD Calibration":
    st.header("Experiment 3: RTD Calibration")
    st.info("Module under construction: Logic similar to Exp 1.")

st.markdown("---")
st.caption("© 2026 EEE Virtual Lab | Professional Engineering Education")
