import streamlit as st
import numpy as np
import plotly.graph_objects as go
from experiments.exp_logic import add_noise, apply_tolerance, calculate_loading

st.set_page_config(page_title="EEE Virtual Sensors Lab", layout="wide", page_icon="⚡")

# Global session state for persistence
if 'components_initialized' not in st.session_state:
    st.session_state.components_initialized = False

st.sidebar.title("🔬 Lab Experiments")
experiments = [
    "1. Potentiometer Loading Effect",
    "2. Strain Gauge Bridge Analysis", 
    "3. Temperature Measurement (RTD/Thermistor)",
    "4. Piezo-electric Transducer",
    "5. Hall Effect Speed Control",
    "6. DC Bridges (Wheatstone/Kelvin)",
    "7. AC Bridges (Maxwell/Hay/Schering)",
    "8. Real-time Power Measurement",
    "9. Energy Metering (Wh)",
    "10. Thermocouple Calibration",
    "11. Synchro Transmitter/Receiver",
    "12. Power Quality (Harmonic Distortion)"
]
selected_exp = st.sidebar.selectbox("Choose Experiment:", experiments)

st.title("⚡ EEE Virtual Sensors & Instruments Lab")
st.markdown("**Realistic simulations** with noise, tolerances & loading effects")

# Initialize components once
if not st.session_state.components_initialized:
    st.session_state.r_pot = apply_tolerance(10000)  # 10k pot
    st.session_state.r_strain = apply_tolerance(120) # Strain gauge
    st.session_state.r_rtd = apply_tolerance(100)    # RTD at 0°C
    st.session_state.components_initialized = True

# EXPERIMENT 1: Potentiometer
if selected_exp == experiments[0]:
    st.header("1. Potentiometer Loading Effect")
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Controls")
        v_in = 10.0
        pos = st.slider("Pot Position (%)", 0, 100, 50) / 100
        r_load_options = {"No Load": 1e12, "Light (100k)": 100000, "Medium (10k)": 10000, "Heavy (1k)": 1000}
        load_key = st.selectbox("Load:", list(r_load_options.keys()))
        r_load = r_load_options[load_key]
        
        r_top = st.session_state.r_pot * (1 - pos)
        r_bottom = st.session_state.r_pot * pos
        v_out = calculate_loading(v_in, r_top, r_bottom, r_load)
        v_meas = add_noise(v_out)
        
        st.metric("V_out (Measured)", f"{v_meas:.3f} V", delta=f"{v_in*pos:.3f} V (Ideal)")
    
    with col2:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=[0,1], y=[0, v_in*pos], mode='lines', name="Ideal"))
        fig.add_trace(go.Scatter(x=[0,1], y=[0, v_meas], mode='lines+markers', name="Real"))
        fig.update_layout(title="Vout Comparison", xaxis_title="Normalized", yaxis_title="Volts")
        st.plotly_chart(fig, use_container_width=True)

# EXPERIMENT 2: Strain Gauge
elif selected_exp == experiments[1]:
    st.header("2. Strain Gauge Bridge Analysis")
    col1, col2 = st.columns([1, 2])
    
    with col1:
        weight = st.slider("Load (kg)", 0.0, 5.0, 1.0)
        bridge_v = 5.0
        gf = 2.1  # Gauge factor
        
        delta_r = st.session_state.r_strain * gf * (weight * 9.81 / 1e6)  # Microstrain
        v_out = bridge_v * (delta_r / (4 * st.session_state.r_strain))
        v_meas = add_noise(v_out, 0.0001)
        
        st.metric("Bridge Output", f"{v_meas*1000:.2f} mV")
    
    with col2:
        strains = np.linspace(0, weight*9.81/1e6, 50)
        v_ideal = bridge_v * (st.session_state.r_strain * gf * strains / (4 * st.session_state.r_strain))
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=strains*1e6, y=v_ideal*1000, name="Ideal"))
        fig.add_trace(go.Scatter(x=[weight*9.81/1e6*1e6], y=[v_meas*1000], mode='markers', name="Measured"))
        fig.update_layout(title="Calibration Curve", xaxis_title="Strain (µε)", yaxis_title="mV")
        st.plotly_chart(fig)

# EXPERIMENT 3: Temperature (RTD)
elif selected_exp == experiments[2]:
    st.header("3. Temperature Measurement (RTD)")
    temp = st.slider("Temperature (°C)", -50, 200, 25)
    
    # RTD Pt100: R = 100 * (1 + 0.00385*temp)
    r_meas = st.session_state.r_rtd * (1 + 0.00385 * temp)
    r_noisy = add_noise(r_meas, r_meas*0.001)  # 0.1% noise
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Resistance", f"{r_noisy:.2f} Ω")
    with col2:
        st.metric("Calc Temp", f"{(r_noisy/st.session_state.r_rtd - 1)/0.00385:.1f} °C")
    
    fig = go.Figure()
    temps = np.linspace(-50, 200, 100)
    rs = 100 * (1 + 0.00385 * temps)
    fig.add_trace(go.Scatter(x=temps, y=rs, name="RTD Curve"))
    fig.add_trace(go.Scatter(x=[temp], y=[r_noisy], mode='markers', name="Measured"))
    st.plotly_chart(fig)

# PLACEHOLDER FOR REMAINING (IMPLEMENT SIMILARLY)
else:
    st.header(selected_exp)
    st.warning("🔧 Coming soon! Realistic physics + noise implemented.")
    st.info("**Implemented:** Exp 1-3 fully working. Others use same pattern.")
    
    # Quick demo plot
    fig = go.Figure(go.Scatter(x=np.linspace(0,10,100), y=np.sin(np.linspace(0,10,100)) + np.random.normal(0,0.1,100), name="Noisy Signal"))
    st.plotly_chart(fig)

st.divider()
st.caption("🌟 EEE Virtual Lab | Built with Streamlit | Realistic Errors Simulated")
