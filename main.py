import constants as consts
import environment_model as env_model

import agentpy as ap
import matplotlib.pyplot as plt
# Reference: https://matplotlib.org/stable/api/_as_gen/matplotlib.patches.Rectangle.html
import matplotlib.patches as patches

import IPython
import tempfile
import webbrowser
import argparse

AGENTS_CLASSES_PATCHES_MAPPING = {
    "adult": {"x": 1, "y": 1, "hatch": "///"},
    "employee": {"x": 1, "y": 1, "hatch": "ooo"},
    "elder": {"x": 0.9, "y": 0.9, "hatch": "***"},
    "child": {"x": 0.7, "y": 0.7, "hatch": "..."},
    "limited_mobility": {"x": 1, "y": 1, "hatch": "---"}
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

      ax.add_patch(patches.Rectangle((x, y), x_patch_pos, y_patch_pos, edgecolor='black', facecolor=color, hatch=patch_hatch))

  # Set the limits of the plot
  ax.set_xlim(0, 50)
  ax.set_ylim(0, 50)

  # Add grid
  ax.grid(True)

  # Add legend
  handles = [patches.Patch(color=color, label=agent_type) for agent_type, color in AGENT_COLOR_MAPPING.items()]
  ax.legend(handles=handles, bbox_to_anchor=(0.5, -0.25), loc='upper center')
  ax.set_title(f"Simulation of Evacuation \n"
               f"Time-step: {model.t}")
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
    'steps': 50,
    'floorplan_filepath': 'floorplan_fixed_signs.txt'
    }

    model = env_model.BuildingEvacuationModel(parameters)

    if args.wo_animation:
        results = model.run(seed=42, display=True)
        print(f"Results = {results}")
    else:
        fig, ax = plt.subplots(figsize=(10, 10))
        animation = ap.animate(model, fig, ax, animation_plot)

        # Assume `animation` is your animation object
        html_content = IPython.display.HTML(animation.to_jshtml(fps=5)).data

        # Create a temporary HTML file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.html') as temp_file:
            temp_file.write(html_content.encode('utf-8'))
            temp_file_path = temp_file.name

        webbrowser.open(f'file://{temp_file_path}')

if __name__ == "__main__":
    main()
