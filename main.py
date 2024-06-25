import constants as consts
import environment_model as env_model
import images

import agentpy as ap
import matplotlib.pyplot as plt
# Reference: https://matplotlib.org/stable/api/_as_gen/matplotlib.patches.Rectangle.html
import matplotlib.patches as patches
import pandas as pd

import IPython
import tempfile
import webbrowser
import argparse
import datetime
import os
import json

AGENTS_CLASSES_PATCHES_MAPPING = {
    consts.ADULT_KEY: {"x": 1, "y": 1, "hatch": "///"},
    consts.EMPLOYEE_KEY: {"x": 1, "y": 1, "hatch": "ooo"},
    consts.ELDER_KEY: {"x": 0.9, "y": 0.9, "hatch": "***"},
    consts.CHILD_KEY: {"x": 0.7, "y": 0.7, "hatch": "..."},
    consts.LIM_MOB_KEY: {"x": 1, "y": 1, "hatch": "---"}
}

CHARACTERISTICS_COLOR_MAPPING = {
    "knows_exit_position": "lime",
    "high_panic_level": "red",
    "medium_panic_level": "yellow",
}

# Define colors for each unique type of agent
AGENT_COLOR_MAPPING = {
    "EmergencyExitSignAgent": "orange",
    "EmergencyExitAgent": "green",
    "ObstacleAgent": "gray",
    "PersonAgent": "cyan",
}

def animation_plot(model, ax):
  # The dictionary of agents
  agents_positions = {str(key): value for key, value in model.building.positions.items()}

  # Plot each agent
  for agent, (x, y) in agents_positions.items():
      agent_type = agent.split()[0]  # Get the type of agent
      color = AGENT_COLOR_MAPPING.get(agent_type, "grey")  # Get the color for this type of agent

      # Replace the (person) agent's color based on its own attributes/characteristics
      if agent_type == "PersonAgent":
        agent_obj = next(person for person in model.person_agents if str(person) == str(agent))
        agent_class = agent_obj.agent_class

        x_patch_pos = AGENTS_CLASSES_PATCHES_MAPPING[agent_class]["x"]
        y_patch_pos = AGENTS_CLASSES_PATCHES_MAPPING[agent_class]["y"]
        patch_hatch = AGENTS_CLASSES_PATCHES_MAPPING[agent_class]["hatch"]
        alpha = 0.7

        if agent_obj.panic_level >= 0.1 and agent_obj.panic_level < 0.2:
            color = CHARACTERISTICS_COLOR_MAPPING["medium_panic_level"]
        elif agent_obj.panic_level >= 0.2:
            color = CHARACTERISTICS_COLOR_MAPPING["high_panic_level"]
        if agent_obj.known_exit_position is not None:
            color = CHARACTERISTICS_COLOR_MAPPING["knows_exit_position"]
      else:
        x_patch_pos = 1
        y_patch_pos = 1
        patch_hatch = None
        alpha = 1

      ax.add_patch(patches.Rectangle((x, y), x_patch_pos, y_patch_pos, edgecolor='black', facecolor=color, hatch=patch_hatch, alpha=alpha))

  safe_adults = 0
  safe_employees = 0
  safe_children = 0
  safe_elder = 0
  safe_lim_mob = 0
  if model.t > 0:
    custom_data = model._simulation_data[model.t - 1]
    safe_adults = custom_data[consts.ADULT_KEY]
    safe_employees = custom_data[consts.EMPLOYEE_KEY]
    safe_children = custom_data[consts.CHILD_KEY]
    safe_elder = custom_data[consts.ELDER_KEY]
    safe_lim_mob = custom_data[consts.LIM_MOB_KEY]

  # Set the limits of the plot
  ax.set_xlim(0, 50)
  ax.set_ylim(0, 50)

  # Add grid
  ax.grid(True)

  # Add legend
  handles = [patches.Patch(color=color, label=agent_type) for agent_type, color in AGENT_COLOR_MAPPING.items()]
  ax.legend(handles=handles, bbox_to_anchor=(0.5, -0.25), loc='upper center')
  ax.set_title(f"Simulation of Evacuation | Time-step: {model.t}")

  color_code_string = f"Characteristics color code \n knows_exit_position : {CHARACTERISTICS_COLOR_MAPPING['knows_exit_position']}\n medium_panic_level: {CHARACTERISTICS_COLOR_MAPPING['medium_panic_level']}\n high_panic_level: {CHARACTERISTICS_COLOR_MAPPING['high_panic_level']}"

  # Add a textbox to the right of the plot
  characteristics_props = dict(boxstyle='round', facecolor='white', alpha=0.5)
  ax.text(1.02, 0.75, color_code_string, transform=ax.transAxes, fontsize=12, va='center', ha='left', bbox=characteristics_props)

  safe_people_props = dict(boxstyle='round', facecolor='white', alpha=0.5)
  safe_people_string = f"Number of safe people\n" + \
  f"Adults ({AGENTS_CLASSES_PATCHES_MAPPING[consts.ADULT_KEY]['hatch'][0]}): {safe_adults}\n" + \
  f"Employees({AGENTS_CLASSES_PATCHES_MAPPING[consts.EMPLOYEE_KEY]['hatch'][0]}): {safe_employees}\n" + \
  f"Children({AGENTS_CLASSES_PATCHES_MAPPING[consts.CHILD_KEY]['hatch'][0]}): {safe_children}\n" + \
  f"Elders({AGENTS_CLASSES_PATCHES_MAPPING[consts.ELDER_KEY]['hatch'][0]}): {safe_elder}\n" + \
  f"Lim mobility({AGENTS_CLASSES_PATCHES_MAPPING[consts.LIM_MOB_KEY]['hatch'][0]}): {safe_lim_mob}"

  ax.text(1.02, 0.5, safe_people_string, transform=ax.transAxes, fontsize=12, va='center', ha='left', bbox=safe_people_props)

  ax.set_aspect('equal', adjustable='box')


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('--wo_animation', action='store_true', help='Enable animation', default=False)

    args = parser.parse_args()

    print("Building evacuation simulation")
    parameters = {
    'n_agents': 20,
    'adults_percentage': 0.5,
    'employee_percentage': 0.1,
    'child_percentage': 0.2,
    'elder_percentage': 0.1,
    'limited_mobility_percentage': 0.1,
    'random_obstacles_percentage': 0.05, # Based on the amount of free grids
    'floorplan_filepath': 'environments/floorplan_four_exits.txt',
    'strategy': 'every_man_for_himself',
    'steps': 2,
    }

    timestamp_string = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
    folder_name = f"{consts.ARTIFACTS_FOLDER}/{timestamp_string}_run"
    parameter_json_filename = f"{folder_name}/parameters.json"
    html_filename = f"{folder_name}/simulation_animation.html"
    csv_filename = f"{folder_name}/simulation_data.csv"

    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

    with open(parameter_json_filename, 'w') as json_file:
        json.dump(parameters, json_file, indent=4)

    model = env_model.BuildingEvacuationModel(parameters)

    if args.wo_animation:
        results = model.run(seed=42, display=True)
        json_data = results[consts.CUSTOM_RECORD_KEY]
        df = pd.DataFrame(json_data)
        df.to_csv(csv_filename)

        images.generate_saved_agents_plot(df, folder_name, parameters)

        print(f"Results = {results}")
    else:
        fig, ax = plt.subplots(figsize=(15, 10))
        animation = ap.animate(model, fig, ax, animation_plot)

        n_of_emergency_exits = int(len(model.emergency_exit) / 2)
        n_of_emergency_exit_signs = len(model.emergency_exit_sign)
        parameters['n_of_emergency_exits'] = n_of_emergency_exits
        parameters['n_of_emergency_exit_signs'] = n_of_emergency_exit_signs

        # Assume `animation` is your animation object
        html_content = IPython.display.HTML(animation.to_jshtml(fps=5)).data

        with open(html_filename, 'w') as html_file:
            html_file.write(html_content)

        json_data = model._simulation_data
        df = pd.DataFrame(json_data)
        df.to_csv(csv_filename)

        images.generate_saved_agents_plot(df, folder_name, parameters)

    print(f"The simulation artifacts are saved in {folder_name} folder")

if __name__ == "__main__":
    main()
