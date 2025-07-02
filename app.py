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

# --- Inputs ---
with st.sidebar:
    st.header("🛠️ Mission Parameters")
    mission_days = st.slider("Mission Duration (days)", 1, 1000, 180)
    shielding_material = st.selectbox("Shielding Material", ["None", "Aluminum", "Polyethylene"])

# --- Proton Flux Data ---
url = "https://services.swpc.noaa.gov/json/goes/primary/differential-proton-flux-1-day.json"

try:
    data = requests.get(url).json()
    df = pd.DataFrame(data)
    df['time_tag'] = pd.to_datetime(df['time_tag'])
    df['flux'] = pd.to_numeric(df['flux'], errors='coerce')
    df = df[df['energy'] == '>=10 MeV'].dropna()

    flux = df['flux'].iloc[-1]
    st.success(f"📡 Live Proton Flux (≥10 MeV): {flux:.2e} protons/cm²/s/sr")

    fig = px.line(df, x="time_tag", y="flux",
                  title="☄️ Real-Time Proton Flux (≥10 MeV)",
                  labels={"time_tag": "Time (UTC)", "flux": "Proton Flux"})
    st.plotly_chart(fig, use_container_width=True)
except:
    flux = 100  # fallback
    st.warning("⚠️ Unable to fetch live data. Using fallback: 100 protons/cm²/s/sr")

# --- Dose + Risk Calculation ---
base_dose_per_day = flux * 0.00005
shield_factors = {'None': 1.0, 'Aluminum': 0.7, 'Polyethylene': 0.5}
daily_dose = base_dose_per_day * shield_factors[shielding_material]
total_dose = daily_dose * mission_days
risk_percent = (total_dose / 1000) * 5
xray_equiv = total_dose / 0.1

# --- Display Metrics ---
col1, col2, col3 = st.columns(3)
col1.metric("☢️ Estimated Total Dose (mSv)", f"{total_dose:.2f}")
col2.metric("⚠️ Estimated Cancer Risk", f"{risk_percent:.2f} %")
col3.info(f"💡 ~{xray_equiv:.0f} chest X-rays")

# --- Risk Category ---
if risk_percent < 1:
    category = "🟢 Low"
elif risk_percent < 5:
    category = "🟠 Moderate"
else:
    category = "🔴 High"
st.subheader(f"🧬 Risk Category: {category}")

# --- Shielding Effectiveness Table ---
st.markdown("### 🛡️ Shielding Effectiveness Comparison")
df_shield = pd.DataFrame({
    "Material": list(shield_factors.keys()),
    "Shield Factor": list(shield_factors.values()),
    "Dose per Day (mSv)": [base_dose_per_day * f for f in shield_factors.values()]
})
st.table(df_shield)

# --- Monte Carlo Simulation ---
st.markdown("### 🎲 Monte Carlo Simulation of Dose")
simulated_doses = np.random.normal(total_dose, total_dose * 0.1, 10000)
fig2, ax = plt.subplots()
ax.hist(simulated_doses, bins=50, color='skyblue', edgecolor='black')
ax.set_title("Simulated Dose Distribution")
ax.set_xlabel("Dose (mSv)")
ax.set_ylabel("Frequency")
st.pyplot(fig2)

# --- Educational Tabs ---
st.markdown("### 📚 Learn More")
tab1, tab2, tab3, tab4 = st.tabs([
    "🌠 What is Cosmic Radiation?",
    "🧪 Risk Calculation",
    "🛡️ Shielding",
    "📉 Assumptions"
])

with tab1:
    st.markdown("""
    Cosmic radiation includes energetic particles like protons and ions from the sun and beyond the galaxy.  
    As you leave Earth's magnetic shield, exposure increases significantly.
    """)

with tab2:
    st.markdown("""
    Radiation dose is calculated using flux × time × shielding factor.  
    Risk is estimated using ICRP’s linear model: 5% increase in lifetime cancer risk per Sv.
    """)

with tab3:
    st.markdown("""
    - **None** = Full exposure  
    - **Aluminum** = ~30% dose reduction  
    - **Polyethylene** = ~50% dose reduction  
    Material choice critically affects mission safety.
    """)

with tab4:
    st.markdown("""
    ⚠️ Assumptions:
    - Flux is averaged and only ≥10 MeV considered  
    - No latency or repair mechanisms  
    - Linear risk model applied to all doses  
    """)

# --- Future Enhancements ---
st.markdown("---")
st.subheader("🚀 Future Enhancements (Phases)")

with st.expander("✅ Show Mock Showers"):
    st.write("Simulate random cosmic ray showers using `random` + `folium`.")

    if st.checkbox("🌍 Enable Mock Shower Map", value=True):
        st.markdown("This simulates random cosmic ray impacts on Earth.")
        m = folium.Map(location=[20, 0], zoom_start=2, tiles="CartoDB dark_matter")
        for _ in range(100):
            lat, lon = random.uniform(-60, 60), random.uniform(-180, 180)
            folium.CircleMarker(
                location=[lat, lon],
                radius=4,
                color="crimson",
                fill=True,
                fill_opacity=0.6
            ).add_to(m)
        st_folium(m, width=700, height=400)
    else:
        st.info("Shower map not shown.")

with st.expander("🔜 Pull KASCADE Data"):
    st.write("Historical cosmic ray data from KASCADE detector via FTP or API.")
    st.code("Source: kcdc.ikp.kit.edu")

with st.expander("🔜 Overlay Atmospheric Conditions"):
    st.write("Use Earth models to simulate effects of atmospheric shielding.")

with st.expander("🔜 Timeline Animation"):
    st.write("Use `folium.plugins.TimestampedGeoJson` for animated radiation timelines.")
    st.code("from folium.plugins import TimestampedGeoJson")

# --- Footer ---
st.markdown("---")
st.caption("📘 Based on ICRP estimates. For educational use only. Developed with ❤️ using Streamlit.")
