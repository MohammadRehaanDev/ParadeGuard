
import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
from datetime import date, datetime
import time


THEME_COLOR = "#00687a"  
RISK_COLORS = {
    "Low": "#2ecc71",    
    "Medium": "#f39c12", 
    "High": "#e74c3c"    
}
MISSING_FLAG = -999.0
MAX_CITY_LENGTH = 100

st.set_page_config(page_title="ParadeGuard", layout="centered")
st.title("ParadeGuard — Heat Risk (10-year historical window)")


st.markdown(
    "**Classification rules:** Low = *< 20%*, Medium = *≥ 20% and ≤ 50%*, High = *> 50%*"
)


city_input = st.text_input("Enter city name (e.g., New Delhi):")
col1, col2 = st.columns(2)
with col1:
    user_start = st.date_input("Start date", date(2025, 6, 1))
with col2:
    user_end = st.date_input("End date", date(2025, 7, 31))

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

if st.button("Check Heat Risk"):
    
    if not city_input.strip():
        st.error("Please enter a city name.")
    elif len(city_input) > MAX_CITY_LENGTH:  
        st.error("City name too long. Please enter a shorter name.")
    elif user_start > user_end:
        st.error("Start date must be before end date.")
    else:
        
        try:
            geolocator = Nominatim(user_agent="parade_guard_app", timeout=10)
            location = geolocator.geocode(city_input)
        except (GeocoderTimedOut, GeocoderServiceError):
            location = None

        if not location:
            st.error("City not found or geocoding service unavailable.")
        else:
            lat, lon = location.latitude, location.longitude
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

                        
                        st.markdown(
                            f"<div style='padding:1em; background-color:{RISK_COLORS[risk]}; "
                            f"color:white; text-align:center; border-radius:8px; font-size:1.5em;'>"
                            f"Heat Risk: {risk} ({pct:.2f}% of days > 35°C)"
                            "</div>",
                            unsafe_allow_html=True,
                        )

                        
                        df_window.set_index("date", inplace=True)
                        yearly_hot = df_window.resample("YE").apply(lambda x: (x["T2M_MAX"] > 35).sum())

                        fig, ax = plt.subplots()
                        ax.plot(
                            yearly_hot.index.year,
                            yearly_hot.values,
                            marker="o",
                            color=THEME_COLOR,
                            linewidth=2,
                            label="Hot Days (>35°C)",
                        )
                        ax.set_xlabel("Year")
                        ax.set_ylabel("Number of Hot Days")
                        ax.set_title("Annual Hot Days in Selected Period")
                        ax.legend()

                        
                        st.caption(
                            "Note: NASA POWER data is global and may include interpolated values in remote or ocean regions. "
                            "Interpret such locations with caution."
                        )

                        st.pyplot(fig)
