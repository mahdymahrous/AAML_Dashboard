import pandas as pd
import streamlit as st
import numpy as np
import time
from datetime import datetime, timedelta
import base64

# --- PAGE CONFIG ---
st.set_page_config(page_title="Radiology Procedures Counter", layout="wide")

# --- CUSTOM CSS (centered, single page) ---
st.markdown("""
<style>
body {
    background-color: #1e1e1e;
    color: #ffffff;
    font-family: 'Segoe UI', sans-serif;
    display: flex;
    justify-content: center;
}
.main .block-container {
    max-width: 800px;
    padding: 1rem 2rem;
}
h1 {
    color: #FFA500;
    font-size: 50px;
    text-align: center;
    margin-top: 10px;
    margin-bottom: 20px;
}
.counter, .alltime-counter {
    text-align: center;
    margin: 20px 0;
}
.counter-number, .alltime-number {
    font-size: 100px;
    font-weight: bold;
    color: #FFA500;
}
.counter-label, .alltime-label {
    font-size: 36px;
    color: #ffffff;
}
.clock {
    font-size: 60px;
    color: #00FF00;
    font-weight: bold;
    margin: 20px 0;
    text-align: center;
}
.section-box {
    display: inline-block;
    border-radius: 15px;
    padding: 20px 25px;
    text-align: center;
    min-width: 150px;
    font-size: 36px;
    font-weight: bold;
    color: #ffffff;
    margin: 10px;
}
.section-label {
    font-size: 20px;
    margin-top: 8px;
}
</style>
""", unsafe_allow_html=True)

# --- FILE PATHS ---
excel_path = r"./Global Health Data.xlsx"
logo_path = r"./AAML_Logo.png"

# --- HEADER (logo centered above title using base64) ---
def img_to_base64(path):
    with open(path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

logo_base64 = img_to_base64(logo_path)

st.markdown(f"""
<div style="text-align:center;">
    <img src="data:image/png;base64,{logo_base64}" width="250" style="display:block; margin:auto;">
    <h1>AAML Radiology Procedures</h1>
</div>
""", unsafe_allow_html=True)

# --- LOAD DATA ---
@st.cache_data
def load_data(path):
    df = pd.read_excel(path)
    df['PROCEDURE_END'] = pd.to_datetime(df['PROCEDURE_END'], format="%d-%m-%y %H:%M", errors='coerce')
    df = df.dropna(subset=['PROCEDURE_END'])
    df = df.sort_values('PROCEDURE_END')
    return df

df = load_data(excel_path)

if not df.empty:

    # --- PLACEHOLDERS ---
    alltime_placeholder = st.empty()
    display_placeholder = st.empty()
    section_placeholder = st.empty()
    clock_placeholder = st.empty()

    # --- SECTION COLORS ---
    section_colors = {
        "X-Ray": "#E63946",
        "CT": "#457B9D",
        "US": "#F4A261",
        "X-Ray (BMD)": "#A8DADC",
        "MRI": "#2A9D8F",
        "Other NM": "#6D6875",
        "PET-CT": "#FFB400",
        "X-Ray (Fluoro)": "#D62828",
        "Mamo": "#F77F00",
        "HE": "#264653"
    }

    # --- SIMULATION SETUP ---
    oldest_time = df['PROCEDURE_END'].min()
    now = datetime.now()
    time_of_day_now = now.time()
    simulated_current_time = datetime.combine(oldest_time.date(), time_of_day_now)

    last_procedure_time = df[df['PROCEDURE_END'].dt.date == oldest_time.date()]['PROCEDURE_END'].max()
    if simulated_current_time > last_procedure_time:
        simulated_current_time = last_procedure_time

    # --- FAST-FORWARD PROCEDURES ---
    df_today = df[df['PROCEDURE_END'].dt.date == oldest_time.date()]
    simulated_count = df_today[df_today['PROCEDURE_END'] <= simulated_current_time].shape[0]
    section_counts = df_today[df_today['PROCEDURE_END'] <= simulated_current_time].groupby('SECTION_CODE').size()

    # --- ALL-TIME START ---
    alltime_start = 1_500_000
    total_count = alltime_start + simulated_count

    # --- DISPLAY INITIAL ALL-TIME COUNTER ---
    with alltime_placeholder.container():
        st.markdown(f"""
        <div class='alltime-counter'>
            <div class='alltime-number'>{total_count:,}</div>
            <div class='alltime-label'>All-Time Procedures</div>
        </div>
        """, unsafe_allow_html=True)

    # --- DISPLAY INITIAL TODAY COUNTER ---
    with display_placeholder.container():
        st.markdown(f"""
        <div class='counter'>
            <div class='counter-number'>{simulated_count:,}</div>
            <div class='counter-label'>Procedures Completed Today</div>
        </div>
        """, unsafe_allow_html=True)

    # --- DISPLAY INITIAL SECTION COUNTS ---
    with section_placeholder.container():
        section_html = "<div style='text-align:center;'>"
        for section, count in section_counts.items():
            color = section_colors.get(section, "#888888")
            section_html += f"""<div class='section-box' style='background-color:{color};'>
                                 {count:,}
                                 <div class='section-label'>{section}</div>
                                 </div>"""
        section_html += "</div>"
        st.markdown(section_html, unsafe_allow_html=True)

    # --- FUTURE PROCEDURES FOR TODAY ---
    df_future = df_today[df_today['PROCEDURE_END'] > simulated_current_time]

    # --- LIVE CLOCK AND REAL-TIME COUNT ---
    while True:
        current_time = datetime.now()
        clock_placeholder.markdown(f"<div class='clock'>{current_time.strftime('%d-%m-%Y %H:%M:%S')}</div>", unsafe_allow_html=True)

        # Calculate new simulated count
        elapsed_seconds = (datetime.combine(oldest_time.date(), current_time.time()) - simulated_current_time).total_seconds()
        new_count = df_future[df_future['PROCEDURE_END'] <= simulated_current_time + timedelta(seconds=elapsed_seconds)].shape[0]

        # Update counters
        today_count = simulated_count + new_count
        total_count = alltime_start + today_count

        with display_placeholder.container():
            st.markdown(f"""
            <div class='counter'>
                <div class='counter-number'>{today_count:,}</div>
                <div class='counter-label'>Procedures Completed Today</div>
            </div>
            """, unsafe_allow_html=True)

        with alltime_placeholder.container():
            st.markdown(f"""
            <div class='alltime-counter'>
                <div class='alltime-number'>{total_count:,}</div>
                <div class='alltime-label'>All-Time Procedures</div>
            </div>
            """, unsafe_allow_html=True)

        # --- UPDATE SECTION COUNTS ---
        current_section_counts = df_today[df_today['PROCEDURE_END'] <= simulated_current_time + timedelta(seconds=elapsed_seconds)].groupby('SECTION_CODE').size()
        with section_placeholder.container():
            section_html = "<div style='text-align:center;'>"
            for section, count in current_section_counts.items():
                color = section_colors.get(section, "#888888")
                section_html += f"""<div class='section-box' style='background-color:{color};'>
                                     {count:,}
                                     <div class='section-label'>{section}</div>
                                     </div>"""
            section_html += "</div>"
            st.markdown(section_html, unsafe_allow_html=True)

        time.sleep(1)

