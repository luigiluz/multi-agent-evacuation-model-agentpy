"""This file contains the environment model for the building evacuation simulation"""

import os
import agents

import agentpy as ap
import numpy as np

# E.g,: The total number of points is equal to width * height
## Let's say width = 10 and height = 10, there will be 100 available points
## If ObjectDensity is equal to 0.1, there will be 10 points with objects
## This will leave us with 100 - 0.1*100 = 90 available points
## Let's say PopulationDensity is equal to 0.5, there will be 0.5*90 = 45 agents
## spread in the available 90 points

class BuildingEvacuationModel(ap.Model):
  def __load_floorplan_file(self, filepath):
    with open(os.path.join("", filepath), "rt") as f:
      floorplan = np.matrix([line.strip().split() for line in f.readlines()])

    # Rotatethe floorplan so it's interpreted as seen in the text file
    floorplan = np.rot90(floorplan, 3)

    return floorplan

  def __get_positions_from_floorplan(self, item, floorplan):
    pos_typle_of_arrays = np.where(floorplan == item)
    x_position, y_position = pos_typle_of_arrays

    # Convert the numpy arrays to lists
    x_position_list = x_position.tolist()
    y_position_list = y_position.tolist()

    # Combine the lists into a list of tuples
    positions = list(zip(x_position_list, y_position_list))

    return positions

  def __get_environment_info_from_file(self, filepath):
    # W -> Parede
    # E -> Saida
    # S -> Sign
    floorplan = self.__load_floorplan_file(filepath)
    width, height = np.shape(floorplan)
    environment_info = {
        'W': self.__get_positions_from_floorplan('W', floorplan),
        'E': self.__get_positions_from_floorplan('E', floorplan),
        'S': self.__get_positions_from_floorplan('S', floorplan),
        'width': width,
        'height': height
    }

    return environment_info

  def setup(self):
    # Called at the start of the simulation

    environment_info = self.__get_environment_info_from_file(self.p.floorplan_filepath)

    # Global values
    width = environment_info['width']
    height = environment_info['height']

    # Create grid (building)
    # The building will be represented as a one floor thas specified width and height
    self.building = ap.Grid(self, [width, height], track_empty=True)

    # Place the emergency exit signs
    n_emergency_exit_signs = len(environment_info['S'])
    self.emergency_exit_sign = ap.AgentList(self, n_emergency_exit_signs, agents.EmergencyExitSignAgent)
    self.building.add_agents(self.emergency_exit_sign, positions=environment_info['S'])
    self.emergency_exit_sign.setup_nearests_exits(environment_info['E'], self.building)

    # Place the emergency exits
    # TODO: Pensar numa logica de posicionar os alarmes de incendio
    n_of_emergency_exits = len(environment_info['E'])
    self.emergency_exit = ap.AgentList(self, n_of_emergency_exits, agents.EmergencyExitAgent)
    self.building.add_agents(self.emergency_exit, positions=environment_info['E'])
    # Solução possível:
    # Posso passar a posição de todas as saídas de emergência para as placas
    # Dentro das placas ele computa a distância e escolhe qual é a melhor

    # Place the obstacles
    number_of_obstacles = len(environment_info['W'])
    print(f"Number of obstacles = {number_of_obstacles}")
    self.objects = ap.AgentList(self, number_of_obstacles, agents.ObstacleAgent)
    self.building.add_agents(self.objects, positions=environment_info['W'])

    # Place the agents
    # TODO: Receber o numero de agentes como entrada da simulação
    # TODO: Depois evoluir para definir a quantidade de pessoas de cada classe
    number_of_person_agents = self.p.n_agents
    print(f"Number of agents = {number_of_person_agents}")
    self.person_agents = ap.AgentList(self, number_of_person_agents, agents.PersonAgent)
    self.building.add_agents(self.person_agents, random=True, empty=True)


  def step(self):
    # Called at every simulation step
    self.emergency_exit_sign.inform_nearest_emergency_exit(self.building)
    self.person_agents.evacuate(self.building)
    self.emergency_exit.allow_people(self.building)

    # Check if the stop criteria was met
    # The stop criteria would be all people saved

  def update(self):
    # Called after setup as well as after each step
    # Normally used to record variables
    pass


  def end(self):
    # Called at the end of the simulation
    pass
