""" This file contains the agents for the building evacuation simulation"""

import itertools
import random

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
    # TODO: Ele vai buscar pelas saídas mais próximas e definir a saída mais próxima
    # que será a saída que ele indicará para os agentes
    self.nearest_emergency_exit = (10, 0) # Hardcoded por enquanto
    # TODO: Calcular a informação da saída mais próxima para colocar na saída de emergencia

  def setup_pos(self, grid):
    self.grid = grid

  def inform_nearest_emergency_exit(self):
    # Olha os agentes próximos e envia uma mensagem contendo a informação da saída mais próxima

    # Utiliza o protocolo FIPA para indicar a saída
    # TODO: Modificar para utilizar o FIPA
    neighbors = self.grid.neighbors(self, 2)
    for agents in neighbors:
      # Nem todos os agentes possuem a classe
      # O ideal seria conseguir filtrar pelo tipo de agente
      try:
        if agents.agent_class == consts.ADULT_KEY:
          agents.nearest_emergency_exit = self.nearest_emergency_exit
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
    self.nearest_emergency_exit = None
    self.is_safe = False

  def setup_pos(self, grid):
    self.grid = grid

  def _compute_better_path(self, destination_path):
      if abs(destination_path[0]) >= self.physical_capacity:
        if destination_path[0] > 0:
          x_movement = self.physical_capacity
        else:
          x_movement = -self.physical_capacity
      else:
        x_movement = destination_path[0]

      if abs(destination_path[1]) >= self.physical_capacity:
        if destination_path[1] > 0:
          y_movement = self.physical_capacity
        else:
          y_movement = -self.physical_capacity
      else:
        y_movement = destination_path[1]

      return (x_movement, y_movement)

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

    if self.nearest_emergency_exit == None:
      best_absolute_destination = random.choice(posible_next_positions_empty)
    else:
      distances_list = []
      # Computar a diferença entre o destino e as posições possíveis
      for position in posible_next_positions_empty:
        # Calculando a distancia de manhattan (x1 - x0) + (y1 - y0), podemos mudar para outra distância
        current_distance = (self.nearest_emergency_exit[0] - position[0]) + (self.nearest_emergency_exit[1] - position[1])
      # Escolher o que tem a menor distância
      # Ordena a lista do menor pro maior e seleciona o primeiro item
      sorted_distances = sorted(distances_list)
      best_absolute_destination = sorted_distances[0]
    # for item in empty_positions:
      # print(f"item={item}")
    # neighbors = self.building.neighbors(person, 1) # Isso aqui me devolve uma lista de agentes proximos no raio, essa lista pode ser vazia
    # Isso vai ajudar pra ver se preciso me comunicar com algum agente proximo ou se existe algum obstaculo
    # print(f"Agent: {person}, Agent neighbors = {neighbors}, Len = {len(neighbors)}")
    # if self.nearest_emergency_exit == None:
    #   random_x_movement = random.choice([-self.physical_capacity, self.physical_capacity])
    #   random_y_movement = random.choice([-self.physical_capacity, self.physical_capacity])
    #   current_relative_destination = (random_x_movement, random_y_movement)
    # else:
    #   current_agent_position = self.grid.positions[self]
    #   delta_x = self.nearest_emergency_exit[0] - current_agent_position[0]
    #   delta_y = self.nearest_emergency_exit[1] - current_agent_position[1]
    #   destination_path = (delta_x, delta_y)
    #   current_relative_destination = self._compute_better_path(destination_path)

    self.grid.move_to(self, best_absolute_destination)

    # TODO: Checar se está perto da saída de emergência
    neighbors = self.grid.neighbors(self, self.physical_capacity)
    for agent in neighbors:
      try:
        if agent.is_emergency_exit:
          self.nearest_emergency_exit = self.grid.positions[agent]
      except:
        pass


class EmergencyExitAgent(ap.Agent):
  def setup(self):
    self.people_passed = 0
    self.is_emergency_exit = True

  def setup_pos(self, grid):
    self.grid = grid

  def allow_people(self):
    neighbors = self.grid.neighbors(self, 1)
    for agent in neighbors:
      # Apenas para agentes que sao pessoas
      # O ideal seria checar o tipo do agente
      try:
        if agent.is_safe == False:
          self.people_passed = self.people_passed + 1
          agent.is_safe = True
      except:
        pass
