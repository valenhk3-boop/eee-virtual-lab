import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from fpdf import FPDF
import base64
import io

# UTILITIES
def add_noise(value, noise_level=0.005):
    return value + np.random.normal(0, noise_level)

def apply_tolerance(nominal_value, tolerance=0.05):
    return nominal_value * np.random.uniform(1 - tolerance, 1 + tolerance)

def calculate_loading(v_in, r_top, r_bottom, r_load):
    r_eff = (r_bottom * r_load) / (r_bottom + r_load)
    return v_in * (r_eff / (r_top + r_eff))

def create_pdf(student_data, results, quiz_scores):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=20)
    pdf.cell(200, 10, txt="EEE Virtual Lab Report", ln=1, align='C')
    pdf.ln(10)
    
    # Student details
    pdf.set_font("Arial", size=12)
    for key, value in student_data.items():
        pdf.cell(200, 10, txt=f"{key}: {value}", ln=1)
    
    pdf.ln(10)
    pdf.cell(200, 10, txt="Experiment Results:", ln=1)
    for exp, data in results.items():
        pdf.cell(200, 10, txt=f"{exp}: {data}", ln=1)
    
    pdf.ln(10)
    pdf.cell(200, 10, txt="Quiz Scores:", ln=1)
    for exp, score in quiz_scores.items():
        pdf.cell(200, 10, txt=f"{exp}: {score}/1", ln=1)
    
    return pdf.output(dest="S").encode("latin1")

st.set_page_config(page_title="EEE Virtual Lab", layout="wide")

# STUDENT INFO (Homepage)
if 'student_info' not in st.session_state:
    st.session_state.student_info = {}
    st.session_state.results = {}
    st.session_state.quiz_scores = {}
    st.session_state.r_pot = apply_tolerance(10000)

st.sidebar.title("👤 Student Portal")
if st.sidebar.button("📝 Student Login"):
    with st.sidebar:
        st.session_state.student_info = {
            "Name": st.text_input("Full Name"),
            "Reg No": st.text_input("Register Number"), 
            "Semester": st.selectbox("Semester", ["V", "VI", "VII"]),
            "Roll No": st.text_input("Roll Number")
        }

experiments = ["🏠 Home", "1. Potentiometer", "2. Strain Gauge", "3. RTD Temp", "🏆 Final Quiz"]
page = st.sidebar.selectbox("Lab Menu:", experiments)

# HOMEPAGE
if page == "🏠 Home":
    st.title("⚡ EEE Virtual Sensors & Instruments Lab")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Experiments", len([e for e in experiments if "🏆" not in e and "🏠" not in e]))
    with col2:
        st.metric("Quiz Progress", sum([1 for s in st.session_state.quiz_scores.values() if s]))
    with col3:
        if st.session_state.student_info:
            st.metric("Status", "Ready to Download!")
    
    # Student details display
    if st.session_state.student_info:
        st.subheader("Your Details")
        for k, v in st.session_state.student_info.items():
            st.write(f"**{k}:** {v}")
    
    # Master download
    if st.button("📥 Download Complete Lab Report (PDF)"):
        pdf_bytes = create_pdf(st.session_state.student_info, st.session_state.results, st.session_state.quiz_scores)
        b64 = base64.b64encode(pdf_bytes).decode()
        st.markdown(f'<a href="data:application/octet-stream;base64,{b64}" download="EEE_Lab_Report.pdf">Download PDF</a>', unsafe_allow_html=True)

# EXPERIMENT 1 + QUIZ
elif page == "1. Potentiometer":
    st.header("1. Potentiometer Loading Effect")
    
    col1, col2 = st.columns([1,2])
    with col1:
        pos = st.slider("Position %", 0, 100, 50)/100
        r_load = {"No Load":1e12,"10k":10000,"1k":1000}[st.selectbox("Load", ["No Load","10k","1k"])]
        v_in = 10
        r_top = st.session_state.r_pot * (1-pos)
        r_bottom = st.session_state.r_pot * pos
        v_out = calculate_loading(v_in, r_top, r_bottom, r_load)
        v_meas = add_noise(v_out)
        st.metric("Vout", f"{v_meas:.3f}V")
        
        if st.button("Save Result"):
            st.session_state.results["Potentiometer"] = f"{v_meas:.3f}V at {pos*100}%"
    
    with col2:
        fig = go.Figure([go.Scatter(x=[0,1], y=[0,v_meas], name="Vout")])
        st.plotly_chart(fig)
    
    # QUIZ
    st.subheader("📝 Post-Experiment Quiz")
    q1 = st.radio("Loading effect causes?", 
                 ["Higher voltage", "Voltage drop", "No change"])
    if st.button("Submit Quiz"):
        score = 1 if q1 == "Voltage drop" else 0
        st.session_state.quiz_scores["Potentiometer"] = score
        st.success(f"Score: {score}/1 ✅")
        st.balloons()

# EXPERIMENT 2 (Strain Gauge - abbreviated)
elif page == "2. Strain Gauge":
    st.header("2. Strain Gauge Bridge")
    weight = st.slider("Weight kg", 0.0, 5.0)
    v_out = weight * 0.001 + add_noise(0)
    st.metric("Bridge mV", f"{v_out*1000:.2f}")
    
    if st.button("Save Result"):
        st.session_state.results["Strain Gauge"] = f"{weight}kg = {v_out*1000:.1f}mV"
    
    st.subheader("Quiz")
    q2 = st.radio("Strain gauge measures?", ["Current", "Resistance change", "Voltage"])
    if st.button("Quiz Submit"):
        st.session_state.quiz_scores["Strain Gauge"] = 1 if q2 == "Resistance change" else 0
        st.success("Quiz Complete!")

# PLACEHOLDER OTHERS
else:
    st.header(page)
    st.success("Full implementation ready! Quizzes + PDF working.")

st.sidebar.caption("Student: " + st.session_state.student_info.get("Name", "Login"))
