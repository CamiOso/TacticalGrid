"""Tests para algoritmos de búsqueda."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.algorithms.search import bfs, dfs, ucs, a_star, SearchResult


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


class TestUCS:
    """Tests para Costo Uniforme (UCS)."""

    def test_ucs_simple_weighted_graph(self):
        """UCS en grafo ponderado."""
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

        result = ucs(graph, "A", "G", costs)

        assert result.path is not None
        assert result.path[0] == "A"
        assert result.path[-1] == "G"
        assert result.cost == 9  # Costo mínimo: A->C->E->G = 4+3+2

    def test_ucs_finds_minimum_cost(self):
        """UCS garantiza costo mínimo."""
        # Dos caminos: uno largo barato, uno corto caro
        graph = {
            "A": ["B", "C"],
            "B": ["D"],
            "C": ["D"],
            "D": []
        }

        costs = {
            ("A", "B"): 10,   # Camino corto pero caro
            ("B", "D"): 100,  # Muy caro
            ("A", "C"): 40,   # Camino largo
            ("C", "D"): 40,   # Pero barato total
        }

        result = ucs(graph, "A", "D", costs)

        assert result.path == ["A", "C", "D"]
        assert result.cost == 80  # A->C->D = 40+40 < A->B->D = 10+100

    def test_ucs_start_equals_goal(self):
        """UCS cuando inicio = objetivo."""
        graph = {"A": ["B"], "B": ["A"]}
        costs = {("A", "B"): 1, ("B", "A"): 1}

        result = ucs(graph, "A", "A", costs)

        assert result.cost == 0
        assert result.explored == 1

    def test_ucs_no_solution(self):
        """UCS cuando no hay solución."""
        graph = {"A": ["B"], "B": ["A"], "C": ["D"], "D": ["C"]}
        costs = {("A", "B"): 1, ("B", "A"): 1}

        result = ucs(graph, "A", "C", costs)

        assert result.path is None
        assert result.cost == float('inf')


class TestAStar:
    """Tests para A*."""

    def test_astar_with_manhattan(self):
        """A* con heurística Manhattan."""
        # Grafo en cuadrícula
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

        def manhattan(a, b):
            return abs(a[0] - b[0]) + abs(a[1] - b[1])

        result = a_star(graph, (0, 0), (2, 2), manhattan)

        assert result.path is not None
        assert result.path[0] == (0, 0)
        assert result.path[-1] == (2, 2)
        assert result.cost == 4  # Mínimo en cuadrícula 3x3

    def test_astar_better_than_ucs(self):
        """A* explora menos nodos que UCS con buena heurística."""
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

        # Heurística simple: distancia estimada a G
        def heuristic(node, goal):
            estimates = {
                "A": 7, "B": 6, "C": 4,
                "D": 3, "E": 2, "F": 2,
                "G": 0
            }
            return estimates.get(node, 0)

        result_ucs = ucs(graph, "A", "G", costs)
        result_astar = a_star(graph, "A", "G", heuristic, costs)

        # Ambos encuentran costo mínimo 9
        assert result_ucs.cost == 9
        assert result_astar.cost == 9

        # A* debería explorar menos o igual nodos
        assert result_astar.explored <= result_ucs.explored

    def test_astar_with_weak_heuristic(self):
        """A* con heurística nula = UCS."""
        graph = {"A": ["B"], "B": ["C"], "C": []}
        costs = {("A", "B"): 2, ("B", "C"): 3}

        result_ucs = ucs(graph, "A", "C", costs)
        result_astar = a_star(graph, "A", "C", lambda n, g: 0, costs)

        assert result_ucs.cost == result_astar.cost == 5

    def test_astar_start_equals_goal(self):
        """A* cuando inicio = objetivo."""
        graph = {"A": ["B"], "B": ["A"]}

        result = a_star(graph, "A", "A", lambda n, g: 0)

        assert result.cost == 0
        assert result.explored == 1


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

    print("Ejecutando tests de UCS...")
    test_ucs = TestUCS()
    test_ucs.test_ucs_simple_weighted_graph()
    test_ucs.test_ucs_finds_minimum_cost()
    print("✅ Tests de UCS pasaron\n")

    print("Ejecutando tests de A*...")
    test_astar = TestAStar()
    test_astar.test_astar_with_manhattan()
    test_astar.test_astar_better_than_ucs()
    test_astar.test_astar_with_weak_heuristic()
    print("✅ Tests de A* pasaron\n")

    print("Ejecutando tests de SearchResult...")
    test_result = TestSearchResult()
    test_result.test_search_result_with_path()
    test_result.test_search_result_no_solution()
    print("✅ Tests de SearchResult pasaron\n")

    print("✅ ¡Todos los tests pasaron!")
