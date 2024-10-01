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
pcm_vol_fraction = 0.5
LowUseUEF = 'LowUseL.csv'
MediumUseUEF = 'MediumUseL.csv'
HighUseUEF = 'HighUseL.csv'

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

def run_water_heater(dwelling_args,load_profile):
    # Create Dwelling from input files
    dwelling = Dwelling(**dwelling_args)

    # Extract equipment by its end use and update simulation properties
    equipment = dwelling.get_equipment_by_end_use("Water Heating")
    equipment.main_simulator = True
    equipment.save_results = dwelling.save_results
    equipment.export_res = dwelling.export_res
    equipment.results_file = dwelling.results_file

    # If necessary, update equipment schedule
    equipment.model.schedule['Zone Temperature (C)'] = 19.722222 #from the UEF standard https://www.energy.gov/eere/buildings/articles/2014-06-27-issuance-test-procedures-residential-and-commercial-water
    equipment.model.schedule['Water Use Schedule (L/min)'] = load_profile #converted the schedule files directly to L/min
    equipment.model.schedule['Mains Temperature (C)'] = 14.4444
    equipment.reset_time()

    # Simulate equipment
    df = equipment.simulate()
    
    return df

def plot_comparison(df_no_pcm_MediumUse,df_no_pcm_LowUse,df_no_pcm_HighUse,df_with_pcm_MediumUse,df_with_pcm_LowUse,df_with_pcm_HighUse):
    CreateFigures.plt.figure(figsize=(12, 8))
    
    # Plot without PCM
    CreateFigures.plt.plot(df_no_pcm_MediumUse.index, df_no_pcm_MediumUse["Hot Water Outlet Temperature (C)"], label="No PCM,Medium Use", color='blue',linestyle='-')
    CreateFigures.plt.plot(df_no_pcm_LowUse.index, df_no_pcm_LowUse["Hot Water Outlet Temperature (C)"], label="No PCM,Low Use", color='blue',linestyle='--')
    CreateFigures.plt.plot(df_no_pcm_HighUse.index, df_no_pcm_HighUse["Hot Water Outlet Temperature (C)"], label="No PCM,High Use", color='blue',linestyle=':')
    # Plot with PCM
    CreateFigures.plt.plot(df_with_pcm_MediumUse.index, df_with_pcm_MediumUse["Hot Water Outlet Temperature (C)"], label="With PCM,Medium Use", color='red',linestyle='-')
    CreateFigures.plt.plot(df_with_pcm_LowUse.index, df_with_pcm_LowUse["Hot Water Outlet Temperature (C)"], label="With PCM,Low Use", color='red',linestyle='--')
    CreateFigures.plt.plot(df_with_pcm_HighUse.index, df_with_pcm_HighUse["Hot Water Outlet Temperature (C)"], label="With PCM,High Use", color='red',linestyle=':')
    # Set plot labels and title
    CreateFigures.plt.xlabel("Time")
    CreateFigures.plt.ylabel("Temperature (°C)")
    CreateFigures.plt.title("Comparison of Hot Water Outlet Temperature\n PCM Water Node:"+ str(pcm_water_node) +"\n PCM Vol Fraction:" +str(pcm_vol_fraction))
    CreateFigures.plt.legend()
    CreateFigures.plt.grid(True)
    CreateFigures.plt.show()

if __name__ == '__main__':
    # Run simulation without PCM
    df_no_pcm_MediumUse = run_water_heater(dwelling_args,MediumUseUEF)
    df_no_pcm_LowUse = run_water_heater(dwelling_args,LowUseUEF)
    df_no_pcm_HighUse = run_water_heater(dwelling_args,HighUseUEF)

    # Update to include PCM
    dwelling_args_with_pcm = add_pcm_model(dwelling_args.copy())
    
    # Run simulation with PCM
    df_with_pcm_MediumUse = run_water_heater(dwelling_args_with_pcm,MediumUseUEF)
    df_with_pcm_LowUse = run_water_heater(dwelling_args_with_pcm,LowUseUEF)
    df_with_pcm_HighUse = run_water_heater(dwelling_args_with_pcm,HighUseUEF)

    # Plot comparison
    plot_comparison(df_no_pcm_MediumUse,df_no_pcm_LowUse,df_no_pcm_HighUse,df_with_pcm_MediumUse,df_with_pcm_LowUse,df_with_pcm_HighUse)
