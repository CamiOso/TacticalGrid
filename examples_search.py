"""Ejemplos de uso de algoritmos de búsqueda BFS y DFS."""

from src.algorithms.search import bfs, dfs


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


if __name__ == "__main__":
    ejemplo_grafo_simple()
    ejemplo_laberinto()
    ejemplo_comparacion()
    ejemplo_sin_solucion()

    print("\n" + "=" * 60)
    print("✅ Ejemplos completados")
    print("=" * 60)
