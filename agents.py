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
    self.leader_agent = None
    self.number_of_followers = 0
    self.elapsed_time = 0

  def setup_characteristics(self, agent_class, exit_information=None):
    self.agent_class = agent_class
    self.memory = utils.CircularBuffer(consts.AGENTS_CLASS_CHARACTERISTICS_MAPPING[self.agent_class][consts.MEMORY_KEY])

    self.environment_knowledge = consts.AGENTS_CLASS_CHARACTERISTICS_MAPPING[self.agent_class][consts.ENV_KNOW_KEY]
    self.path_finding = search.HeuristicSearch(max_iter=self.environment_knowledge)

    if self.agent_class == consts.EMPLOYEE_KEY:
      self.panic_level = 0
    else:
      self.panic_level = random.uniform(0, 0.3)

    self.physical_capacity = consts.AGENTS_CLASS_CHARACTERISTICS_MAPPING[self.agent_class][consts.PHYS_CAP_KEY]
    self.accumulated_steps = 0

    if self.agent_class == consts.EMPLOYEE_KEY:
      self.emergency_exit_locations = exit_information

  def setup_position(self, grid):
    if self.agent_class == consts.EMPLOYEE_KEY:
      best_distance = float('inf')
      for emergency_exit in self.emergency_exit_locations:
        distance = utils.euclidean_distance(emergency_exit, self._get_agent_current_position(grid))
        if distance < best_distance:
          best_distance = distance
          nearest_exit = emergency_exit
      self.known_exit_position = nearest_exit


  def _get_agent_current_position(self, grid):
    current_position = None
    try:
      current_position = grid.positions[self]
    except:
      pass
    return current_position


  def _inform_known_position(self, agent_to_inform):
    if self.known_exit_position is not None:
      agent_to_inform.known_exit_position = self.known_exit_position


  def _inform_nearest_exit(self, agent_to_inform, grid):
    best_distance = float('inf')
    for emergency_exit in self.emergency_exit_locations:
      distance = utils.euclidean_distance(emergency_exit, self._get_agent_current_position(grid))
      if distance < best_distance:
        best_distance = distance
        nearest_exit = emergency_exit

    self.known_exit_position = nearest_exit
    agent_to_inform.known_exit_position = nearest_exit


  def _inform_follow_me(self, agent_to_inform):
    if agent_to_inform.leader_agent is None:
      agent_to_inform.leader_agent = self
      self.number_of_followers = self.number_of_followers + 1


  def _increment_accumulated_steps(self):
    self.accumulated_steps += self.physical_capacity


  def _increment_elapsed_time(self):
    self.elapsed_time = self.elapsed_time + 1


  def _agent_ready_to_move(self):
    ready_to_move = False
    if self.accumulated_steps >= 1:
      self.accumulated_steps = 0
      ready_to_move = True

    return ready_to_move

  def _get_next_positions(self, current_position, grid):
    possible_next_positions = search.get_absolute_possible_movements(current_position)
    empty_positions = grid.empty

    posible_next_positions_empty = search.get_empty_possible_positions(possible_next_positions, empty_positions)
    next_positions = utils.find_exclusive_tuples(posible_next_positions_empty, self.memory.get())
    if not next_positions:
      next_positions = posible_next_positions_empty

    return next_positions


  def _random_movement(self, not_previously_seen_empty_positions):
    destination = random.choice(not_previously_seen_empty_positions)

    return destination


  def _find_optimal_path(self, current_position, grid):
    best_node = self.path_finding.find_best_path(self.memory, current_position, self.known_exit_position, grid)
    if len(best_node.previous_states) > 1:
      destination = best_node.previous_states[1]
    else:
      destination = best_node.previous_states[0]

    return destination


  def evacuate(self, grid, strategy):
    # Check if the agent is still in the environment
    current_position = self._get_agent_current_position(grid)
    if current_position is None:
      return

    # Percept the environment
    closer_neighbors = grid.neighbors(self, 1)

    ## Only check nearby exits (to avoid seeing over obstacles)
    for agent in closer_neighbors:
      if isinstance(agent, EmergencyExitAgent):
        self.known_exit_position = grid.positions[agent]

    ## Look for distant agents to warn them
    distant_neighbors = grid.neighbors(self, 3)
    for agent in distant_neighbors:

      # The agents are able to notice the emergency exit independent of the strategy
      if isinstance(agent, EmergencyExitSignAgent):
        self.known_exit_position = agent.nearest_emergency_exit

      if isinstance(agent, PersonAgent):
        if strategy == consts.EVERY_MAN_FOR_HIMSELF_KEY:
          # Do nothing
          pass
        elif strategy == consts.COMMUNICATION_KEY:
          # Adults and employees are able to communicate the exit
          if self.agent_class in [consts.ADULT_KEY, consts.EMPLOYEE_KEY]:
            self._inform_known_position(agent)
        elif strategy == consts.EVACUATION_PLAN_KEY:
          if self.agent_class == consts.ADULT_KEY:
            self._inform_known_position(agent)
          elif self.agent_class == consts.EMPLOYEE_KEY:
            if agent.agent_class == consts.ADULT_KEY:
              self._inform_nearest_exit(agent, grid)
            elif agent.agent_class in [consts.CHILD_KEY, consts.ELDER_KEY, consts.LIM_MOB_KEY]:
              self._inform_follow_me(agent)
              self._inform_nearest_exit(agent, grid)

    # Move based on agent's physical capacity
    self._increment_accumulated_steps()
    self._increment_elapsed_time()

    if self._agent_ready_to_move():
      panic_level_rng = random.random()

      next_positions = self._get_next_positions(current_position, grid)

      if self.agent_class == consts.EMPLOYEE_KEY:
        if strategy == consts.EVACUATION_PLAN_KEY:
          if (self.number_of_followers >= 5 or self.elapsed_time >= 15):
            current_destination = self._find_optimal_path(current_position, grid)
          else:
            current_destination = self._random_movement(next_positions)
        elif strategy in [consts.EVERY_MAN_FOR_HIMSELF_KEY, consts.COMMUNICATION_KEY]:
          current_destination = self._find_optimal_path(current_position, grid)

      elif self.agent_class == consts.ADULT_KEY:
        if self.known_exit_position and (panic_level_rng >= self.panic_level):
          current_destination = self._find_optimal_path(current_position, grid)
        else:
          current_destination = self._random_movement(next_positions)

      elif self.agent_class in [consts.CHILD_KEY, consts.ELDER_KEY, consts.LIM_MOB_KEY]:
        current_destination = None
        # Leaders only exist in evacuation plan strategy
        if strategy == consts.EVACUATION_PLAN_KEY:
          if self.leader_agent:
            current_destination = self.leader_agent._get_agent_current_position(grid)

        if current_destination is None and self.known_exit_position and (panic_level_rng >= self.panic_level):
          current_destination = self._find_optimal_path(current_position, grid)
        else:
          current_destination = self._random_movement(next_positions)

      grid.move_to(self, current_destination)
      self.memory.append(current_destination)
