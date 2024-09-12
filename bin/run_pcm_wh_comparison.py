# -*- coding: utf-8 -*-
"""
Created on Thu Sep 12 13:10:39 2024

@author: halgr
"""

import datetime as dt
import matplotlib.pyplot as plt  # Ensure matplotlib is imported

from ochre import Dwelling, CreateFigures
from ochre.Models import TankWithPCM
from bin.run_dwelling import dwelling_args

pcm_water_node = 5
pcm_vol_fraction = 0.2

dwelling_args.update(
    {
        "time_res": dt.timedelta(minutes=1),  # Time resolution of the simulation
        "duration": dt.timedelta(days=1),  # Duration of the simulation
        "verbosity": 9,
    }
)

def add_pcm_model(dwelling_args):
    dwelling_args["Equipment"]["Water Heating"] = {
        "model_class": TankWithPCM,
        "Water Tank": {
            "pcm_water_node": pcm_water_node,
            "pcm_vol_fraction": pcm_vol_fraction,
        },
    }
    return dwelling_args

def run_water_heater(dwelling_args):
    # Create Dwelling from input files
    dwelling = Dwelling(**dwelling_args)

    # Extract equipment by its end use and update simulation properties
    equipment = dwelling.get_equipment_by_end_use("Water Heating")
    equipment.main_simulator = True
    equipment.save_results = dwelling.save_results
    equipment.export_res = dwelling.export_res
    equipment.results_file = dwelling.results_file

    # If necessary, update equipment schedule
    equipment.model.schedule['Zone Temperature (C)'] = 20
    equipment.reset_time()

    # Simulate equipment
    df = equipment.simulate()
    
    return df

def plot_comparison(df_no_pcm, df_with_pcm):
    plt.figure(figsize=(12, 8))
    
    # Plot without PCM
    plt.plot(df_no_pcm.index, df_no_pcm["Hot Water Outlet Temperature (C)"], label="No PCM", color='blue')
    
    # Plot with PCM
    plt.plot(df_with_pcm.index, df_with_pcm["Hot Water Outlet Temperature (C)"], label="With PCM", color='red')
    
    # Set plot labels and title
    plt.xlabel("Time")
    plt.ylabel("Temperature (°C)")
    plt.title("Comparison of Hot Water Outlet Temperature")
    plt.legend()
    plt.grid(True)
    plt.show()

if __name__ == '__main__':
    # Run simulation without PCM
    df_no_pcm = run_water_heater(dwelling_args)

    # Update to include PCM
    dwelling_args_with_pcm = add_pcm_model(dwelling_args.copy())
    
    # Run simulation with PCM
    df_with_pcm = run_water_heater(dwelling_args_with_pcm)

    # Plot comparison
    plot_comparison(df_no_pcm, df_with_pcm)
