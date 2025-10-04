import streamlit as st
import requests
import pandas as pd

st.title("Hello, ParadeGuard!")

url = "https://power.larc.nasa.gov/api/temporal/daily/point?start=20240101&end=20250101&latitude=28.6&longitude=77.2&community=SB&parameters=T2M_MAX&format=JSON"
response = requests.get(url).json()


data = response['properties']['parameter']['T2M_MAX']
df = pd.DataFrame(list(data.items()), columns=["date", "T2M_MAX"])
df["date"] = pd.to_datetime(df["date"])

st.write(df.head())


def calculate_risk(df, threshold=35):
    hot_days = (df["T2M_MAX"] > threshold).sum()
    total_days = len(df)
    pct = (hot_days / total_days) * 100
    if pct < 20:
        return "Low", pct
    elif pct <= 50:
        return "Medium", pct
    else:
        return "High", pct

risk, pct = calculate_risk(df)
st.subheader(f"Heat Risk: {risk}")
st.write(f"Percentage of days > 35°C: {pct:.2f}%")

import matplotlib.pyplot as plt

df.set_index("date", inplace=True)


yearly_hot_days = df.resample("Y").apply(lambda x: (x["T2M_MAX"] > 35).sum())

fig, ax = plt.subplots()
ax.plot(yearly_hot_days.index.year, yearly_hot_days.values, marker="o", color="orange", label="Hot Days > 35°C")
ax.axhline(y=35, color="red", linestyle="--", label="Threshold (35°C)")
ax.set_xlabel("Year")
ax.set_ylabel("Number of Hot Days")
ax.set_title("Annual Hot Days (>35°C)")
ax.legend()

st.pyplot(fig)


