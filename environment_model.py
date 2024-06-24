"""This file contains the environment model for the building evacuation simulation"""

import os
import agents

import agentpy as ap
import numpy as np

import constants as consts


class BuildingEvacuationModel(ap.Model):
  def __load_floorplan_file(self, filepath):
    with open(os.path.join("", filepath), "rt") as f:
      floorplan = np.matrix([line.strip().split() for line in f.readlines()])

    # Rotate the floorplan so it's interpreted as seen in the text file
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
    floorplan = self.__load_floorplan_file(filepath)
    width, height = np.shape(floorplan)
    environment_info = {
        consts.WALL_KEY: self.__get_positions_from_floorplan(consts.WALL_KEY, floorplan),
        consts.EXIT_KEY: self.__get_positions_from_floorplan(consts.EXIT_KEY, floorplan),
        consts.SIGN_KEY: self.__get_positions_from_floorplan(consts.SIGN_KEY, floorplan),
        consts.WIDTH_KEY: width,
        consts.HEIGHT_KEY: height
    }

    return environment_info

  def setup(self):
    # Called at the start of the simulation

    # Used to record data
    self._simulation_data = []

    environment_info = self.__get_environment_info_from_file(self.p.floorplan_filepath)

    # Global values
    width = environment_info[consts.WIDTH_KEY]
    height = environment_info[consts.HEIGHT_KEY]

    # Create grid (building)
    # The building will be represented as a one floor thas specified width and height
    self.building = ap.Grid(self, [width, height], track_empty=True)

    # Place the emergency exit signs
    n_emergency_exit_signs = len(environment_info[consts.SIGN_KEY])
    self.emergency_exit_sign = ap.AgentList(self, n_emergency_exit_signs, agents.EmergencyExitSignAgent)
    self.building.add_agents(self.emergency_exit_sign, positions=environment_info[consts.SIGN_KEY])
    self.emergency_exit_sign.setup_nearests_exits(environment_info[consts.EXIT_KEY], self.building)

    # Place the emergency exits
    n_of_emergency_exits = len(environment_info[consts.EXIT_KEY])
    self.emergency_exit = ap.AgentList(self, n_of_emergency_exits, agents.EmergencyExitAgent)
    self.building.add_agents(self.emergency_exit, positions=environment_info[consts.EXIT_KEY])

    # Place the obstacles
    number_of_obstacles = len(environment_info[consts.WALL_KEY])
    self.objects = ap.AgentList(self, number_of_obstacles, agents.ObstacleAgent)
    self.building.add_agents(self.objects, positions=environment_info[consts.WALL_KEY])

    # TODO: Validar se a porcentagem de agentes é igual a 100%
    # TODO: Validar se o numero de agentes é igual ao numero total

    # Place the agents
    number_of_person_agents = self.p.n_agents
    number_of_agents_per_class = {
      consts.ADULT_KEY: int(self.p.adults_percentage * number_of_person_agents),
      consts.EMPLOYEE_KEY: int(self.p.employee_percentage * number_of_person_agents),
      consts.CHILD_KEY: int(self.p.child_percentage * number_of_person_agents),
      consts.ELDER_KEY: int(self.p.elder_percentage * number_of_person_agents),
      consts.LIM_MOB_KEY: int(self.p.limited_mobility_percentage * number_of_person_agents)
    }

    self.person_agents = ap.AgentList(self)

    if number_of_person_agents == 1:
      # Used to debug
      person_agent = ap.AgentList(self, number_of_person_agents, agents.PersonAgent)
      person_agent.setup_characteristics(consts.EMPLOYEE_KEY, environment_info[consts.EXIT_KEY])
      self.person_agents = self.person_agents.__add__(person_agent)
      self.building.add_agents(self.person_agents, positions=[(20, 3)], empty=True)
    else:
      for agent_class, n_of_agents in number_of_agents_per_class.items():
        print(f"Setting up {n_of_agents} {agent_class} agents..")
        current_agents_class = ap.AgentList(self, n_of_agents, agents.PersonAgent)
        current_agents_class.setup_characteristics(agent_class, environment_info[consts.EXIT_KEY])

        self.person_agents = self.person_agents.__add__(current_agents_class)

      self.building.add_agents(self.person_agents, random=True, empty=True)
    self.person_agents.setup_position(self.building)


  def __compute_safe_agents_class(self, agent_class):
    return sum(exit.safe_agents_dict.get(agent_class, 0) for exit in self.emergency_exit)


  def step(self):
    # Called at every simulation step
    self.person_agents.evacuate(self.building)
    self.emergency_exit.allow_people(self.building)

    step_record_dict = {
      consts.STEP_KEY: self.t,
      consts.ADULT_KEY: self.__compute_safe_agents_class(consts.ADULT_KEY),
      consts.CHILD_KEY: self.__compute_safe_agents_class(consts.CHILD_KEY),
      consts.LIM_MOB_KEY: self.__compute_safe_agents_class(consts.LIM_MOB_KEY),
      consts.ELDER_KEY: self.__compute_safe_agents_class(consts.ELDER_KEY),
      consts.EMPLOYEE_KEY: self.__compute_safe_agents_class(consts.EMPLOYEE_KEY)
    }

    self._simulation_data.append(step_record_dict)

    # TODO: Adicionar checagem de condição final
    # Se a quantidade de pessoas salvas é igual ao total de agentes

  def update(self):
    # Called after setup as well as after each step
    # Normally used to record variables
    pass


  def end(self):
    # Called at the end of the simulation
    self.output[consts.CUSTOM_RECORD_KEY] = self._simulation_data
