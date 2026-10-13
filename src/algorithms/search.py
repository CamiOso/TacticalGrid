"""Algoritmos de búsqueda: BFS, DFS, UCS y A*."""

from collections import deque
from heapq import heappush, heappop, heapify
from typing import List, Dict, Optional, Callable, Tuple
from itertools import count


class SearchResult:
    """Resultado de una búsqueda."""

    def __init__(self, path: Optional[List], cost: int, expanded: int, generated: int = None, max_frontier: int = None):
        self.path = path
        self.cost = cost
        self.expanded = expanded  # Nodos expandidos (sacados de la frontera)
        self.generated = generated if generated is not None else expanded  # Nodos generados (creados)
        self.max_frontier = max_frontier if max_frontier is not None else expanded  # Máximo tamaño de frontera
        # Compatibilidad: explored ahora mapea a expanded
        self.explored = expanded

    def __repr__(self):
        if self.path:
            return f"SearchResult(path_length={len(self.path)-1}, cost={self.cost}, expanded={self.expanded}, generated={self.generated})"
        return f"SearchResult(No solution found, expanded={self.expanded}, generated={self.generated})"


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

    **IA**:
    - Usa: Frontier FIFO para expandir por niveles.
    - Interviene: Selecciona nodo más antiguo (FIFO) y pausa si hay ciclo.
    - Validar: Que visited evita revisitar; que result es camino conectado.

    Args:
        graph: Diccionario de adyacencia {nodo: [vecinos]}
        start: Nodo inicial
        goal: Nodo objetivo

    Returns:
        SearchResult con el camino, costo y nodos explorados
    """
    if start == goal:
        return SearchResult([start], 0, 1, 1, 1)

    visited = {start}
    queue = deque([(start, [start])])
    expanded = 0
    generated = 1  # start node

    while queue:
        node, path = queue.popleft()
        expanded += 1

        for neighbor in graph.get(node, []):
            if neighbor == goal:
                return SearchResult(path + [neighbor], len(path), expanded + 1, generated + 1, len(queue) + 1)

            if neighbor not in visited:
                visited.add(neighbor)
                generated += 1
                queue.append((neighbor, path + [neighbor]))

    return SearchResult(None, float('inf'), expanded, generated, 0)


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

    **IA**:
    - Usa: Frontier LIFO (pila) para explorar profundo primero.
    - Interviene: Selecciona nodo más reciente (LIFO) y retrocede si sin salida.
    - Validar: Que no hay ciclos (visited); que camino es válido.

    Args:
        graph: Diccionario de adyacencia {nodo: [vecinos]}
        start: Nodo inicial
        goal: Nodo objetivo

    Returns:
        SearchResult con el camino, costo y nodos explorados
    """
    if start == goal:
        return SearchResult([start], 0, 1, 1, 1)

    visited = {start}
    stack = [(start, [start])]
    expanded = 0
    generated = 1  # start node

    while stack:
        node, path = stack.pop()
        expanded += 1

        for neighbor in graph.get(node, []):
            if neighbor == goal:
                return SearchResult(path + [neighbor], len(path), expanded + 1, generated + 1, len(stack) + 1)

            if neighbor not in visited:
                visited.add(neighbor)
                generated += 1
                stack.append((neighbor, path + [neighbor]))

    return SearchResult(None, float('inf'), expanded, generated, 0)


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

    **IA**:
    - Usa: Frontier por costo acumulado g(n) con heap de prioridad.
    - Interviene: Selecciona nodo con menor costo; descarta si encuentra mejor camino.
    - Validar: Que best_cost evita redundancias; que resultado es costo mínimo.

    Args:
        graph: Diccionario de adyacencia {nodo: [vecinos]}
        start: Nodo inicial
        goal: Nodo objetivo
        costs: Diccionario de costos {(nodo1, nodo2): costo}

    Returns:
        SearchResult con el camino, costo y nodos explorados
    """
    if start == goal:
        return SearchResult([start], 0, 1, 1, 1)

    tie_breaker = count()
    frontier = [(0, next(tie_breaker), start, [start])]
    best_cost = {start: 0}
    expanded = 0
    generated = 1  # start node
    max_frontier = 1

    while frontier:
        cost, _, node, path = heappop(frontier)

        if cost > best_cost.get(node, float('inf')):
            continue

        expanded += 1

        if node == goal:
            return SearchResult(path, cost, expanded, generated, max_frontier)

        for neighbor in graph.get(node, []):
            edge_cost = costs.get((node, neighbor), 1)
            new_cost = cost + edge_cost

            if new_cost < best_cost.get(neighbor, float('inf')):
                best_cost[neighbor] = new_cost
                heappush(frontier, (new_cost, next(tie_breaker), neighbor, path + [neighbor]))
                generated += 1
                max_frontier = max(max_frontier, len(frontier))

    return SearchResult(None, float('inf'), expanded, generated, max_frontier)


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

    **IA**:
    - Usa: Frontier por f(n) = g(n) + h(n) (costo real + heurística).
    - Interviene: Heurística reduce nodos vs UCS; selecciona nodo con menor f.
    - Validar: Que h es admisible; que A* explora ≤ nodos que UCS.

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
        return SearchResult([start], 0, 1, 1, 1)

    tie_breaker = count()
    h_start = heuristic(start, goal)
    frontier = [(h_start, 0, next(tie_breaker), start, [start])]
    best_cost = {start: 0}
    expanded = 0
    generated = 1  # start node
    max_frontier = 1

    while frontier:
        f_score, g_score, _, node, path = heappop(frontier)

        if g_score > best_cost.get(node, float('inf')):
            continue

        expanded += 1

        if node == goal:
            return SearchResult(path, g_score, expanded, generated, max_frontier)

        for neighbor in graph.get(node, []):
            edge_cost = costs.get((node, neighbor), 1)
            new_g = g_score + edge_cost
            h_neighbor = heuristic(neighbor, goal)
            new_f = new_g + h_neighbor

            if new_g < best_cost.get(neighbor, float('inf')):
                best_cost[neighbor] = new_g
                heappush(frontier, (new_f, new_g, next(tie_breaker), neighbor, path + [neighbor]))
                generated += 1
                max_frontier = max(max_frontier, len(frontier))

    return SearchResult(None, float('inf'), expanded, generated, max_frontier)


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

    **IA**:
    - Usa: Frontier limitada a k mejores nodos (A* con memory cap).
    - Interviene: Ordena por f(n); descarta peores si excede k.
    - Validar: Que frontera ≤ k; que más k = menos exploración; k=1 es greedy.

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
        return SearchResult([start], 0, 1, 1, 1)

    if k <= 0:
        raise ValueError("k debe ser >= 1")

    tie_breaker = count()
    h_start = heuristic(start, goal)
    frontier = [(h_start, 0, next(tie_breaker), start, [start])]
    best_cost = {start: 0}
    expanded = 0
    generated = 1  # start node
    max_frontier = 1

    while frontier:
        # Expandir mejor nodo
        f_score, g_score, _, node, path = heappop(frontier)

        if g_score > best_cost.get(node, float('inf')):
            continue

        expanded += 1

        if node == goal:
            return SearchResult(path, g_score, expanded, generated, max_frontier)

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
                generated += 1

        # Agregar sucesores a la frontera
        for successor in successors:
            heappush(frontier, successor)

        max_frontier = max(max_frontier, len(frontier))

        # Mantener frontera limitada a k elementos
        if len(frontier) > k:
            # Descartar los peores elementos, mantener solo k mejores
            frontier_list = list(frontier)
            frontier_list.sort()  # Ordena por f_score (primer elemento de tupla)
            frontier = frontier_list[:k]
            heapify(frontier)

    return SearchResult(None, float('inf'), expanded, generated, max_frontier)
