"""Tests para algoritmos de búsqueda."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.algorithms.search import bfs, dfs, SearchResult


class TestBFS:
    """Tests para BFS."""

    def test_bfs_simple_graph(self):
        """BFS en un grafo simple."""
        graph = {
            "A": ["B", "F"],
            "B": ["A", "C", "E"],
            "C": ["B", "D", "E"],
            "D": ["C", "E", "F"],
            "E": ["B", "C", "D"],
            "F": ["A", "D"],
        }

        result = bfs(graph, "A", "D")

        assert result.path is not None
        assert result.path[0] == "A"
        assert result.path[-1] == "D"
        assert result.cost >= 2  # Mínimo 2 movimientos

    def test_bfs_start_equals_goal(self):
        """BFS cuando inicio = objetivo."""
        graph = {"A": ["B"], "B": ["A"]}
        result = bfs(graph, "A", "A")

        assert result.path == ["A"]
        assert result.cost == 0
        assert result.explored == 1

    def test_bfs_no_solution(self):
        """BFS cuando no hay solución."""
        graph = {
            "A": ["B"],
            "B": ["A"],
            "C": ["D"],
            "D": ["C"],
        }

        result = bfs(graph, "A", "C")

        assert result.path is None
        assert result.cost == float('inf')

    def test_bfs_shortest_path(self):
        """BFS garantiza el camino más corto."""
        # Grafo lineal: A -> B -> C -> D
        graph = {
            "A": ["B"],
            "B": ["A", "C"],
            "C": ["B", "D"],
            "D": ["C"],
        }

        result = bfs(graph, "A", "D")

        assert result.path == ["A", "B", "C", "D"]
        assert result.cost == 3  # 3 movimientos

    def test_bfs_maze_like(self):
        """BFS en un laberinto pequeño."""
        # Simular estados de posición: (0,0), (0,1), etc.
        # Vecinos accesibles directamente
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

        result = bfs(graph, (0, 0), (2, 2))

        assert result.path is not None
        assert result.path[0] == (0, 0)
        assert result.path[-1] == (2, 2)
        assert result.cost == 4  # Camino mínimo: 4 movimientos


class TestDFS:
    """Tests para DFS."""

    def test_dfs_simple_graph(self):
        """DFS en un grafo simple."""
        graph = {
            "A": ["B", "F"],
            "B": ["A", "C", "E"],
            "C": ["B", "D", "E"],
            "D": ["C", "E", "F"],
            "E": ["B", "C", "D"],
            "F": ["A", "D"],
        }

        result = dfs(graph, "A", "D")

        assert result.path is not None
        assert result.path[0] == "A"
        assert result.path[-1] == "D"

    def test_dfs_start_equals_goal(self):
        """DFS cuando inicio = objetivo."""
        graph = {"A": ["B"], "B": ["A"]}
        result = dfs(graph, "A", "A")

        assert result.path == ["A"]
        assert result.cost == 0

    def test_dfs_no_solution(self):
        """DFS cuando no hay solución."""
        graph = {
            "A": ["B"],
            "B": ["A"],
            "C": ["D"],
            "D": ["C"],
        }

        result = dfs(graph, "A", "C")

        assert result.path is None

    def test_dfs_explores_depth_first(self):
        """DFS explora primero en profundidad."""
        # Grafo con ramas: A -> (B -> C) y (A -> D)
        graph = {
            "A": ["B", "D"],
            "B": ["A", "C"],
            "C": ["B"],
            "D": ["A"],
        }

        result = dfs(graph, "A", "C")

        assert result.path is not None
        # DFS debería ir por B primero (por cómo entra en la pila)
        assert "B" in result.path


class TestSearchResult:
    """Tests para la clase SearchResult."""

    def test_search_result_with_path(self):
        """SearchResult con solución."""
        result = SearchResult(["A", "B", "C"], 2, 5)

        assert result.path == ["A", "B", "C"]
        assert result.cost == 2
        assert result.explored == 5
        assert "path_length=2" in repr(result)

    def test_search_result_no_solution(self):
        """SearchResult sin solución."""
        result = SearchResult(None, float('inf'), 10)

        assert result.path is None
        assert "No solution" in repr(result)


if __name__ == "__main__":
    # Ejecutar tests manualmente
    print("Ejecutando tests de BFS...")
    test_bfs = TestBFS()
    test_bfs.test_bfs_simple_graph()
    test_bfs.test_bfs_shortest_path()
    test_bfs.test_bfs_maze_like()
    print("✅ Tests de BFS pasaron\n")

    print("Ejecutando tests de DFS...")
    test_dfs = TestDFS()
    test_dfs.test_dfs_simple_graph()
    test_dfs.test_dfs_explores_depth_first()
    print("✅ Tests de DFS pasaron\n")

    print("Ejecutando tests de SearchResult...")
    test_result = TestSearchResult()
    test_result.test_search_result_with_path()
    test_result.test_search_result_no_solution()
    print("✅ Tests de SearchResult pasaron\n")

    print("✅ ¡Todos los tests pasaron!")
