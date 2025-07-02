import streamlit as st
import requests
import numpy as np
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import folium
from streamlit_folium import st_folium
import random

# --- Page Config ---
st.set_page_config(page_title="☄️ Cosmic Radiation Risk Calculator", layout="wide")

st.title("🚀 Cosmic Radiation Risk Calculator")
st.markdown("Estimate radiation risk from cosmic exposure during space missions using **live space weather data** 🌌")
st.markdown("---")

# --- Sidebar Inputs ---
with st.sidebar:
    st.header("🛠️ Mission Parameters")
    mission_days = st.slider("Mission Duration (days)", 1, 1000, 180)
    shielding_material = st.selectbox("Shielding Material", ["None", "Aluminum", "Polyethylene"])

# --- Caching Functions ---
@st.cache_data(ttl=600)
def get_proton_flux():
    url = "https://services.swpc.noaa.gov/json/goes/primary/differential-proton-flux-1-day.json"
    data = requests.get(url).json()
    df = pd.DataFrame(data)
    df['time_tag'] = pd.to_datetime(df['time_tag'])
    df['flux'] = pd.to_numeric(df['flux'], errors='coerce')
    df = df[df['energy'] == '>=10 MeV'].dropna()
    return df

@st.cache_data
def simulate_doses(total_dose):
    return np.random.normal(total_dose, total_dose * 0.1, 10000)

# --- Get Data ---
try:
    df = get_proton_flux()
    flux = df['flux'].iloc[-1]
    st.success(f"📡 Live Proton Flux (≥10 MeV): {flux:.2e} protons/cm²/s/sr")

    fig = px.line(df, x="time_tag", y="flux",
                  title="☄️ Real-Time Proton Flux (≥10 MeV)",
                  labels={"time_tag": "Time (UTC)", "flux": "Proton Flux"})
    st.plotly_chart(fig, use_container_width=True)
except Exception as e:
    flux = 100
    st.warning("⚠️ Using fallback: 100 protons/cm²/s/sr")

# --- Dose Calculations ---
base_dose_per_day = flux * 0.00005
shield_factors = {'None': 1.0, 'Aluminum': 0.7, 'Polyethylene': 0.5}
daily_dose = base_dose_per_day * shield_factors[shielding_material]
total_dose = daily_dose * mission_days
risk_percent = (total_dose / 1000) * 5
xray_equiv = total_dose / 0.1

# --- Metrics Display ---
col1, col2, col3 = st.columns(3)
col1.metric("☢️ Total Dose (mSv)", f"{total_dose:.2f}")
col2.metric("⚠️ Cancer Risk", f"{risk_percent:.2f} %")
col3.info(f"💡 ~{xray_equiv:.0f} chest X-rays")

# --- Risk Category ---
if risk_percent < 1:
    category = "🟢 Low"
elif risk_percent < 5:
    category = "🟠 Moderate"
else:
    category = "🔴 High"
st.subheader(f"🧬 Risk Category: {category}")

# --- Shielding Table ---
st.markdown("### 🛡️ Shielding Effectiveness")
df_shield = pd.DataFrame({
    "Material": list(shield_factors.keys()),
    "Shield Factor": list(shield_factors.values()),
    "Dose per Day (mSv)": [base_dose_per_day * f for f in shield_factors.values()]
})
st.table(df_shield)

# --- Monte Carlo Plot ---
st.markdown("### 🎲 Dose Simulation (Monte Carlo)")
simulated_doses = simulate_doses(total_dose)
fig2, ax = plt.subplots()
ax.hist(simulated_doses, bins=50, color='skyblue', edgecolor='black')
ax.set_title("Simulated Total Dose Distribution")
ax.set_xlabel("Dose (mSv)")
ax.set_ylabel("Frequency")
st.pyplot(fig2)

# --- Educational Tabs ---
st.markdown("### 📚 Learn More")
tab1, tab2, tab3, tab4 = st.tabs([
    "🌠 Cosmic Radiation",
    "🧪 Risk Calculation",
    "🛡️ Shielding",
    "📉 Assumptions"
])

with tab1:
    st.markdown("""
    Cosmic radiation includes energetic particles from the sun and beyond our galaxy.  
    They pose risks to astronauts once outside Earth’s protective magnetic field.
    """)

with tab2:
    st.markdown("""
    Dose = Flux × Time × Shielding Factor  
    Risk = 5% increase in lifetime cancer per Sv (ICRP model)
    """)

with tab3:
    st.markdown("""
    - **None**: No protection  
    - **Aluminum**: ~30% dose reduction  
    - **Polyethylene**: ~50% dose reduction  
    """)

with tab4:
    st.markdown("""
    ⚠️ Simplified model using only ≥10 MeV flux  
    Assumes linear risk, no biological repair  
    """)

# --- Enhancements ---
st.markdown("---")
st.subheader("🚀 Future Enhancements")

# Mock shower map session
if 'mock_coords' not in st.session_state:
    st.session_state.mock_coords = [(random.uniform(-60, 60), random.uniform(-180, 180)) for _ in range(100)]

with st.expander("✅ Show Mock Showers"):
    if st.checkbox("🌍 Enable Mock Shower Map", value=True):
        m = folium.Map(location=[20, 0], zoom_start=2, tiles="CartoDB dark_matter")
        for lat, lon in st.session_state.mock_coords:
            folium.CircleMarker(
                location=[lat, lon],
                radius=4,
                color="crimson",
                fill=True,
                fill_opacity=0.6
            ).add_to(m)
        st_folium(m, width=700, height=400)
    else:
        st.info("Mock showers are hidden.")

with st.expander("🔜 Pull KASCADE Data"):
    st.write("Historical cosmic ray data via `kcdc.ikp.kit.edu` or FTP.")
    st.code("Source: kcdc.ikp.kit.edu")

with st.expander("🔜 Overlay Atmospheric Conditions"):
    st.write("Simulate atmospheric shielding using radiation density maps.")

with st.expander("🔜 Timeline Animation"):
    st.write("Use `folium.plugins.TimestampedGeoJson` for animated event mapping.")
    st.code("from folium.plugins import TimestampedGeoJson")

# --- Footer ---
st.markdown("---")
st.caption("📘 Based on ICRP guidance. For educational use only. Built with ❤️ using Streamlit.")
