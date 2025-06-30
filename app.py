import streamlit as st
import requests
import numpy as np
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="☄️ Cosmic Radiation Risk Calculator", layout="centered")

st.title("🚀 Cosmic Radiation Risk Calculator")
st.markdown("Estimate radiation risk from cosmic exposure during space missions using live data 🌌")

# --- Inputs ---
mission_days = st.slider("Mission Duration (days)", 1, 1000, 180)
shielding_material = st.selectbox("Shielding Material", ["None", "Aluminum", "Polyethylene"])

# --- Real-time proton flux from NOAA ---
url = "https://services.swpc.noaa.gov/json/goes/primary/differential-proton-flux-1-day.json"

try:
    data = requests.get(url).json()
    df = pd.DataFrame(data)
    df['time_tag'] = pd.to_datetime(df['time_tag'])
    df['flux'] = pd.to_numeric(df['flux'], errors='coerce')
    df = df[df['energy'] == '>=10 MeV']  # Focus on >10 MeV range
    df = df.dropna()

    # Latest value
    flux = df['flux'].iloc[-1]
    st.success(f"Live Proton Flux (≥10 MeV): {flux:.2e} protons/cm²/s/sr")

    # Plot
    fig = px.line(df, x="time_tag", y="flux", title="☄️ Real-Time Proton Flux (≥10 MeV)", 
                  labels={"time_tag": "Time (UTC)", "flux": "Proton Flux"})
    st.plotly_chart(fig, use_container_width=True)
except Exception as e:
    flux = 100  # fallback
    st.warning("⚠️ Unable to fetch live data. Using default flux: 100 p/cm²/s/sr")

# --- Dose Calculation ---
base_dose_per_day = flux * 0.00005  # empirical approximation
shield_factors = {'None': 1.0, 'Aluminum': 0.7, 'Polyethylene': 0.5}
daily_dose = base_dose_per_day * shield_factors[shielding_material]
total_dose = daily_dose * mission_days  # in mSv

# --- Risk Estimate ---
risk_percent = (total_dose / 1000) * 5  # linear ERR model

# --- Display Metrics ---
st.metric("☢️ Estimated Total Dose (mSv)", f"{total_dose:.2f}")
st.metric("⚠️ Estimated Cancer Risk", f"{risk_percent:.2f} %")

# --- Additional Comparison ---
xray_equiv = total_dose / 0.1  # chest X-ray ~0.1 mSv
st.info(f"💡 Equivalent to ~{xray_equiv:.0f} chest X-rays")

# --- Risk Category ---
if risk_percent < 1:
    category = "🟢 Low"
elif risk_percent < 5:
    category = "🟠 Moderate"
else:
    category = "🔴 High"
st.subheader(f"🧬 Risk Category: {category}")

st.caption("ICRP model: 5% risk increase per 1 Sv of exposure. Not for clinical use.")
