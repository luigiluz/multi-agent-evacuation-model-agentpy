""" This file contains the agents for the building evacuation simulation"""

import random
import utils
import search

import constants as consts
import agentpy as ap

class ObstacleAgent(ap.Agent):
  def setup(self):
    pass

  def agent_method(self):
    # This agent has no action, it only stays in its position
    pass


class EmergencyExitSignAgent(ap.Agent):
  def setup(self):
    pass

  def setup_nearests_exits(self, emergency_exit_positions, grid):
    current_position = grid.positions[self]
    best_distance = float('inf')

    for emergency_exit_position in emergency_exit_positions:
      current_distance = utils.manhattan_distance(emergency_exit_position, current_position)
      if current_distance < best_distance:
        self.nearest_emergency_exit = emergency_exit_position
        best_distance = current_distance


  # def inform_nearest_emergency_exit(self, grid):
  #   # Olha os agentes próximos e envia uma mensagem contendo a informação da saída mais próxima

  #   # Utiliza o protocolo FIPA para indicar a saída
  #   # TODO: Modificar para utilizar o FIPA
  #   neighbors = grid.neighbors(self, consts.EMERGENCY_EXIT_SIGN_VISIBLITY_RADIUS)
  #   for agents in neighbors:
  #     # Nem todos os agentes possuem a classe
  #     # O ideal seria conseguir filtrar pelo tipo de agente
  #     try:
  #       if agents.agent_class == consts.ADULT_KEY:
  #         agents.known_exit_position = self.nearest_emergency_exit
  #     except:
  #       pass


class EmergencyExitAgent(ap.Agent):
  def setup(self):
    self.is_emergency_exit = True
    self.safe_agents_dict = {
      consts.ADULT_KEY: 0,
      consts.CHILD_KEY: 0,
      consts.ELDER_KEY: 0,
      consts.LIM_MOB_KEY: 0,
      consts.EMPLOYEE_KEY: 0
    }

  def allow_people(self, grid):
    neighbors = grid.neighbors(self, consts.EMERGENCY_EXIT_VISIBLITY_RADIUS)

    neighbors_close_to_exit = [
        agent
        for agent in neighbors
        if (isinstance(agent, PersonAgent))
        and (hasattr(agent, consts.IS_SAFE_KEY) and (not agent.is_safe))
    ]

    for safe_neighbor in neighbors_close_to_exit:
      self.safe_agents_dict[safe_neighbor.agent_class] += 1

    grid.remove_agents(neighbors_close_to_exit)


class PersonAgent(ap.Agent):
  def setup(self):
    self.known_exit_position = None
    self.is_safe = False

  def setup_characteristics(self, agent_class):
    self.agent_class = agent_class
    self.memory = utils.CircularBuffer(consts.AGENTS_CLASS_CHARACTERISTICS_MAPPING[self.agent_class][consts.MEMORY_KEY])

    self.environment_knowledge = consts.AGENTS_CLASS_CHARACTERISTICS_MAPPING[self.agent_class][consts.ENV_KNOW_KEY]
    self.path_finding = search.HeuristicSearch(max_iter=self.environment_knowledge)

    self.panic_level = random.uniform(0, 0.3)

    self.physical_capacity = consts.AGENTS_CLASS_CHARACTERISTICS_MAPPING[self.agent_class][consts.PHYS_CAP_KEY]
    self.accumulated_steps = 0

    # TODO: Adicionar informações das saídas de emergência se for da classe EMPLOYEE

  def _get_agent_current_position(self, grid):
    current_position = None
    try:
      current_position = grid.positions[self]
    except:
      pass
    return current_position

  def evacuate(self, grid):
    current_position = self._get_agent_current_position(grid)
    if current_position is None:
      return

    # Percept the environment
    closer_neighbors = grid.neighbors(self, 1)

    # Only check nearby exits (to avoid seeing over obstacles)
    for agent in closer_neighbors:
      if isinstance(agent, EmergencyExitAgent):
        self.known_exit_position = grid.positions[agent]

    # Look for distant agents to warn them
    distant_neighbors = grid.neighbors(self, 3)
    for agent in distant_neighbors:
      if isinstance(agent, EmergencyExitSignAgent):
        self.known_exit_position = agent.nearest_emergency_exit
      elif isinstance(agent, PersonAgent):
        if self.agent_class == consts.ADULT_KEY or self.agent_class == consts.EMPLOYEE_KEY:
          if self.known_exit_position is not None:
            agent.known_exit_position = self.known_exit_position

    # Move based on its physical capacity
    self.accumulated_steps += self.physical_capacity

    if self.accumulated_steps >= 1:
      self.accumulated_steps = 0

      possible_next_positions = search.get_absolute_possible_movements(current_position)
      empty_positions = grid.empty

      posible_next_positions_empty = search.get_empty_possible_positions(possible_next_positions, empty_positions)
      not_previously_seen_empty_positions = utils.find_exclusive_tuples(posible_next_positions_empty, self.memory.get())

      best_absolute_destination = current_position
      if not_previously_seen_empty_positions:
        if self.known_exit_position == None:
          best_absolute_destination = random.choice(not_previously_seen_empty_positions)
        else:
          best_node = self.path_finding.find_best_path(self.memory, current_position, self.known_exit_position, grid)
          # TODO: Adicionar influência do nível de pânico
          # Dependendo do nível de pânico, a pessoa pode escolher o caminho não ótimo
          best_absolute_destination = best_node.previous_states[1]

      # Action
      grid.move_to(self, best_absolute_destination)
      self.memory.append(best_absolute_destination)
