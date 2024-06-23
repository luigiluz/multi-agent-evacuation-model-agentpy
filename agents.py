""" This file contains the agents for the building evacuation simulation"""

import itertools
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


  def inform_nearest_emergency_exit(self, grid):
    # Olha os agentes próximos e envia uma mensagem contendo a informação da saída mais próxima

    # Utiliza o protocolo FIPA para indicar a saída
    # TODO: Modificar para utilizar o FIPA
    neighbors = grid.neighbors(self, consts.EMERGENCY_EXIT_SIGN_VISIBLITY_RADIUS)
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
    self.physical_capacity = 0 if random.random() < 0.23 else 1
    self.panic_level = 0
    self.environment_knowledge = 1
    self.agent_class = consts.ADULT_KEY
    self.known_exit_position = None
    self.is_safe = False
    self.memory = utils.CircularBuffer(consts.PERSON_AGENT_MEMORY_SIZE)
    self.path_finding = search.HeuristicSearch()

  def _get_agent_current_position(self, grid):
    current_position = None
    try:
      current_position = grid.positions[self]
    except:
      pass
    return current_position

  def evacuate(self, grid):
    # Pega posição atual
    current_position = self._get_agent_current_position(grid)
    if current_position is None:
      return

    # Eu vou precisar fazer isso no A*
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
        best_absolute_destination = best_node.previous_states[1]

    grid.move_to(self, best_absolute_destination)
    self.memory.append(best_absolute_destination)

    neighbors = grid.neighbors(self, self.physical_capacity)
    for agent in neighbors:
      try:
        if agent.is_emergency_exit:
          self.known_exit_position = grid.positions[agent]
      except:
        pass


class EmergencyExitAgent(ap.Agent):
  def setup(self):
    self.people_passed = 0
    self.is_emergency_exit = True

  # Isso aqui é apenas pra contabilizar os agentes que passaram
  def allow_people(self, grid):
    neighbors = grid.neighbors(self, consts.EMERGENCY_EXIT_VISIBLITY_RADIUS)

    neighbors = [
        agent
        for agent in neighbors
        if (isinstance(agent, PersonAgent))
        and (hasattr(agent, "is_safe") and (not agent.is_safe))
    ]
    # print(f"neighbors: {len(neighbors)}")
    # print(f"> safe (from this exit door): {self.people_passed}")

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
    # ELe sai do grid mas continua na lista
    # Preciso encontrar um jeito de não deixar ele mais na lista
    grid.remove_agents(safe_agents)
    # A bronca é que ele vai passar novamente no for e não vai ter mais posição
    # O que eu posso fazer para evitar isso de um jeito decente?
    # Nao queria fazer com um try except...
