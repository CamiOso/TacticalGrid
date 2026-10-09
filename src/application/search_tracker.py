"""Rastrea el proceso de búsqueda paso a paso."""

from typing import List, Dict, Tuple
from collections import deque
from heapq import heappush, heappop, heapify
from itertools import count

class SearchTracker:
    """Ejecuta búsqueda rastreando cada paso."""

    def __init__(self, graph: Dict, start, goal, costs: Dict = None):
        self.graph = graph
        self.start = start
        self.goal = goal
        self.costs = costs or {}
        self.steps = []  # Lista de pasos
        self.current_step = 0

    def track_bfs(self) -> Tuple[List, int, List]:
        """BFS rastreando pasos."""
        visited = {self.start}
        queue = deque([(self.start, [self.start])])
        explored_order = []

        while queue:
            node, path = queue.popleft()
            explored_order.append(node)

            # Guardar paso
            self.steps.append({
                'node': node,
                'path': path.copy(),
                'explored': explored_order.copy(),
                'frontier': list(queue)
            })

            for neighbor in self.graph.get(node, []):
                if neighbor == self.goal:
                    final_path = path + [neighbor]
                    self.steps.append({
                        'node': neighbor,
                        'path': final_path.copy(),
                        'explored': explored_order + [neighbor],
                        'frontier': []
                    })
                    return final_path, len(path), explored_order

                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))

        return None, float('inf'), explored_order

    def track_ucs(self) -> Tuple[List, int, List]:
        """UCS rastreando pasos."""
        tie_breaker = count()
        frontier = [(0, next(tie_breaker), self.start, [self.start])]
        best_cost = {self.start: 0}
        explored_order = []

        while frontier:
            cost, _, node, path = heappop(frontier)

            if cost > best_cost.get(node, float('inf')):
                continue

            explored_order.append(node)

            # Guardar paso
            self.steps.append({
                'node': node,
                'cost': cost,
                'path': path.copy(),
                'explored': explored_order.copy(),
                'frontier': [(c, n) for c, _, n, _ in frontier]
            })

            if node == self.goal:
                return path, cost, explored_order

            for neighbor in self.graph.get(node, []):
                edge_cost = self.costs.get((node, neighbor), 1)
                new_cost = cost + edge_cost

                if new_cost < best_cost.get(neighbor, float('inf')):
                    best_cost[neighbor] = new_cost
                    heappush(frontier, (new_cost, next(tie_breaker), neighbor, path + [neighbor]))

        return None, float('inf'), explored_order

    def get_step(self, index: int) -> Dict:
        """Obtiene un paso específico."""
        if 0 <= index < len(self.steps):
            return self.steps[index]
        return None

    def get_all_steps(self) -> List[Dict]:
        """Obtiene todos los pasos."""
        return self.steps

    def total_steps(self) -> int:
        """Retorna número total de pasos."""
        return len(self.steps)
