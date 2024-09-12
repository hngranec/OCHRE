import datetime as dt

from ochre import Dwelling, CreateFigures
from ochre.Models import TankWithPCM
from bin.run_dwelling import dwelling_args

pcm_water_node = 5
pcm_vol_fraction = 0.2


dwelling_args.update(
    {
        "time_res": dt.timedelta(minutes=1),  # time resolution of the simulation
        "duration": dt.timedelta(days=1),  # duration of the simulation
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


def run_water_heater(dwelling_args, plot_title):
    # Create Dwelling from input files, see bin/run_dwelling.py
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

    # print(df.head())
    CreateFigures.plot_time_series_detailed((df["Hot Water Outlet Temperature (C)"],))
    CreateFigures.plt.title(plot_title)
    CreateFigures.plt.show()


if __name__ == '__main__':
    #run without PCM
    run_water_heater(dwelling_args, "No PCM \n PCM Water Node:"+ str(pcm_water_node) +"\n PCM Vol Fraction:" +str(pcm_vol_fraction))

    #update to include PCM
    dwelling_args = add_pcm_model(dwelling_args)
    
    #Run with PCM
    run_water_heater(dwelling_args, "With PCM \n PCM Water Node:"+ str(pcm_water_node) +"\n PCM Vol Fraction:" +str(pcm_vol_fraction))
