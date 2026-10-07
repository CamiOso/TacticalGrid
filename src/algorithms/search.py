"""Algoritmos de búsqueda: BFS, DFS, UCS y A*."""

from collections import deque
from heapq import heappush, heappop, heapify
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

    **Propósito**: Encontrar el camino con menos movimientos (número de pasos).

    **Estrategia**: Expande por niveles usando una cola FIFO. Primero visita todos
    los nodos a distancia 1, luego distancia 2, etc.

    **Información del estado utilizada**: Solo la posición actual (nodo). No utiliza
    heurísticas ni información sobre el objetivo.

    **Costo Computacional**:
    - Tiempo: O(V + E) donde V=vértices, E=aristas
    - Espacio: O(V) para la cola en peor caso

    **Optimalidad**: ✓ Encuentra camino óptimo por número de movimientos
    (en grafos sin pesos).

    **Ventaja**: Completo y óptimo para grafos sin pesos.

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

    **Propósito**: Explorar sistemáticamente el espacio, profundizando al máximo
    en cada rama antes de retroceder.

    **Estrategia**: Usa una pila LIFO. Expande el nodo más recientemente agregado,
    descendiendo profundamente antes de explorar hermanos.

    **Información del estado utilizada**: Solo la posición actual. No utiliza
    heurísticas ni información del objetivo (búsqueda ciega).

    **Costo Computacional**:
    - Tiempo: O(V + E) en peor caso (puede explorar todo el grafo)
    - Espacio: O(h) donde h=profundidad del árbol (mejor que BFS)

    **Optimalidad**: ✗ NO garantiza el camino más corto. El camino encontrado
    depende del orden de exploración de vecinos.

    **Ventaja**: Usa menos memoria que BFS. Útil para exploración profunda.

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

    **Propósito**: Encontrar el camino de costo mínimo acumulado (no el más corto).

    **Estrategia**: Expande siempre el nodo con menor costo acumulado g(n) desde
    el inicio. Usa una cola de prioridad ordenada por costo.

    **Información del estado utilizada**:
    - Costo acumulado desde inicio (g)
    - Costos de aristas entre nodos
    NO utiliza información sobre el objetivo (búsqueda ciega).

    **Costo Computacional**:
    - Tiempo: O((V + E) log V) con heap de prioridad
    - Espacio: O(V) para el heap

    **Optimalidad**: ✓ Garantiza el camino de costo mínimo si todos los costos
    son positivos.

    **Diferencia vs BFS**: BFS minimiza pasos, UCS minimiza costo acumulado.
    En un mapa con terrenos variados, UCS puede elegir un camino más largo pero
    más barato (atravesar pasto en lugar de montaña).

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

    **Propósito**: Encontrar el camino de costo mínimo de forma más eficiente
    que UCS usando información heurística sobre el objetivo.

    **Estrategia**: Expande el nodo con menor f(n) = g(n) + h(n), donde:
    - g(n): Costo acumulado desde inicio (real)
    - h(n): Heurística estimada del costo restante al objetivo

    **Información del estado utilizada**:
    - Costo acumulado desde inicio
    - Estimación heurística al objetivo
    - Costos de aristas

    **Costo Computacional**:
    - Tiempo: O((V + E) log V) con heap
    - Espacio: O(V)
    - En práctica: O((V + E) * factor_ramificación)
    - Mejor que UCS cuando h es informativa

    **Optimalidad**: ✓ Garantiza camino óptimo SI h(n) es ADMISIBLE.
    Admisible significa: h(n) <= h*(n) (nunca sobrestima el costo real).

    **Heurísticas comunes**:
    - Manhattan: |x1-x2| + |y1-y2| (para grid con movimientos 4-dir)
    - Euclidean: sqrt((x1-x2)² + (y1-y2)²) (línea recta)
    - Ambas son admisibles.

    **Ventaja sobre UCS**: Explora MENOS nodos porque h(n) guía la búsqueda
    hacia el objetivo. En un grid 5x5:
    - UCS: ~35 nodos explorados
    - A* Manhattan: ~29 nodos explorados

    Args:
        graph: Diccionario de adyacencia {nodo: [vecinos]}
        start: Nodo inicial
        goal: Nodo objetivo
        heuristic: Función h(nodo, goal) que estima costo restante. Debe ser admisible.
        costs: Diccionario de costos {(nodo1, nodo2): valor}. Default: 1 por arista.

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


def beam_search(graph: dict, start: str, goal: str,
                heuristic: Callable[[str, str], float],
                k: int = 2,
                costs: Dict[Tuple[str, str], int] = None) -> SearchResult:
    """
    Beam Search: A* con memoria limitada.

    **Propósito**: Encontrar camino sin explorar toda la frontera.
    Mantiene solo los k nodos más prometedores en memoria.

    **Estrategia**: Similar a A*, pero limita la frontera a k elementos.
    - Expande f(n) = g(n) + h(n) como A*
    - Pero solo conserva k mejores nodos
    - Cuando la frontera alcanza k, descarta el peor nodo

    **Información del estado que utiliza**:
    - Costo acumulado g(n)
    - Heurística estimada h(n)
    - Parámetro k (tamaño máximo de frontera)

    **Costo Computacional**:
    - Tiempo: O(b^d) en peor caso (sin poda)
    - Espacio: O(k) - frontera limitada a k nodos
    - Mucho mejor que A* en memoria (a costo de optimalidad)

    **Optimalidad**: ✗ NO garantiza camino óptimo
    - k pequeño: más rápido, menos memoria, peor camino
    - k grande: se acerca a A*, más memoria
    - Es un trade-off: memoria vs calidad de solución

    **Parámetros típicos**:
    - k=1: Greedy puro (muy rápido, muy malo)
    - k=2: Apenas mejor que greedy
    - k=4: Balance razonable
    - k=8+: Se acerca a A*

    **Análisis según PDF**:
    - Efecto de k en exploración: a mayor k, más nodos explorados
    - Efecto en solución: a mayor k, mejor camino
    - Efecto en memoria: lineal con k

    Args:
        graph: Diccionario de adyacencia {nodo: [vecinos]}
        start: Nodo inicial
        goal: Nodo objetivo
        heuristic: Función h(nodo, goal)
        k: Tamaño máximo de la frontera (beam width)
        costs: Diccionario de costos (opcional)

    Returns:
        SearchResult con el camino encontrado
    """
    if costs is None:
        costs = {}

    if start == goal:
        return SearchResult([start], 0, 1)

    if k <= 0:
        raise ValueError("k debe ser >= 1")

    tie_breaker = count()
    h_start = heuristic(start, goal)
    frontier = [(h_start, 0, next(tie_breaker), start, [start])]
    best_cost = {start: 0}
    explored = 0

    while frontier:
        # Expandir mejor nodo
        f_score, g_score, _, node, path = heappop(frontier)

        if g_score > best_cost.get(node, float('inf')):
            continue

        explored += 1

        if node == goal:
            return SearchResult(path, g_score, explored)

        # Generar sucesores
        successors = []
        for neighbor in graph.get(node, []):
            edge_cost = costs.get((node, neighbor), 1)
            new_g = g_score + edge_cost
            h_neighbor = heuristic(neighbor, goal)
            new_f = new_g + h_neighbor

            if new_g < best_cost.get(neighbor, float('inf')):
                best_cost[neighbor] = new_g
                successors.append((new_f, new_g, next(tie_breaker), neighbor, path + [neighbor]))

        # Agregar sucesores a la frontera
        for successor in successors:
            heappush(frontier, successor)

        # Mantener frontera limitada a k elementos
        if len(frontier) > k:
            # Descartar los peores elementos, mantener solo k mejores
            frontier_list = list(frontier)
            frontier_list.sort()  # Ordena por f_score (primer elemento de tupla)
            frontier = frontier_list[:k]
            heapify(frontier)

    return SearchResult(None, float('inf'), explored)
