import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import base64

# Core Functions (inline - no imports needed)
def add_noise(value, noise_level=0.005):
    return value + np.random.normal(0, noise_level)

def apply_tolerance(nominal_value, tolerance=0.05):
    return nominal_value * np.random.normal(1, tolerance/3)

def calculate_loading(v_in, r_top, r_bottom, r_load):
    r_eff = (r_bottom * r_load) / (r_bottom + r_load) if r_load > 0 else r_bottom
    return v_in * (r_eff / (r_top + r_eff))

# PDF HTML Generator (no fpdf needed)
def generate_report_html(student_info, results, quiz_scores):
    html = f"""
    <html>
    <head><title>EEE Lab Report</title>
    <style>body{{font-family:Arial;margin:40px;background:#f0f8ff}} 
    h1{{color:#1e3a8a;text-align:center}} 
    table{{width:100%;border-collapse:collapse;margin:20px 0}}
    th,td{{border:1px solid #ddd;padding:12px;text-align:left}}
    th{{background:#3b82f6;color:white}}</style></head>
    <body>
    <h1>⚡ EEE Virtual Lab Report</h1>
    <h2>Student Details</h2>
    <p><strong>Name:</strong> {student_info.get('Name', 'N/A')}</p>
    <p><strong>Reg No:</strong> {student_info.get('Reg No', 'N/A')}</p>
    <p><strong>Semester:</strong> {student_info.get('Semester', 'N/A')}</p>
    
    <h2>Experiment Results</h2>
    <table>
    <tr><th>Experiment</th><th>Result</th></tr>
    """
    for exp, result in results.items():
        html += f"<tr><td>{exp}</td><td>{result}</td></tr>"
    
    html += """
    </table>
    <h2>Quiz Performance</h2>
    <table>
    <tr><th>Experiment</th><th>Score</th></tr>
    """
    for exp, score in quiz_scores.items():
        html += f"<tr><td>{exp}</td><td>{score}/1</td></tr>"
    html += "</table></body></html>"
    return html

st.set_page_config(page_title="EEE Virtual Lab", layout="wide", page_icon="⚡")

# Session State
if 'student_info' not in st.session_state:
    st.session_state.student_info = {}
    st.session_state.results = {}
    st.session_state.quiz_scores = {}
    st.session_state.r_pot = apply_tolerance(10000)

# SIDEBAR - Student + Navigation
st.sidebar.title("👤 Student Portal")
if st.sidebar.button("✏️ Enter Details"):
    with st.sidebar:
        st.session_state.student_info = {
            "Name": st.text_input("Full Name", key="name"),
            "Reg No": st.text_input("Register No", key="reg"),
            "Semester": st.selectbox("Semester", ["V", "VI", "VII"], key="sem"),
            "Roll No": st.text_input("Roll No", key="roll")
        }

experiments = ["🏠 Home", "1. Potentiometer", "2. Strain Gauge", "3. RTD Temp", "🏆 Final Quiz"]
page = st.sidebar.selectbox("Select Experiment:", experiments)

# HOMEPAGE
if page == "🏠 Home":
    st.title("⚡ EEE Virtual Sensors & Instruments Lab")
    
    col1, col2, col3 = st.columns(3)
    completed = sum(1 for v in st.session_state.quiz_scores.values() if v == 1)
    with col1: st.metric("Experiments", 3, delta=completed)
    with col2: st.metric("Quizzes Passed", completed)
    with col3: st.metric("Status", "Ready!" if st.session_state.student_info else "Enter Details")
    
    if st.session_state.student_info:
        st.subheader("✅ Your Profile")
        for k,v in st.session_state.student_info.items():
            st.write(f"**{k}:** {v}")
        
        # MASTER DOWNLOAD
        if st.button("📥 Download Complete Report (PDF)", type="primary"):
            html_content = generate_report_html(st.session_state.student_info, 
                                              st.session_state.results, 
                                              st.session_state.quiz_scores)
            b64 = base64.b64encode(html_content.encode()).decode()
            href = f'<a href="data:text/html;base64,{b64}" download="EEE_Lab_Report_{st.session_state.student_info.get("Reg No","STUDENT")}.html">Download Report</a>'
            st.markdown(href, unsafe_allow_html=True)
            st.info("💡 HTML opens in browser + printable as PDF")

# EXPERIMENT 1: Potentiometer + Quiz
elif page == "1. Potentiometer":
    st.header("🔌 1. Potentiometer Loading Effect")
    col1, col2 = st.columns([1,2])
    
    with col1:
        st.subheader("Simulation")
        pos = st.slider("Potentiometer %", 0, 100, 50)/100
        load_options = {"No Load": 1e12, "Light 100kΩ": 1e5, "10kΩ": 1e4, "Heavy 1kΩ": 1e3}
        load_key = st.selectbox("Load Condition:", list(load_options.keys()))
        r_load = load_options[load_key]
        
        v_in = 10.0
        r_top = st.session_state.r_pot * (1-pos)
        r_bottom = st.session_state.r_pot * pos
        v_ideal = v_in * pos
        v_real = calculate_loading(v_in, r_top, r_bottom, r_load)
        v_meas = add_noise(v_real)
        
        st.metric("Measured Voltage", f"{v_meas:.3f} V", delta_color="inverse")
        st.caption(f"Ideal: {v_ideal:.3f}V | Error: {abs(v_ideal-v_meas):.3f}V")
        
        if st.button("💾 Save This Result"):
            st.session_state.results["Potentiometer"] = f"{v_meas:.3f}V @ {pos*100:.0f}% (Error: {abs(v_ideal-v_meas):.3f}V)"
            st.success("Saved!")
    
    with col2:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=[0,1], y=[0, v_ideal], name="Ideal (No Load)", line=dict(color="green")))
        fig.add_trace(go.Scatter(x=[0,1], y=[0, v_meas], name="Measured (w/ Load)", line=dict(color="red")))
        fig.update_layout(title="Loading Effect Visualization", xaxis_title="Normalized", yaxis_title="Volts")
        st.plotly_chart(fig, use_container_width=True)
    
    # QUIZ SECTION
    st.subheader("📝 Understanding Check (1 Question)")
    col_q1, col_q2, col_q3 = st.columns(3)
    with col_q1:
        q1_ans = st.radio("Loading effect causes Vout to be:",
                         ["Higher than ideal", "Same as ideal", "Lower than ideal"], index=2, key="q1")
    if st.button("✅ Submit Quiz & Score"):
        score = 1 if q1_ans == "Lower than ideal" else 0
        st.session_state.quiz_scores["Potentiometer"] = score
        st.balloons()
        st.success(f"🎉 Correct! {score}/1" if score else "Try again!")

# SIMPLIFIED OTHER EXPERIMENTS
elif page == "2. Strain Gauge":
    st.header("🛠️ 2. Strain Gauge Bridge")
    weight = st.slider("Applied Weight (kg)", 0.0, 10.0, 2.0)
    strain_voltage = add_noise(weight * 0.5 * 0.001)  # mV simulation
    st.metric("Bridge Output", f"{strain_voltage*1000:.2f} mV")
    
    if st.button("Save Result"):
        st.session_state.results["Strain Gauge"] = f"{weight}kg → {strain_voltage*1000:.1f}mV"
    
    st.radio("Strain gauges change:", ["Voltage directly", "Resistance", "Capacitance"], key="q2")
    if st.button("Quiz"):
        st.session_state.quiz_scores["Strain Gauge"] = 1

elif page == "3. RTD Temp":
    st.header("🌡️ 3. RTD Temperature")
    temp = st.slider("Set Temperature °C", -20, 150, 25)
    r_rtd = 100 * (1 + 0.00385 * temp) + add_noise(0, 0.1)
    st.metric("RTD Resistance", f"{r_rtd:.2f} Ω")
    
    if st.button("Save"):
        st.session_state.results["RTD"] = f"{temp}°C → {r_rtd:.1f}Ω"

elif page == "🏆 Final Quiz":
    st.header("🎖️ Final Assessment (Complete Lab)")
    st.info("Answer to pass lab!")
    final_q = st.radio("Primary cause of measurement error in lab?", 
                       ["Perfect components", "Noise + Tolerances", "Ideal calculations"])
    if st.button("Complete Lab"):
        final_score = 1 if final_q == "Noise + Tolerances" else 0
        st.balloons()
        st.success(f"Lab Complete! Final Score: {final_score}/1")

st.markdown("---")
st.caption(f"👤 {st.session_state.student_info.get('Name', 'Guest')} | EEE Virtual Lab | Quizzes & Reports Ready")
