import pandas as pd
import matplotlib.pyplot as plt


try:
    df = pd.read_csv("heat_data.csv", skiprows=1, na_values=['***'])
except FileNotFoundError:
    print("ERROR: heat_data.csv not found. Did you download the correct L-OTI CSV and save it to the project folder?")
    exit()


df_clean = df[['Year', 'J-D']].copy()
df_clean.rename(columns={'J-D': 'Anomaly_C'}, inplace=True)


df_clean.dropna(inplace=True)


df_clean['Year'] = df_clean['Year'].astype(int)
df_filtered = df_clean[(df_clean['Year'] >= 1980) & (df_clean['Year'] <= 2023)].copy()

print(f"L-OTI Data successfully loaded and filtered. Total years: {len(df_filtered)}")
print(f"Data range: {df_filtered['Year'].min()} to {df_filtered['Year'].max()}")




LINE_COLOR = '#00687a' 

fig, ax = plt.subplots(figsize=(10, 6))

ax.plot(
    df_filtered['Year'], 
    df_filtered['Anomaly_C'],  
    color=LINE_COLOR, 
    linewidth=3, 
    marker='o', 
    markersize=5,
    label='L-OTI Anomaly'
)


ax.set_title(
    'Global Surface Temperature Anomaly (1980–2023)', 
    fontsize=16, 
    fontweight='bold', 
    color='black'
)
ax.set_xlabel('Year', fontsize=12)
ax.set_ylabel('Temperature Anomaly (°C)', fontsize=12) 


ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)
ax.grid(axis='y', linestyle='--', alpha=0.5)


min_val = df_filtered['Anomaly_C'].min()
max_val = df_filtered['Anomaly_C'].max()
ax.set_ylim(min(0, min_val - 0.05), max_val + 0.05) 

fig.patch.set_facecolor('#0a0a0a')      
ax.set_facecolor('#0a0a0a')             
ax.tick_params(colors='white')          
ax.yaxis.label.set_color('white')       
ax.xaxis.label.set_color('white')       
ax.title.set_color('white')             
ax.spines['left'].set_color('white')    
ax.spines['bottom'].set_color('white')
ax.grid(color='gray', linestyle='--', alpha=0.5)  


plt.savefig("need_graph_dark.png", dpi=300, bbox_inches='tight')

print("need_graph_dark.png saved successfully.")