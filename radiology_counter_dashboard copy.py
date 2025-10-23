import pandas as pd
import streamlit as st
import numpy as np
import time

st.set_page_config(page_title="Radiology Procedures Counter", layout="wide")

# --- CSS for page width ---
st.markdown(
    """
    <style>
    .main .block-container { max-width: 75%; padding-left: 2rem; padding-right: 2rem; }
    </style>
    """, unsafe_allow_html=True
)

# --- Upload Excel and Logo ---
excel_file = st.file_uploader("Upload Excel file", type=["xlsx"])
logo_file = st.file_uploader("Upload Logo (PNG/JPG)", type=["png","jpg"])

if excel_file is not None and logo_file is not None:
    st.image(logo_file, use_container_width=True)
    
    # --- LOAD DATA ---
    @st.cache_data
    def load_data(file):
        df = pd.read_excel(file)
        df['PROCEDURE_END'] = pd.to_datetime(df['PROCEDURE_END'], errors='coerce')
        df = df.dropna(subset=['PROCEDURE_END'])
        df = df.sort_values('PROCEDURE_END')
        return df

    df = load_data(excel_file)

    if df.empty:
        st.error("No valid PROCEDURE_END times found in the file.")
    else:
        st.success(f"Loaded {len(df)} procedures.")

        # --- FILTER BY SECTION ---
        section_options = sorted(df['SECTION_CODE'].dropna().unique())
        selected_section = st.selectbox("Filter by Section:", ["All"] + list(section_options))
        if selected_section != "All":
            df = df[df['SECTION_CODE'] == selected_section]

        # --- SIMULATION SETTINGS ---
        start_time = df['PROCEDURE_END'].min()
        end_time = df['PROCEDURE_END'].max()
        st.write(f"Time range: {start_time} → {end_time}")

        speed = st.slider("Playback speed (seconds per simulated second):", 0.01, 1.0, 0.2, step=0.01)
        update_every_seconds = st.slider("Update counter every N seconds:", 1, 30, 5)

        if st.button("▶ Start Simulation"):
            display_placeholder = st.empty()
            chart_placeholder = st.empty()

            df_sorted = df.sort_values('PROCEDURE_END')
            df_sorted['CumulativeCount'] = range(0, len(df_sorted))

            procedure_times = df_sorted['PROCEDURE_END'].values.astype('datetime64[ns]')
            counts = df_sorted['CumulativeCount'].values

            progress = []

            for current_time in pd.date_range(start=start_time, end=end_time, freq='1S'):
                if current_time.second % update_every_seconds != 0:
                    continue

                idx = procedure_times.searchsorted(np.datetime64(current_time), side='right')
                simulated_count = counts[idx - 1] if idx > 0 else 0
                progress.append({'Time': current_time, 'Count': simulated_count})

                with display_placeholder.container():
                    st.markdown(
                        f"<div style='text-align:center; margin-top:20px;'>"
                        f"<div style='font-size:90px; font-weight:bold; color: orange;'>{simulated_count:,}</div>"
                        f"<div style='font-size:28px; color:white;'>Procedures Completed So Far</div></div>",
                        unsafe_allow_html=True
                    )

                chart_placeholder.line_chart(pd.DataFrame(progress).set_index('Time'))
                time.sleep(speed)

            st.success("✅ Simulation complete")
