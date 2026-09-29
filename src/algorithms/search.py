"""Algoritmos de búsqueda: BFS, DFS, UCS y A*."""

from collections import deque
from heapq import heappush, heappop
from typing import List, Dict, Optional, Callable, Tuple
from itertools import count


class SearchResult:
    """Resultado de una búsqueda."""

    def __init__(self, path: Optional[List], cost: int, explored: int):
        self.path = path
        self.cost = cost
        self.explored = explored

    def __repr__(self):
        if self.path:
            return f"SearchResult(path_length={len(self.path)-1}, cost={self.cost}, explored={self.explored})"
        return f"SearchResult(No solution found, explored={self.explored})"


def bfs(graph: Dict, start, goal) -> SearchResult:
    """
    Búsqueda en Anchura (BFS).

    Explora por niveles usando una cola FIFO.
    Garantiza el camino con menos movimientos en grafos sin pesos.

    Args:
        graph: Diccionario de adyacencia {nodo: [vecinos]}
        start: Nodo inicial
        goal: Nodo objetivo

    Returns:
        SearchResult con el camino, costo y nodos explorados
    """
    if start == goal:
        return SearchResult([start], 0, 1)

    visited = {start}
    queue = deque([(start, [start])])
    explored = 0

    while queue:
        node, path = queue.popleft()
        explored += 1

        for neighbor in graph.get(node, []):
            if neighbor == goal:
                return SearchResult(path + [neighbor], len(path), explored + 1)

            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, path + [neighbor]))

    return SearchResult(None, float('inf'), explored)


def dfs(graph: Dict, start, goal) -> SearchResult:
    """
    Búsqueda en Profundidad (DFS).

    Explora profundizando en una rama usando una pila LIFO.
    NO garantiza el camino más corto, pero usa menos memoria.

    Args:
        graph: Diccionario de adyacencia {nodo: [vecinos]}
        start: Nodo inicial
        goal: Nodo objetivo

    Returns:
        SearchResult con el camino, costo y nodos explorados
    """
    if start == goal:
        return SearchResult([start], 0, 1)

    visited = {start}
    stack = [(start, [start])]
    explored = 0

    while stack:
        node, path = stack.pop()
        explored += 1

        for neighbor in graph.get(node, []):
            if neighbor == goal:
                return SearchResult(path + [neighbor], len(path), explored + 1)

            if neighbor not in visited:
                visited.add(neighbor)
                stack.append((neighbor, path + [neighbor]))

    return SearchResult(None, float('inf'), explored)


def ucs(graph: Dict, start: str, goal: str,
        costs: Dict[Tuple[str, str], int]) -> SearchResult:
    """
    Búsqueda de Costo Uniforme (UCS).

    Expande primero el nodo con menor costo acumulado.
    Garantiza el camino de costo mínimo.

    Args:
        graph: Diccionario de adyacencia {nodo: [vecinos]}
        start: Nodo inicial
        goal: Nodo objetivo
        costs: Diccionario de costos {(nodo1, nodo2): costo}

    Returns:
        SearchResult con el camino, costo y nodos explorados
    """
    if start == goal:
        return SearchResult([start], 0, 1)

    tie_breaker = count()
    frontier = [(0, next(tie_breaker), start, [start])]
    best_cost = {start: 0}
    explored = 0

    while frontier:
        cost, _, node, path = heappop(frontier)

        if cost > best_cost.get(node, float('inf')):
            continue

        explored += 1

        if node == goal:
            return SearchResult(path, cost, explored)

        for neighbor in graph.get(node, []):
            edge_cost = costs.get((node, neighbor), 1)
            new_cost = cost + edge_cost

            if new_cost < best_cost.get(neighbor, float('inf')):
                best_cost[neighbor] = new_cost
                heappush(frontier, (new_cost, next(tie_breaker), neighbor, path + [neighbor]))

    return SearchResult(None, float('inf'), explored)


def a_star(graph: Dict, start: str, goal: str,
           heuristic: Callable[[str, str], float],
           costs: Dict[Tuple[str, str], int] = None) -> SearchResult:
    """
    Algoritmo A*.

    Expande primero el nodo con menor f(n) = g(n) + h(n).
    - g(n): costo acumulado
    - h(n): heurística (estimación del costo restante)

    Garantiza camino óptimo si la heurística es admisible.

    Args:
        graph: Diccionario de adyacencia {nodo: [vecinos]}
        start: Nodo inicial
        goal: Nodo objetivo
        heuristic: Función h(nodo, goal) que estima el costo restante
        costs: Diccionario de costos (opcional, default 1)

    Returns:
        SearchResult con el camino, costo y nodos explorados
    """
    if costs is None:
        costs = {}

    if start == goal:
        return SearchResult([start], 0, 1)

    tie_breaker = count()
    h_start = heuristic(start, goal)
    frontier = [(h_start, 0, next(tie_breaker), start, [start])]
    best_cost = {start: 0}
    explored = 0

    while frontier:
        f_score, g_score, _, node, path = heappop(frontier)

        if g_score > best_cost.get(node, float('inf')):
            continue

        explored += 1

        if node == goal:
            return SearchResult(path, g_score, explored)

        for neighbor in graph.get(node, []):
            edge_cost = costs.get((node, neighbor), 1)
            new_g = g_score + edge_cost
            h_neighbor = heuristic(neighbor, goal)
            new_f = new_g + h_neighbor

            if new_g < best_cost.get(neighbor, float('inf')):
                best_cost[neighbor] = new_g
                heappush(frontier, (new_f, new_g, next(tie_breaker), neighbor, path + [neighbor]))

    return SearchResult(None, float('inf'), explored)
