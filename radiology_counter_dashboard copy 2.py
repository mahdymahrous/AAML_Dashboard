import pandas as pd
import streamlit as st
import numpy as np
import time
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo  # Python 3.9+
import base64

# --- PAGE CONFIG ---
st.set_page_config(page_title="Radiology Procedures Counter", layout="wide")

# --- CUSTOM CSS ---
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
    max-width: 900px;
    padding: 1rem 2rem;
}
h1 {
    color: #FFA500;
    font-size: 50px;
    text-align: center;
    margin-top: 10px;
    margin-bottom: 20px;
}

/* --- Today's Counter: Highlighted --- */
.counter {
    text-align: center;
    margin: 20px 0;
    padding: 20px;
    border: 3px solid #FFA500;
    border-radius: 20px;
    background-color: #1f1f1f;
    box-shadow: 0 0 30px #FFA500;
}
.counter-number {
    font-size: 120px;  /* Bigger for emphasis */
    font-weight: bold;
    color: #FFA500;
    text-shadow: 0 0 20px #FFA500;
}
.counter-label {
    font-size: 42px;
    color: #ffffff;
    letter-spacing: 1px;
}

/* --- All-Time Counter: Secondary --- */
.alltime-counter {
    text-align: center;
    margin: 20px 0;
    padding: 15px;
    border-radius: 15px;
    background-color: #2e2e2e;
    border: 2px dashed #888888;
    box-shadow: 0 0 10px #888888;
}
.alltime-number {
    font-size: 60px;   /* Smaller than today */
    font-weight: bold;
    color: #888888;
}
.alltime-label {
    font-size: 28px;
    color: #cccccc;
}

/* --- Date & Clock --- */
.datetime-container {
    text-align: center;
    margin: 20px 0 40px 0;
}
.current-date {
    font-size: 32px;       /* smaller than title */
    font-weight: 600;
    color: #FFFFFF;
    text-transform: uppercase;
    border-bottom: 3px solid #FFA500;
    display: inline-block;
    padding-bottom: 4px;
    margin-bottom: 10px;
    letter-spacing: 1px;
}
.clock {
    font-size: 40px;       /* smaller than title */
    color: #00FF88;
    font-weight: bold;
    font-family: 'Consolas', 'Courier New', monospace;
    text-shadow: 0 0 10px #00FF88;
}

/* --- Sections --- */
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
    transition: transform 0.2s;
}
.section-box:hover {
    transform: scale(1.1);
}
.section-label {
    font-size: 20px;
    margin-top: 8px;
}

/* --- Glow for updated sections (minimal addition) --- */
@keyframes glowPulse {
    0%   { box-shadow: 0 0 6px 2px rgba(255,255,255,0.35); transform: translateY(0); }
    50%  { box-shadow: 0 0 24px 8px rgba(255,255,255,0.65); transform: translateY(-3px); }
    100% { box-shadow: 0 0 6px 2px rgba(255,255,255,0.35); transform: translateY(0); }
}
.glow {
    animation: glowPulse 1s ease-in-out;
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
    <img src="data:image/png;base64,{logo_base64}" width="400" style="display:block; margin:auto;">
    <h1>AAML Radiology Procedures</h1>
</div>
""", unsafe_allow_html=True)

# --- LOAD DATA ---
@st.cache_data
def load_data(path):
    df = pd.read_excel(path)
    df['PROCEDURE_END'] = pd.to_datetime(df['PROCEDURE_END'], format="%d-%m-%y %H:%M:%S", errors='coerce')
    df = df.dropna(subset=['PROCEDURE_END'])
    # Add random seconds to PROCEDURE_END to ensure uniqueness
    df['PROCEDURE_END'] = df['PROCEDURE_END'] + pd.to_timedelta(np.random.randint(0, 60, len(df)), unit='s')
    df = df.sort_values('PROCEDURE_END')
    return df

df = load_data(excel_path)

# --- TIMEZONE ---
tz = ZoneInfo("Asia/Riyadh")  # GMT+3

if not df.empty:
    # --- AUTO-START SIMULATION WITH DEFAULT VALUES ---
    st.sidebar.header("Simulation Setup")

    default_alltime = 1_554_362
    default_date = df['PROCEDURE_END'].dt.date.min()

    # All-Time input (editable)
    alltime_start = st.sidebar.number_input(
        "Enter All-Time Start Value",
        min_value=0,
        value=default_alltime,
        step=1000,
        format="%d"
    )

    # Date picker (editable)
    available_dates = sorted(df['PROCEDURE_END'].dt.date.unique())
    selected_date = st.sidebar.selectbox(
        "Select a Date to Simulate",
        options=available_dates,
        index=available_dates.index(default_date),
        format_func=lambda d: d.strftime("%d-%m-%Y")
    )

    # Auto-start simulation
    start_sim = True
    st.sidebar.success(f"Simulation auto-started for **{selected_date.strftime('%d-%m-%Y')}** with All-Time {alltime_start:,}")

    # --- PLACEHOLDERS ---
    datetime_placeholder = st.empty()
    alltime_placeholder = st.empty()
    display_placeholder = st.empty()
    section_placeholder = st.empty()

    # --- SECTION COLORS ---
    section_colors = {
        "X-Ray": "#E63946",
        "CT": "#457B9D",
        "US": "#F4A261",
        "X-Ray (BMD)": "#A8DADC8F",
        "MRI": "#2A9D8F",
        "Other NM": "#6D6875",
        "PET-CT": "#FFB400",
        "X-Ray (Fluoro)": "#D62828",
        "Mamo": "#F77F00",
        "HE": "#264653"
    }

    # --- SIMULATION SETUP ---
    now = datetime.now(tz)
    time_of_day_now = now.time()

    df_today = df[df['PROCEDURE_END'].dt.date == selected_date]
    if df_today.empty:
        st.error(f"No procedures found for {selected_date.strftime('%d-%m-%Y')}.")
        st.stop()

    simulated_current_time = datetime.combine(selected_date, time_of_day_now)
    last_procedure_time = df_today['PROCEDURE_END'].max()
    if simulated_current_time > last_procedure_time:
        simulated_current_time = last_procedure_time

    # --- INITIAL COUNTS ---
    simulated_count = df_today[df_today['PROCEDURE_END'] <= simulated_current_time].shape[0]
    section_counts = df_today[df_today['PROCEDURE_END'] <= simulated_current_time].groupby('SECTION_CODE').size()
    total_count = alltime_start + simulated_count

    # --- INITIAL DISPLAY ---
    with datetime_placeholder.container():
        st.markdown(f"""
        <div class='datetime-container'>
            <div class='current-date'>{datetime.now(tz).strftime('%A, %d %B %Y')}</div>
            <div class='clock'>{datetime.now(tz).strftime('%H:%M:%S')}</div>
        </div>
        """, unsafe_allow_html=True)

    with alltime_placeholder.container():
        st.markdown(f"""
        <div class='alltime-counter'>
            <div class='alltime-number'>{total_count:,}</div>
            <div class='alltime-label'>Total Procedures</div>
        </div>
        """, unsafe_allow_html=True)

    with display_placeholder.container():
        st.markdown(f"""
        <div class='counter'>
            <div class='counter-number'>{simulated_count:,}</div>
            <div class='counter-label'>Procedures Today</div>
        </div>
        """, unsafe_allow_html=True)

    with section_placeholder.container():
        section_html = "<div style='text-align:center;'>"
        for section, count in section_counts.items():
            color = section_colors.get(section, "#888888")
            section_html += f"""
            <div class='section-box' style='background-color:{color};'>
                {count:,}
                <div class='section-label'>{section}</div>
            </div>"""
        section_html += "</div>"
        st.markdown(section_html, unsafe_allow_html=True)

    # --- FUTURE PROCEDURES ---
    df_future = df_today[df_today['PROCEDURE_END'] > simulated_current_time]

    # --- Prepare previous counts for change detection (minimal addition) ---
    previous_section_counts = section_counts.copy()

    # --- LIVE SIMULATION LOOP ---
    while True:
        current_time = datetime.now(tz)

        # --- UPDATED DATETIME DISPLAY ---
        with datetime_placeholder.container():
            st.markdown(f"""
            <div class='datetime-container'>
                <div class='current-date'>{datetime.now(tz).strftime('%A, %d %B %Y')}</div>
                <div class='clock'>{current_time.strftime('%H:%M:%S')}</div>
            </div>
            """, unsafe_allow_html=True)

        elapsed_seconds = (datetime.combine(selected_date, current_time.time()) - simulated_current_time).total_seconds()
        new_count = df_future[df_future['PROCEDURE_END'] <= simulated_current_time + timedelta(seconds=elapsed_seconds)].shape[0]

        today_count = simulated_count + new_count
        total_count = alltime_start + today_count

        # Update counters
        with display_placeholder.container():
            st.markdown(f"""
            <div class='counter'>
                <div class='counter-number'>{today_count:,}</div>
                <div class='counter-label'>Procedures Today</div>
            </div>
            """, unsafe_allow_html=True)

        with alltime_placeholder.container():
            st.markdown(f"""
            <div class='alltime-counter'>
                <div class='alltime-number'>{total_count:,}</div>
                <div class='alltime-label'>Total Procedures</div>
            </div>
            """, unsafe_allow_html=True)

        current_section_counts = df_today[df_today['PROCEDURE_END'] <= simulated_current_time + timedelta(seconds=elapsed_seconds)].groupby('SECTION_CODE').size()

        # --- Detect which sections increased since last iteration (minimal addition) ---
        # create a union index so new sections are handled too
        union_index = previous_section_counts.index.union(current_section_counts.index)
        prev_reindexed = previous_section_counts.reindex(union_index, fill_value=0)
        curr_reindexed = current_section_counts.reindex(union_index, fill_value=0)
        diffs = curr_reindexed - prev_reindexed
        updated_sections = diffs[diffs > 0].index.tolist()

        with section_placeholder.container():
            section_html = "<div style='text-align:center;'>"
            # iterate current counts to preserve the same visual behavior
            for section, count in current_section_counts.items():
                color = section_colors.get(section, "#888888")
                glow_class = "glow" if section in updated_sections else ""
                section_html += f"""
                <div class='section-box {glow_class}' style='background-color:{color};'>
                    {count:,}
                    <div class='section-label'>{section}</div>
                </div>"""
            section_html += "</div>"
            st.markdown(section_html, unsafe_allow_html=True)

        # update previous counts for next loop
        previous_section_counts = curr_reindexed.copy()

        time.sleep(1)

