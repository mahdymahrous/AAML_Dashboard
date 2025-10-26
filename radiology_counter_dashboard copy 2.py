import pandas as pd
import streamlit as st
import numpy as np
import time
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import base64

# --- PAGE CONFIG ---
st.set_page_config(page_title="Radiology Procedures Counter", layout="wide")

with open("./BG.png", "rb") as f:
    bg_base64 = base64.b64encode(f.read()).decode()

# --- CUSTOM CSS ---
st.markdown(f"""
<style>
body, .stApp {{
    background-image: url("data:image/png;base64,{bg_base64}");
    background-size: cover;
    background-repeat: no-repeat;
    background-attachment: fixed;
    color: #ffffff;
}}
.main .block-container {{
    max-width: 900px;
    padding: 1rem 2rem;
    background-color: rgba(0,0,0,0.4);
    border-radius: 15px;
}}
h1 {{
    color: #FFA500;
    font-size: 50px;
    text-align: center;
    margin-top: 10px;
    margin-bottom: 20px;
}}
.counter {{
    text-align: center;
    margin: 20px 0;
    padding: 0;
    border: none;
    border-radius: 0;
    background-color: transparent;
    box-shadow: none;
}}
.counter-number {{
    font-size: 120px;
    font-weight: bold;
    color: #FFA500;
    text-shadow: 0 0 20px #FFA500;
}}
.counter-label {{
    font-size: 42px;
    color: #ffffff;
    letter-spacing: 1px;
}}
.alltime-counter {{
    text-align: center;
    margin: 20px 0;
    padding: 0;
    border: none;
    border-radius: 0;
    background-color: transparent;
    box-shadow: none;
}}
.alltime-number {{ 
    font-size: 120px;
    font-weight: bold;
    color: #ec3903;
    text-shadow: 0 0 20px #FFA500;
}}
.alltime-label {{
    font-size: 42px;
    color: #ffffff;
    letter-spacing: 1px;
}}
.datetime-container {{
    text-align: center;
    margin: 20px 0 40px 0;
}}
.current-date {{
    font-size: 32px;
    font-weight: 600;
    color: #FFFFFF;
    text-transform: uppercase;
    border-bottom: 3px solid #FFA500;
    display: inline-block;
    padding-bottom: 4px;
    margin-bottom: 10px;
    letter-spacing: 1px;
}}
.clock {{
    font-size: 40px;
    color: #00FF88;
    font-weight: bold;
    font-family: 'Consolas', 'Courier New', monospace;
    text-shadow: 0 0 10px #00FF88;
}}
</style>
""", unsafe_allow_html=True)

# --- HEADER ---
def img_to_base64(path):
    with open(path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

logo_base64 = img_to_base64("./AAML_Logo.png")

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
    df['PROCEDURE_END'] = df['PROCEDURE_END'] + pd.to_timedelta(np.random.randint(0, 60, len(df)), unit='s')
    df = df.sort_values('PROCEDURE_END')
    return df

df = load_data("./Global Health Data.xlsx")

# --- TIMEZONE ---
tz = ZoneInfo("Asia/Riyadh")

if not df.empty:
    st.sidebar.header("Simulation Setup")
    default_alltime = 1_554_362
    default_date = df['PROCEDURE_END'].dt.date.min()

    alltime_start = st.sidebar.number_input(
        "Enter All-Time Start Value",
        min_value=0,
        value=default_alltime,
        step=1000,
        format="%d"
    )

    available_dates = sorted(df['PROCEDURE_END'].dt.date.unique())
    selected_date = st.sidebar.selectbox(
        "Select a Date to Simulate",
        options=available_dates,
        index=available_dates.index(default_date),
        format_func=lambda d: d.strftime("%d-%m-%Y")
    )

    st.sidebar.success(f"Simulation auto-started for **{selected_date.strftime('%d-%m-%Y')}** with All-Time {alltime_start:,}")

    # --- PLACEHOLDERS ---
    total_counter_placeholder = st.empty()
    datetime_placeholder = st.empty()
    display_placeholder = st.empty()

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

    simulated_count = df_today[df_today['PROCEDURE_END'] <= simulated_current_time].shape[0]
    total_count = alltime_start + simulated_count

    # --- INITIAL DISPLAY ---
    total_counter_placeholder.markdown(f"""
        <div class='alltime-counter'>
            <div class='alltime-number'>{total_count:,}</div>
            <div class='alltime-label'>Total Procedures Since 1st Dec. 2023</div>
        </div>
    """, unsafe_allow_html=True)

    datetime_placeholder.markdown(f"""
        <div class='datetime-container'>
            <div class='current-date'>{datetime.now(tz).strftime('%A, %d %B %Y')}</div>
            <div class='clock'>{datetime.now(tz).strftime('%H:%M:%S')}</div>
        </div>
    """, unsafe_allow_html=True)

    display_placeholder.markdown(f"""
        <div class='counter'>
            <div class='counter-number'>{simulated_count:,}</div>
            <div class='counter-label'>Procedures Today</div>
        </div>
    """, unsafe_allow_html=True)

    df_future = df_today[df_today['PROCEDURE_END'] > simulated_current_time]

    # --- LIVE SIMULATION LOOP ---
    while True:
        current_time = datetime.now(tz)
        elapsed_seconds = (datetime.combine(selected_date, current_time.time()) - simulated_current_time).total_seconds()
        new_count = df_future[df_future['PROCEDURE_END'] <= simulated_current_time + timedelta(seconds=elapsed_seconds)].shape[0]

        today_count = simulated_count + new_count
        total_count = alltime_start + today_count

        # Update Total counter
        total_counter_placeholder.markdown(f"""
            <div class='alltime-counter'>
                <div class='alltime-number'>{total_count:,}</div>
                <div class='alltime-label'>Total Procedures Since 1st Dec. 2023</div>
            </div>
        """, unsafe_allow_html=True)

        # Update date/time
        datetime_placeholder.markdown(f"""
            <div class='datetime-container'>
                <div class='current-date'>{datetime.now(tz).strftime('%A, %d %B %Y')}</div>
                <div class='clock'>{current_time.strftime('%H:%M:%S')}</div>
            </div>
        """, unsafe_allow_html=True)

        # Update today's procedures
        display_placeholder.markdown(f"""
            <div class='counter'>
                <div class='counter-number'>{today_count:,}</div>
                <div class='counter-label'>Procedures Today</div>
            </div>
        """, unsafe_allow_html=True)

        time.sleep(1)
