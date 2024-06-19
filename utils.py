from collections import deque

class CircularBuffer:
    def __init__(self, size):
        self.buffer = deque(maxlen=size)

    def append(self, value):
        self.buffer.append(value)

    def get(self):
        return list(self.buffer)

    def __contains__(self, item):
        return item in self.buffer

    def __getitem__(self, index):
        return self.buffer[index]


def manhattan_distance(destination, origin):
    if len(destination) != len(origin):
        raise ValueError("Tuples must be of the same length")
    return sum(abs(a - b) for a, b in zip(destination, origin))


def find_exclusive_tuples(list_a, list_b):
    # Convert lists to sets
    set_a = set(list_a)
    set_b = set(list_b)

    # Find elements exclusive to each list
    exclusive_to_a = set_a - set_b

    # Convert the result back to a list
    return list(exclusive_to_a)
