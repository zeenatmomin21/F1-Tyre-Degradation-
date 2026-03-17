

import fastf1
import pandas as pd
import matplotlib.pyplot as plt
import os

# 1. Setup & Folders
# if not os.path.exists('Cache_dir'):
#     os.makedirs('Cache_dir')

fastf1.Cache.enable_cache('Cache_dir') 

# 2. Load Session Data
session = fastf1.get_session(2023, 'Silverstone', 'R')
session.load()

# 3. Filter for Hamilton's "Push Laps"
laps = session.laps.pick_drivers('HAM').pick_quicklaps()

# 4. Logic to calculate your "Stint Delta"
def analyze_stints(df):
    results = []
    # Estimated time gain per lap from fuel burn (adjust based on track)
    fuel_burn_cost = 0.035 

    for stint_id, stint_data in df.groupby('Stint'):
        first_lap_time = stint_data.iloc[0]['LapTime'].total_seconds()
        
        # 1. Calculate raw delta
        stint_data['Raw_Delta'] = stint_data['LapTime'].dt.total_seconds() - first_lap_time
        
        # 2. Add back the fuel effect (Fuel Correction)
        # We multiply the cost by the current lap number to 'penalize' later laps
        stint_data['Stint_Delta'] = stint_data['Raw_Delta'] + (stint_data['LapNumber'] * fuel_burn_cost)
        
        results.append(stint_data)
    
    return pd.concat(results)

# Execute the analysis
processed_laps = analyze_stints(laps)

# 5. Define Colors for the Graph (Fixed the NameError here)
compound_colors = {
    'SOFT': '#FF3333',   # Red
    'MEDIUM': '#FFFF33', # Yellow
    'HARD': '#F0F0F0',   # White
}

# 6. Visualization
plt.figure(figsize=(10, 6), facecolor='#1e1e1e') # Dark background like F1 TV
ax = plt.axes()
ax.set_facecolor('#1e1e1e')

for stint_id, stint_data in processed_laps.groupby('Stint'):
    compound = stint_data['Compound'].iloc[0]
    color = compound_colors.get(compound, 'grey')
    
    plt.plot(
        stint_data['TyreLife'], 
        stint_data['Stint_Delta'], 
        label=f'Stint {stint_id} ({compound})', 
        color=color, 
        marker='o',
        linewidth=2
    )

# Formatting
plt.title("Tyre Degradation: Hamilton - Silverstone 2023", color='white', fontsize=14)
plt.xlabel("Tyre Age (Laps)", color='white')
plt.ylabel("Pace Loss (Seconds vs Lap 1)", color='white')
plt.xticks(color='white')
plt.yticks(color='white')
plt.grid(True, linestyle='--', alpha=0.3)
plt.legend()

plt.show()