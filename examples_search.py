"""Ejemplos de uso de algoritmos de búsqueda."""

from src.algorithms.search import bfs, dfs, ucs, a_star


def ejemplo_grafo_simple():
    """Ejemplo 1: Grafo simple del notebook."""
    print("=" * 60)
    print("EJEMPLO 1: Grafo Simple")
    print("=" * 60)

    graph = {
        "A": ["B", "F"],
        "B": ["A", "C", "E"],
        "C": ["B", "D", "E"],
        "D": ["C", "E", "F"],
        "E": ["B", "C", "D"],
        "F": ["A", "D"],
    }

    print("\nGrafo:")
    for node, neighbors in graph.items():
        print(f"  {node} -> {neighbors}")

    print("\nBuscando camino de A a D:")
    result_bfs = bfs(graph, "A", "D")
    print(f"  BFS: {' -> '.join(result_bfs.path)}")
    print(f"       Costo: {result_bfs.cost}, Nodos explorados: {result_bfs.explored}")

    result_dfs = dfs(graph, "A", "D")
    print(f"  DFS: {' -> '.join(result_dfs.path)}")
    print(f"       Costo: {result_dfs.cost}, Nodos explorados: {result_dfs.explored}")


def ejemplo_laberinto():
    """Ejemplo 2: Laberinto simulado con estados (fila, columna)."""
    print("\n" + "=" * 60)
    print("EJEMPLO 2: Laberinto 3x3")
    print("=" * 60)

    # Laberinto:
    # (0,0) - (0,1) - (0,2)
    #  |       |       |
    # (1,0) - (1,1) - (1,2)
    #  |       |       |
    # (2,0) - (2,1) - (2,2)

    graph = {
        (0, 0): [(0, 1), (1, 0)],
        (0, 1): [(0, 0), (0, 2), (1, 1)],
        (0, 2): [(0, 1), (1, 2)],
        (1, 0): [(0, 0), (1, 1), (2, 0)],
        (1, 1): [(0, 1), (1, 0), (1, 2), (2, 1)],
        (1, 2): [(0, 2), (1, 1), (2, 2)],
        (2, 0): [(1, 0), (2, 1)],
        (2, 1): [(1, 1), (2, 0), (2, 2)],
        (2, 2): [(1, 2), (2, 1)],
    }

    start = (0, 0)
    goal = (2, 2)

    print(f"\nInicio: {start}, Objetivo: {goal}")

    result_bfs = bfs(graph, start, goal)
    print(f"\nBFS:")
    print(f"  Camino: {' -> '.join(str(pos) for pos in result_bfs.path)}")
    print(f"  Movimientos: {result_bfs.cost}")
    print(f"  Nodos explorados: {result_bfs.explored}")

    result_dfs = dfs(graph, start, goal)
    print(f"\nDFS:")
    print(f"  Camino: {' -> '.join(str(pos) for pos in result_dfs.path)}")
    print(f"  Movimientos: {result_dfs.cost}")
    print(f"  Nodos explorados: {result_dfs.explored}")


def ejemplo_comparacion():
    """Ejemplo 3: Comparación BFS vs DFS."""
    print("\n" + "=" * 60)
    print("EJEMPLO 3: Comparación de Eficiencia")
    print("=" * 60)

    # Grafo con múltiples caminos
    graph = {
        "A": ["B", "C"],
        "B": ["A", "D", "E"],
        "C": ["A", "F"],
        "D": ["B"],
        "E": ["B", "G"],
        "F": ["C", "H"],
        "G": ["E", "I"],
        "H": ["F", "I"],
        "I": ["G", "H"],
    }

    print("\nGrafo con múltiples caminos")

    for start, goal in [("A", "I"), ("A", "D"), ("A", "G")]:
        print(f"\nBuscando: {start} -> {goal}")

        result_bfs = bfs(graph, start, goal)
        result_dfs = dfs(graph, start, goal)

        print(f"  BFS: {result_bfs.cost} movimientos, {result_bfs.explored} explorados")
        print(f"  DFS: {result_dfs.cost} movimientos, {result_dfs.explored} explorados")


def ejemplo_sin_solucion():
    """Ejemplo 4: Grafo desconectado (sin solución)."""
    print("\n" + "=" * 60)
    print("EJEMPLO 4: Grafo sin Solución")
    print("=" * 60)

    graph = {
        "A": ["B"],
        "B": ["A"],
        "C": ["D"],
        "D": ["C"],
    }

    print("\nGrafo con dos componentes desconectadas:")
    print("  Componente 1: A <-> B")
    print("  Componente 2: C <-> D")

    result_bfs = bfs(graph, "A", "C")
    print(f"\nBuscando A -> C:")
    print(f"  BFS: {'Sin solución' if result_bfs.path is None else result_bfs.path}")
    print(f"  Nodos explorados: {result_bfs.explored}")


def ejemplo_ucs():
    """Ejemplo 5: UCS con grafo ponderado."""
    print("\n" + "=" * 60)
    print("EJEMPLO 5: Búsqueda de Costo Uniforme (UCS)")
    print("=" * 60)

    graph = {
        "A": ["B", "C"],
        "B": ["D", "E"],
        "C": ["E", "F"],
        "D": ["G"],
        "E": ["G"],
        "F": ["G"],
        "G": []
    }

    costs = {
        ("A", "B"): 2, ("A", "C"): 4,
        ("B", "D"): 5, ("B", "E"): 10,
        ("C", "E"): 3, ("C", "F"): 6,
        ("D", "G"): 4, ("E", "G"): 2, ("F", "G"): 3,
    }

    print("\nGrafo ponderado (con costos diferentes):")
    print("  A --2--> B --5--> D --4--> G")
    print("  A --4--> C --3--> E --2--> G")
    print("  A --4--> C --6--> F --3--> G")

    result = ucs(graph, "A", "G", costs)
    print(f"\nUCS (A -> G):")
    print(f"  Camino: {' -> '.join(result.path)}")
    print(f"  Costo total: {result.cost}")
    print(f"  Nodos explorados: {result.explored}")
    print(f"  (UCS encontró el camino de menor costo acumulado)")


def ejemplo_astar():
    """Ejemplo 6: A* con heurística."""
    print("\n" + "=" * 60)
    print("EJEMPLO 6: A* con Heurística Manhattan")
    print("=" * 60)

    # Cuadrícula 4x4
    graph = {
        (0, 0): [(0, 1), (1, 0)],
        (0, 1): [(0, 0), (0, 2), (1, 1)],
        (0, 2): [(0, 1), (0, 3), (1, 2)],
        (0, 3): [(0, 2), (1, 3)],
        (1, 0): [(0, 0), (1, 1), (2, 0)],
        (1, 1): [(0, 1), (1, 0), (1, 2), (2, 1)],
        (1, 2): [(0, 2), (1, 1), (1, 3), (2, 2)],
        (1, 3): [(0, 3), (1, 2), (2, 3)],
        (2, 0): [(1, 0), (2, 1), (3, 0)],
        (2, 1): [(1, 1), (2, 0), (2, 2), (3, 1)],
        (2, 2): [(1, 2), (2, 1), (2, 3), (3, 2)],
        (2, 3): [(1, 3), (2, 2), (3, 3)],
        (3, 0): [(2, 0), (3, 1)],
        (3, 1): [(2, 1), (3, 0), (3, 2)],
        (3, 2): [(2, 2), (3, 1), (3, 3)],
        (3, 3): [(2, 3), (3, 2)],
    }

    def manhattan(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    start = (0, 0)
    goal = (3, 3)

    print(f"\nCuadrícula 4x4: {start} -> {goal}")

    result_bfs = bfs(graph, start, goal)
    result_astar = a_star(graph, start, goal, manhattan)

    print(f"\nBFS (ciego):")
    print(f"  Movimientos: {result_bfs.cost}")
    print(f"  Nodos explorados: {result_bfs.explored}")

    print(f"\nA* (con heurística Manhattan):")
    print(f"  Movimientos: {result_astar.cost}")
    print(f"  Nodos explorados: {result_astar.explored}")
    print(f"  Mejora: {result_bfs.explored - result_astar.explored} nodos menos explorados")


def ejemplo_astar_vs_ucs():
    """Ejemplo 7: Comparación A* vs UCS."""
    print("\n" + "=" * 60)
    print("EJEMPLO 7: A* vs UCS en Grafo Ponderado")
    print("=" * 60)

    graph = {
        "A": ["B", "C"],
        "B": ["D", "E"],
        "C": ["E", "F"],
        "D": ["G"],
        "E": ["G"],
        "F": ["G"],
        "G": []
    }

    costs = {
        ("A", "B"): 2, ("A", "C"): 4,
        ("B", "D"): 5, ("B", "E"): 10,
        ("C", "E"): 3, ("C", "F"): 6,
        ("D", "G"): 4, ("E", "G"): 2, ("F", "G"): 3,
    }

    # Heurística: estimación del costo a G
    def heuristic_to_g(node, goal):
        estimates = {
            "A": 7, "B": 6, "C": 4,
            "D": 3, "E": 2, "F": 2,
            "G": 0
        }
        return estimates.get(node, 0)

    result_ucs = ucs(graph, "A", "G", costs)
    result_astar = a_star(graph, "A", "G", heuristic_to_g, costs)

    print(f"\nMismo problema: A -> G")

    print(f"\nUCS (solo costo acumulado):")
    print(f"  Camino: {' -> '.join(result_ucs.path)}")
    print(f"  Costo: {result_ucs.cost}")
    print(f"  Nodos explorados: {result_ucs.explored}")

    print(f"\nA* (costo + heurística):")
    print(f"  Camino: {' -> '.join(result_astar.path)}")
    print(f"  Costo: {result_astar.cost}")
    print(f"  Nodos explorados: {result_astar.explored}")

    if result_astar.explored < result_ucs.explored:
        print(f"\n✨ A* fue más eficiente: {result_ucs.explored - result_astar.explored} nodos menos")
    else:
        print(f"\n✨ A* y UCS encontraron la misma solución con eficiencia similar")


if __name__ == "__main__":
    ejemplo_grafo_simple()
    ejemplo_laberinto()
    ejemplo_comparacion()
    ejemplo_sin_solucion()
    ejemplo_ucs()
    ejemplo_astar()
    ejemplo_astar_vs_ucs()

    print("\n" + "=" * 60)
    print("✅ Todos los ejemplos completados")
    print("=" * 60)
