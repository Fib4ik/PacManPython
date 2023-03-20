from collections import deque

class Graph(object):
    """ class for realize graph from list """
    @staticmethod
    def cord(x, y):
        return str(x) + ":" + str(y)

    @staticmethod
    def nums(cordinate):
        return list(map(int, cordinate.split(":")))

    def __init__(self, list_map, block = []):
        self.list_map = list_map
        self.graph = {}
        variants = [0, -1], [0, 1], [-1, 0], [1, 0]
        for index in range(len(list_map) * len(list_map[0])):
            y = index // len(list_map[0])
            x = index - y * len(list_map[0])
            if list_map[y][x] not in block:
                result = []
                for v in variants:
                    if len(list_map[0]) > x + v[0] >= 0 and len(list_map) > y + v[1] >= 0:
                        if list_map[y + v[1]][x + v[0]] not in block:
                            result.append(str(x + v[0]) + ":" + str(y + v[1]))
                self.graph[str(x) + ":" + str(y)] = result[:]

    def find_from_to(self, from_coord, to_coord):
        parent = {}
        visited = []
        search_deque = deque()

        search_deque += [from_coord]
        current_point = None
        while search_deque:
            current_point = search_deque.popleft()
            if not current_point in visited:
                if current_point == to_coord:
                    break
                else:
                    search_deque += self.graph[current_point]
                    for child in self.graph[current_point]:
                        if not child in visited:
                            parent[child] = current_point
                    visited.append(current_point)

        path = []
        while current_point != from_coord:
            path.append(current_point)
            current_point = parent[current_point]
        path.append(current_point)
        return path


if __name__ == "__main__":
    print("You are start library    =(")
