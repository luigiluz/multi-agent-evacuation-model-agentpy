""" This file contains the agents for the building evacuation simulation"""

import itertools
import random
import utils

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

  def setup_pos(self, grid):
    self.grid = grid

  def setup_nearests_exits(self, emergency_exit_positions):
    current_position = self.grid.positions[self]
    best_distance = float('inf')

    for emergency_exit_position in emergency_exit_positions:
      current_distance = utils.manhattan_distance(emergency_exit_position, current_position)
      if current_distance < best_distance:
        self.nearest_emergency_exit = emergency_exit_position
        best_distance = current_distance


  def inform_nearest_emergency_exit(self):
    # Olha os agentes próximos e envia uma mensagem contendo a informação da saída mais próxima

    # Utiliza o protocolo FIPA para indicar a saída
    # TODO: Modificar para utilizar o FIPA
    neighbors = self.grid.neighbors(self, consts.EMERGENCY_EXIT_SIGN_VISIBLITY_RADIUS)
    for agents in neighbors:
      # Nem todos os agentes possuem a classe
      # O ideal seria conseguir filtrar pelo tipo de agente
      try:
        if agents.agent_class == consts.ADULT_KEY:
          agents.known_exit_position = self.nearest_emergency_exit
      except:
        pass


class PersonAgent(ap.Agent):
  # def setup(self, characteristics):
  def setup(self):
    # Preciso definir as características dos agentes de forma aleatoria
    # ou com base em algum parametro
    # self.physical_capacity = self.p.physical_capacity
    # self.panic_level = self.p.panic_level
    # self.environment_knowledge = self.p.environment_knowledge
    # TODO: Esses argumentos serão recebidos como entrada
    # self.physical_capacity = characteristics[PHYS_CAP_KEY]
    # self.panic_level = 0
    # self.environment_knowledge = characteristics[ENV_KNOW_KEY]
    self.physical_capacity = 1
    self.panic_level = 0
    self.environment_knowledge = 1
    self.agent_class = consts.ADULT_KEY
    self.known_exit_position = None
    self.is_safe = False
    self.memory = utils.CircularBuffer(consts.PERSON_AGENT_MEMORY_SIZE)

  def setup_pos(self, grid):
    self.grid = grid

  def _get_absolute_possible_movements(self):
    # Pega posição atual
    current_position = self.grid.positions[self]
    # Lista com possíveis movimentações relativas
    # Ex: se physical capacity = 1, pode se mover pra -1, 0, 1
    possible_movements = list(range(-self.physical_capacity, self.physical_capacity+1))
    # Gera uma lista de tuplas com as movimentações relativas possíveis
    possible_relative_movements = list(itertools.product(possible_movements, possible_movements))
    # Muda de posições relativas para posições absolutas
    possible_absolute_positions = [(current_position[0] + t[0], current_position[1] + t[1]) for t in possible_relative_movements]

    return possible_absolute_positions

  def _get_empty_possible_positions(self, positions_list, empty_positions_list):
    empty_possible_positions = []

    for evaluated_position in positions_list:
      if evaluated_position in empty_positions_list:
        empty_possible_positions.append(evaluated_position)

    return empty_possible_positions

  def evacuate(self):
    possible_next_positions = self._get_absolute_possible_movements()
    empty_positions = self.grid.empty

    posible_next_positions_empty = self._get_empty_possible_positions(possible_next_positions, empty_positions)
    not_previously_seen_empty_positions = utils.find_exclusive_tuples(posible_next_positions_empty, self.memory.get())

    best_absolute_destination = self.grid.positions[self]
    if not_previously_seen_empty_positions is not None:
      if self.known_exit_position == None:
        best_absolute_destination = random.choice(not_previously_seen_empty_positions)
      else:
        shortest_distance = float('inf')
        # Computar a diferença entre o destino e as posições possíveis
        for position in not_previously_seen_empty_positions:
          current_distance = utils.manhattan_distance(self.known_exit_position, position)
          if current_distance < shortest_distance:
            shortest_distance = current_distance
            best_absolute_destination = position

    self.grid.move_to(self, best_absolute_destination)
    self.memory.append(best_absolute_destination)

    neighbors = self.grid.neighbors(self, self.physical_capacity)
    for agent in neighbors:
      try:
        if agent.is_emergency_exit:
          self.known_exit_position = self.grid.positions[agent]
      except:
        pass


class EmergencyExitAgent(ap.Agent):
  def setup(self):
    self.people_passed = 0
    self.is_emergency_exit = True

  def setup_pos(self, grid):
    self.grid = grid

  # Isso aqui é apenas pra contabilizar os agentes que passaram
  def allow_people(self):
    neighbors = self.grid.neighbors(self, consts.EMERGENCY_EXIT_VISIBLITY_RADIUS)
    safe_agents = []
    for agent in neighbors:
      # Apenas para agentes que sao pessoas
      # O ideal seria checar o tipo do agente
      try:
        if agent.is_safe == False:
          self.people_passed = self.people_passed + 1
          safe_agents.append(agent)
      except:
        pass
    #self.grid.remove_agents(safe_agents)
