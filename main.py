import environment_model as env_model

import agentpy as ap
import matplotlib.pyplot as plt
import matplotlib.patches as patches

import IPython
import tempfile
import webbrowser

def animation_plot(model, ax):
  # The dictionary of agents
  agents_positions = {str(key): value for key, value in model.building.positions.items()}

  # Define colors for each unique type of agent
  AGENT_COLOR_MAPPING = {
      "EmergencyExitSignAgent": "orange",
      "EmergencyExitAgent": "green",
      "ObstacleAgent": "gray",
      "PersonAgent": "blue",
  }

  # Plot each agent
  for agent, (x, y) in agents_positions.items():
      agent_type = agent.split()[0]  # Get the type of agent
      color = AGENT_COLOR_MAPPING.get(agent_type, "grey")  # Get the color for this type of agent
      ax.add_patch(patches.Rectangle((x, y), 1, 1, edgecolor='black', facecolor=color))

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
    print("Building evacuation simulation")
    parameters = {
    'n_agents': 20,
    'adults_percentage': 0.1,
    'employee_percentage': 0.2,
    'child_percentage': 0.3,
    'elder_percentage': 0.2,
    'limited_mobility_percentage': 0.2,
    'n_emergency_exit_signs': 2,
    'steps': 20,
    'floorplan_filepath': 'floorplan_fixed.txt'
    }

    model = env_model.BuildingEvacuationModel(parameters)
    fig, ax = plt.subplots(figsize=(10, 10))
    animation = ap.animate(model, fig, ax, animation_plot)

    # Assume `animation` is your animation object
    html_content = IPython.display.HTML(animation.to_jshtml(fps=5)).data

    # Create a temporary HTML file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.html') as temp_file:
        temp_file.write(html_content.encode('utf-8'))
        temp_file_path = temp_file.name

    webbrowser.open(f'file://{temp_file_path}')

    #results = model.run(seed=42)

if __name__ == "__main__":
    main()
