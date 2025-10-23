import pandas as pd
import streamlit as st
import numpy as np

# --- PAGE CONFIG ---
st.set_page_config(page_title="Radiology Procedures Counter", layout="wide")

# --- CUSTOM CSS ---
st.markdown("""
<style>
body {
    background-color: #1e1e1e;
    color: #ffffff;
    font-family: 'Segoe UI', sans-serif;
}
.main .block-container {
    max-width: 95%;
    padding-left: 2rem;
    padding-right: 2rem;
}
h1 {
    color: #FFA500;
    font-size: 60px;
    margin-bottom: 0;
}
</style>
""", unsafe_allow_html=True)

# --- FILE PATHS ---
excel_path = r"./Global Health Data.xlsx"
logo_path = r"./AAML_Logo.png"

# --- First Row: Logo Top-Left ---
st.image(logo_path, width=500)  # variable used correctly

# --- Second Row: Centered Title ---
st.markdown("""
<div style="text-align: center; margin-top: 20px;">
    <h1 style="color:#FFFFFF; margin:0;">AAML Radiology Procedures</h1>
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

    # --- SIMULATION PLACEHOLDERS ---
    display_placeholder = st.empty()
    section_placeholder = st.empty()
    chart_placeholder = st.empty()

    # --- PRECOMPUTE CUMULATIVE COUNTS ---
    df_sorted = df.sort_values('PROCEDURE_END')
    start_value = 1  # set your starting number here
    df_sorted['CumulativeCount'] = range(start_value, start_value + len(df_sorted))
    procedure_times = df_sorted['PROCEDURE_END'].values.astype('datetime64[ns]')
    counts = df_sorted['CumulativeCount'].values
    start_time = df['PROCEDURE_END'].min()
    end_time = df['PROCEDURE_END'].max()
    progress = []

    # --- SECTION COLORS ---
    section_colors = {
        "X-Ray": "#FF6F61",
        "CT": "#6A5ACD",
        "MRI": "#20B2AA",
        "US": "#FFA500",
    }

    # --- SIMULATION LOOP ---
    for current_time in pd.date_range(start=start_time, end=end_time, freq='1S'):
        current_time_np = np.datetime64(current_time)

        idx = procedure_times.searchsorted(current_time_np, side='right')
        simulated_count = counts[idx - 1] if idx > 0 else 0

        # Append one entry per second (remove microseconds)
        progress.append({'Time': current_time.replace(microsecond=0), 'Count': simulated_count})

        # --- MAIN COUNTER (flicker-free) ---
        with display_placeholder.container():
            st.markdown(f"""
            <div style='text-align:center; margin-top:20px;'>
                <div style='font-size:120px; font-weight:bold; color:#FFA500;'>{simulated_count:,}</div>
                <div style='font-size:36px; color:#ffffff;'>Procedures Completed</div>
            </div>
            """, unsafe_allow_html=True)

        # --- SECTION COUNTERS (stable) ---
        section_counts = df[df['PROCEDURE_END'] <= current_time].groupby('SECTION_CODE').size()
        with section_placeholder.container():
            section_html = "<div style='display:flex; justify-content:center; flex-wrap:wrap; gap:20px; margin-top:30px;'>"
            for section, count in section_counts.items():
                color = section_colors.get(section, "#888888")
                section_html += f"""<div style="display:inline-block; background-color:{color}; border-radius:15px; padding:25px 35px;
                                     text-align:center; min-width:180px; font-size:36px; font-weight:bold; color:#ffffff;">
                                     {count:,}
                                     <div style="font-size:20px; margin-top:8px;">{section}</div>
                                     </div>"""
            section_html += "</div>"
            st.markdown(section_html, unsafe_allow_html=True)

        # --- LINE CHART (per second, HH:MM:SS) ---
        chart_df = pd.DataFrame(progress)
        chart_df['Time'] = chart_df['Time'].dt.strftime('%H:%M:%S')  # HH:MM:SS only
        chart_df.set_index('Time', inplace=True)
        chart_placeholder.line_chart(chart_df)
import pandas as pd
import streamlit as st
import numpy as np
import time

# --- PAGE CONFIG ---
st.set_page_config(page_title="Radiology Procedures Counter", layout="wide")

# --- CUSTOM CSS (narrower layout) ---
st.markdown("""
<style>
body {
    background-color: #1e1e1e;
    color: #ffffff;
    font-family: 'Segoe UI', sans-serif;
}
.main .block-container {
    max-width: 75%;  /* narrower layout */
    padding-left: 2rem;
    padding-right: 2rem;
}
h1 {
    color: #FFA500;
    font-size: 50px;
    margin-bottom: 0;
}
</style>
""", unsafe_allow_html=True)

# --- FILE PATHS ---
excel_path = r".\Global Health Data.xlsx"
logo_path = r".\AAML_Logo.png"

# --- HEADER ---
col1, col2 = st.columns([2, 5])
with col1:
    st.image(logo_path, use_container_width=True)
with col2:
    st.markdown("<h1>AAML Radiology Procedures</h1>", unsafe_allow_html=True)

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

    # --- SIMULATION PLACEHOLDERS ---
    display_placeholder = st.empty()
    section_placeholder = st.empty()
    chart_placeholder = st.empty()

    # --- PRECOMPUTE CUMULATIVE COUNTS ---
    df_sorted = df.sort_values('PROCEDURE_END')
    start_time = df['PROCEDURE_END'].min()
    end_time = df['PROCEDURE_END'].max()
    progress = []

    # --- SECTION COLORS ---
    section_colors = {
        "X-Ray": "#FF6F61",
        "CT": "#6A5ACD",
        "MRI": "#20B2AA",
        "US": "#FFA500",
    }

    # --- SIMULATION LOOP (real-time per second) ---
    for current_time in pd.date_range(start=start_time, end=end_time, freq='1S'):
        # --- MAIN COUNTER (flicker-free, exact total) ---
        simulated_count = df[df['PROCEDURE_END'] <= current_time].shape[0]

        with display_placeholder.container():
            st.markdown(f"""
            <div style='text-align:center; margin-top:20px;'>
                <div style='font-size:120px; font-weight:bold; color:#FFA500;'>{simulated_count:,}</div>
                <div style='font-size:36px; color:#ffffff;'>Procedures Completed</div>
            </div>
            """, unsafe_allow_html=True)

        # --- SECTION COUNTERS (stable) ---
        section_counts = df[df['PROCEDURE_END'] <= current_time].groupby('SECTION_CODE').size()
        with section_placeholder.container():
            section_html = "<div style='display:flex; justify-content:center; flex-wrap:wrap; gap:20px; margin-top:30px;'>"
            for section, count in section_counts.items():
                color = section_colors.get(section, "#888888")
                section_html += f"""<div style="display:inline-block; background-color:{color}; border-radius:15px; padding:25px 35px;
                                     text-align:center; min-width:150px; font-size:36px; font-weight:bold; color:#ffffff;">
                                     {count:,}
                                     <div style="font-size:20px; margin-top:8px;">{section}</div>
                                     </div>"""
            section_html += "</div>"
            st.markdown(section_html, unsafe_allow_html=True)

        # --- LINE CHART (per second, HH:MM:SS) ---
        progress.append({'Time': current_time.replace(microsecond=0), 'Count': simulated_count})
        chart_df = pd.DataFrame(progress)
        chart_df['Time'] = chart_df['Time'].dt.strftime('%H:%M:%S')
        chart_df.set_index('Time', inplace=True)
        chart_placeholder.line_chart(chart_df)

        # --- PAUSE 1 SECOND TO UPDATE IN REAL TIME ---
        time.sleep(1)
