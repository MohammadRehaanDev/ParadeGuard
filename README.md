# 🌡️ ParadeGuard

ParadeGuard is a **Streamlit web app** that helps event organizers, communities, and researchers **predict climate risks** (Heat, Rainfall, and Humidity) for outdoor events using **NASA POWER API data**.

Built for hackathons and real-world use, it provides a simple UI to enter a city or coordinates, select event dates, and visualize climate risks over the past 10 years.

---

## 🚀 Live Demo

👉 [Launch ParadeGuard on Streamlit Cloud](https://paradeguard.streamlit.app)

---

## ✨ Features

- 🌍 **Location Search**: Enter a city name (via Open-Meteo Geocoding API) or manually input latitude/longitude.  
- 📅 **Flexible Date Selection**: Choose start and end dates for your event. The app automatically analyzes the last 10 years of data for that date window.  
- 🔥 **Heat Risk Analysis**: Percentage of days with max temperature above **35°C**.  
- 🌧️ **Rainfall Risk Analysis**: Percentage of days with rainfall above **10 mm/day**.  
- 💧 **Humidity Risk Analysis**: Percentage of days with relative humidity above **80%**.  
- 📊 **Risk Levels**: Categorized as **Low / Medium / High** with color-coded banners.  
- 📈 **Visualization**: Line plots showing annual risk days for the past decade.  
- ⚡ **Fast and Interactive**: Powered by Streamlit, pandas, and matplotlib.  
- 🎨 **Polished UI**: Custom CSS, banners, white text, and consistent styling for a hackathon-ready look.  

---

## 🛠️ Tech Stack

- [Streamlit](https://streamlit.io/) — for the interactive app  
- [NASA POWER API](https://power.larc.nasa.gov/) — for climate datasets  
- [Open-Meteo Geocoding API](https://open-meteo.com/) — for city → coordinates  
- [pandas](https://pandas.pydata.org/) — data handling  
- [matplotlib](https://matplotlib.org/) — charting  

---

## 📂 Project Structure
```
ParadeGuard/
│
├── assets/
├── data/
├── scripts/
├── .gitignore
├── LICENSE
├── README.md
├── app.py
├── background.jpg
└── requirements.txt
```

---

## ⚙️ Installation & Local Run

Clone this repo and install dependencies:

```bash
git clone https://github.com/MohammadRehaanDev/ParadeGuard.git
cd ParadeGuard
pip install -r requirements.txt

Run the app locally:

streamlit run app.py

📦 Requirements

Contents of requirements.txt:

streamlit
requests
pandas
matplotlib

📊 Risk Classification
Risk	Condition	Low	Medium	High
Heat Risk	T2M_MAX > 35°C	< 20% of days	20–50%	> 50%
Rainfall Risk	PRECTOTCORR > 10 mm/day	< 20% of days	20–40%	> 40%
Humidity Risk	RH2M > 80%	< 40% of days	40–70%	> 70%
🙌 Acknowledgments

    NASA POWER Project for providing open climate data

    Open-Meteo for the geocoding API

    Streamlit community for making rapid prototyping possible

    Hackathon organizers for the challenge 🚀

📜 License

This project is licensed under the MIT License. See LICENSE for details.
