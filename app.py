import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
from datetime import date, datetime
import base64


THEME_COLOR = "#00687a"  
RISK_COLORS = {
    "Low": "#2ecc71",    
    "Medium": "#f39c12", 
    "High": "#e74c3c"    
}
MISSING_FLAG = -999.0
MAX_CITY_LENGTH = 100


st.set_page_config(page_title="ParadeGuard", page_icon="🌡️", layout="wide")


def set_background(image_file):
    with open(image_file, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()
    page_bg = f"""
    <style>
    .stApp {{
        background: url("data:image/jpg;base64,{encoded}") no-repeat center center fixed;
        background-size: cover;
    }}
    </style>
    """
    st.markdown(page_bg, unsafe_allow_html=True)

try:
    set_background("background.jpg")
except:
    pass  


white_text_css = """
<style>
/* Make ALL text white and bold */
body, .stApp, .stMarkdown, .stText, 
.stDateInput label, .stTextInput label, 
.stRadio label, .stSelectbox label, 
.stNumberInput label {
    color: white !important;
    font-weight: 600 !important;
}

/* Headers */
h1, h2, h3, h4, h5, h6 {
    color: white !important;
    font-weight: 700 !important;
}

/* Inputs */
input, textarea {
    color: white !important;
    background-color: rgba(0,0,0,0.5) !important;
    border: 1px solid #ccc;
}

/* Buttons */
button[kind="primary"], .stButton > button {
    color: white !important;
    background-color: #00687a !important;
    border-radius: 6px;
    border: none;
    font-weight: 700 !important;
}

/* Ensure Quick Stats section is white */
[data-testid="stMetricLabel"], 
[data-testid="stMetricValue"] {
    color: white !important;
    font-weight: 700 !important;
}

/* Ensure radio group label (Choose input method) is white */
[data-testid="stRadio"] label, 
[data-testid="stRadio"] p {
    color: white !important;
    font-weight: 600 !important;
}
</style>
"""
st.markdown(white_text_css, unsafe_allow_html=True)


banner_color = "linear-gradient(90deg, #003366, #00687a)"
st.markdown(
    f"""
    <div style="background: {banner_color}; padding: 1.2em; border-radius: 10px; text-align:center;">
        <h1 style="color:white; margin:0;">🌡️ ParadeGuard</h1>
        <p style="color:#f1f1f1; font-size:18px; margin:0;">
            Predicting Heat Risk with NASA POWER Data
        </p>
    </div>
    <br>
    """,
    unsafe_allow_html=True
)


st.markdown("### 🔍 Enter Event Details")


if "lat" not in st.session_state:
    st.session_state.lat = None
    st.session_state.lon = None
    st.session_state.display_name = None

mode = st.radio("Choose input method:", ["City Name", "Latitude/Longitude"])

if mode == "City Name":
    city_input = st.text_input("📍 City", placeholder="e.g., New Delhi")

    def geocode_city(city: str):
        url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=en&format=json"
        try:
            r = requests.get(url, timeout=10).json()
            if "results" in r and len(r["results"]) > 0:
                loc = r["results"][0]
                return loc["latitude"], loc["longitude"], loc["name"]
        except:
            return None
        return None

    if st.button("🔍 Resolve Location"):
        if not city_input.strip():
            st.error("Please enter a valid city name.")
        elif len(city_input) > MAX_CITY_LENGTH:
            st.error("City name too long.")
        else:
            geo = geocode_city(city_input)
            if not geo:
                st.error("City not found in geocoding database.")
            else:
                st.session_state.lat, st.session_state.lon, st.session_state.display_name = geo
                st.success(
                    f"Resolved: {st.session_state.display_name} "
                    f"(lat={st.session_state.lat:.2f}, lon={st.session_state.lon:.2f})"
                )

else:  
    col1, col2 = st.columns(2)
    with col1:
        st.session_state.lat = st.number_input("Latitude", format="%.4f")
    with col2:
        st.session_state.lon = st.number_input("Longitude", format="%.4f")
    if st.session_state.lat and st.session_state.lon:
        st.session_state.display_name = f"Manual Location ({st.session_state.lat:.2f}, {st.session_state.lon:.2f})"
        st.success(f"Using coordinates: {st.session_state.display_name}")


c1, c2 = st.columns(2)
with c1:
    user_start = st.date_input("Start Date", date(2025, 6, 1))
with c2:
    user_end = st.date_input("End Date", date(2025, 7, 31))


def classify_pct(pct: float) -> str:
    if pct < 20.0:
        return "Low"
    if pct <= 50.0:
        return "Medium"
    return "High"

def fetch_nasa_url(url: str):
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            return r.json()
        return {"error": f"HTTP {r.status_code}"}
    except requests.RequestException:
        return {"error": "Network error"}

def build_df(data_dict: dict) -> pd.DataFrame:
    df = pd.DataFrame(list(data_dict.items()), columns=["date", "T2M_MAX"])
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["T2M_MAX"] = pd.to_numeric(df["T2M_MAX"], errors="coerce")
    df = df[df["T2M_MAX"].notna()]
    df = df[df["T2M_MAX"] != MISSING_FLAG]
    return df


if st.button("🚀 Check Heat Risk"):
    if not st.session_state.lat or not st.session_state.lon:
        st.error("No valid location selected. Please resolve city or enter lat/lon.")
    elif user_start > user_end:
        st.error("Start date must be before end date.")
    else:
        lat, lon = st.session_state.lat, st.session_state.lon
        st.info(f"Using coordinates: {lat:.2f}, {lon:.2f}")

        try:
            ten_years_start = user_start.replace(year=user_start.year - 10)
        except ValueError:
            if user_start.month == 2 and user_start.day == 29:
                ten_years_start = user_start.replace(year=user_start.year - 10, day=28)
            else:
                ten_years_start = user_start

        start_str = ten_years_start.strftime("%Y%m%d")
        end_str = user_end.strftime("%Y%m%d")

        url = (
            f"https://power.larc.nasa.gov/api/temporal/daily/point"
            f"?start={start_str}&end={end_str}&latitude={lat}&longitude={lon}"
            f"&community=SB&parameters=T2M_MAX&format=JSON"
        )

        with st.spinner("Fetching NASA POWER data..."):
            response = fetch_nasa_url(url)

        if "error" in response:
            st.error(f"NASA API error: {response['error']}")
        elif "properties" not in response:
            st.error("Unexpected NASA response format.")
        else:
            raw = response["properties"]["parameter"].get("T2M_MAX", {})
            df_all = build_df(raw)

            if df_all.empty:
                st.warning("No valid data available for this location and period.")
            else:
                
                start_md = (user_start.month, user_start.day)
                end_md = (user_end.month, user_end.day)

                def in_range(d):
                    md = (d.month, d.day)
                    if start_md <= end_md:
                        return start_md <= md <= end_md
                    else:
                        return md >= start_md or md <= end_md

                df_window = df_all[df_all["date"].apply(in_range)]

                if df_window.empty:
                    st.warning("No records matched the exact month-day window.")
                else:
                    hot_days = (df_window["T2M_MAX"] > 35).sum()
                    total_days = len(df_window)
                    pct = (hot_days / total_days) * 100
                    risk = classify_pct(pct)

                    now = datetime.now()
                    if user_end.year >= now.year:
                        st.info(f"Note: Data for {now.year} may be incomplete (only up to today).")

                    icon = "🟢" if risk=="Low" else "🟠" if risk=="Medium" else "🔴"
                    st.markdown(
                        f"<div style='padding:1em; background-color:{RISK_COLORS[risk]}; "
                        f"color:white; text-align:center; border-radius:8px; font-size:1.6em;'>"
                        f"{icon} Heat Risk: <b>{risk}</b> ({pct:.2f}% days > 35°C)"
                        "</div>",
                        unsafe_allow_html=True,
                    )

                    
                    df_window.set_index("date", inplace=True)
                    yearly_hot = df_window.resample("YE").apply(lambda x: (x["T2M_MAX"] > 35).sum())

                    fig, ax = plt.subplots(facecolor="black")
                    ax.plot(
                        yearly_hot.index.year,
                        yearly_hot.values,
                        marker="o",
                        color=THEME_COLOR,
                        linewidth=2,
                        label="Hot Days (>35°C)",
                    )
                    ax.set_xlabel("Year", color="white")
                    ax.set_ylabel("Number of Hot Days", color="white")
                    ax.set_title("Annual Hot Days in Selected Period", color="white")
                    ax.tick_params(colors="white")
                    ax.legend()

                    col_chart, col_stats = st.columns([3, 1])
                    with col_chart:
                        st.pyplot(fig)
                    with col_stats:
                        st.markdown("### 📊 Quick Stats")
                        st.metric("Total Days", total_days)
                        st.metric("Hot Days", int(hot_days))
                        st.metric("Risk %", f"{pct:.2f}%")

                    st.markdown(
                        """
                        <hr>
                        <div style="text-align:center; font-size:14px; color:white;">
                            Built with NASA POWER Data • Hackathon Edition 🌍🚀
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
