import utils
import itertools

import agents

from pprint import pprint

def get_absolute_possible_movements(current_position):
  if current_position is None:
    return

  # Lista com possíveis movimentações relativas
  possible_movements = list(range(-1, 2))
  # Gera uma lista de tuplas com as movimentações relativas possíveis
  possible_relative_movements = list(itertools.product(possible_movements, possible_movements))
  # Muda de posições relativas para posições absolutas
  possible_absolute_positions = [(current_position[0] + t[0], current_position[1] + t[1]) for t in possible_relative_movements]

  return possible_absolute_positions


def get_empty_possible_positions(positions_list, empty_positions_list):
  empty_possible_positions = []

  for evaluated_position in positions_list:
    if evaluated_position in empty_positions_list:
      empty_possible_positions.append(evaluated_position)

  return empty_possible_positions


class SearchNode:
    state = None
    father = None
    cost_since_root_node = 0
    heuristic_function = None
    evaluation_function = 0
    previous_states = []
    previous_nodes = []

    def __init__(self, state, father, cost_since_root_node, heuristic_function):
        self.state = state
        self.father = father
        self.cost_since_root_node = cost_since_root_node
        self.heuristic_function = heuristic_function
        self.evaluation_function = self.cost_since_root_node + self.heuristic_function

    def __repr__(self):
        string = f"f(n) = {self.evaluation_function}, h(n) = {self.heuristic_function}, g(n) = {self.cost_since_root_node}, Flatten state = {self.state}"
        return string


class HeuristicSearch:
    def __init__(self, max_iter=10):
        self.max_iter = max_iter

    def __check_final_condition(self, current_state, final_state):
        ret = False

        if utils.manhattan_distance(current_state, final_state) == 0:
            ret = True
        return ret

    def __update_frontier(self, child_nodes):
        updated_frontier = [*self.frontier, *child_nodes]

        self.frontier = sorted(updated_frontier, key=lambda x: x.evaluation_function)

    def _get_next_nodes(self, memory, current_node, final_state, grid):
        next_nodes = []

        possible_next_positions = get_absolute_possible_movements(current_node.state)
        empty_positions = grid.empty

        possible_next_positions_empty = get_empty_possible_positions(possible_next_positions, empty_positions)

        for position in possible_next_positions_empty:
            if position in memory:
                continue
            obstacle_term = len(grid.empty[(position[0]-1):(position[0]+2)][(position[1]-1):(position[1]+2)])
            distance_term = utils.manhattan_distance(final_state, position)
            heuristic_function = obstacle_term + distance_term
            cost_since_root_node = current_node.cost_since_root_node + 1

            child_node = SearchNode(position, current_node, cost_since_root_node, heuristic_function)
            child_node.previous_states = [current_node.state, *current_node.previous_states]
            child_node.previous_nodes = [current_node, *current_node.previous_nodes]

            next_nodes.append(child_node)

        return next_nodes

    def find_best_path(self, memory, initial_state, final_state, grid):
        self.frontier = []
        self.n_iter = 1

        initial_node = SearchNode(initial_state, None, 0, utils.manhattan_distance(final_state, initial_state))
        self.frontier.append(initial_node)

        while(True):
            #pprint(self.frontier)

            if not self.frontier:
                print(f"Frontier is empty. Finishing the algorithm")

            current_node = self.frontier.pop(0)

            if self.__check_final_condition(current_node.state, final_state) or (self.n_iter > self.max_iter):
                current_node.previous_states = [*current_node.previous_states[::-1], current_node.state]
                current_node.previous_nodes = [*current_node.previous_nodes[::-1], current_node]
                print("Final state or max iter was reached!")
                return current_node

            child_nodes = self._get_next_nodes(memory, current_node, final_state, grid)

            self.__update_frontier(child_nodes)
            self.n_iter = self.n_iter + 1


