import agents
import environment_model as env_model

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
    results = model.run(seed=42)

if __name__ == "__main__":
    main()
