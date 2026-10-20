"""Tests de la heurística `distancia_bfs` y del registro de heurísticas."""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.algorithms.heuristics import (
    crear_distancia_bfs, HEURISTICAS, obtener_heuristica,
    manhattan_distance, manhattan_weighted_by_terrain, zero_heuristic,
)


class TestDistanciaBFS:
    """Tests para la heurística de distancia real en pasos (rodeando muros)."""

    def test_distancia_bfs_pasos_reales(self):
        """La distancia BFS cuenta los pasos reales en un mapa con muro."""
        # Mapa 3x3 con un muro en (1,1): rodearlo cuesta más pasos que Manhattan.
        graph = {
            (0, 0): [(0, 1), (1, 0)],
            (0, 1): [(0, 0), (0, 2)],
            (0, 2): [(0, 1), (1, 2)],
            (1, 0): [(0, 0), (2, 0)],
            (1, 2): [(0, 2), (2, 2)],
            (2, 0): [(1, 0), (2, 1)],
            (2, 1): [(2, 0), (2, 2)],
            (2, 2): [(1, 2), (2, 1)],
        }
        h = crear_distancia_bfs(graph, (2, 2), min_cost=1.0)

        # Manhattan de (0,0) a (2,2) = 4; la distancia BFS respeta el muro.
        assert h((0, 0)) == 4
        assert h((2, 2)) == 0

    def test_distancia_bfs_inaccesible(self):
        """Una celda sin camino al objetivo devuelve infinito."""
        graph = {
            (0, 0): [(0, 1)],
            (0, 1): [(0, 0)],
            # componente separada sin conexión
            (1, 1): [(1, 2)],
            (1, 2): [(1, 1)],
        }
        h = crear_distancia_bfs(graph, (0, 0), min_cost=1.0)
        assert h((1, 1)) == math.inf

    def test_distancia_bfs_domina_manhattan(self):
        """La distancia BFS es siempre >= que Manhattan (>= pasos)."""
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
        goal = (2, 2)
        h = crear_distancia_bfs(graph, goal, min_cost=1.0)
        for estado in graph:
            manhattan = abs(estado[0] - goal[0]) + abs(estado[1] - goal[1])
            assert h(estado) >= manhattan
            assert h(estado) / 1.0 == manhattan  # sin muros: coincide con Manhattan


class TestRegistroHeuristicas:
    """Tests del registro por nombre de heurísticas."""

    def test_heuristica_manhattan_registrada(self):
        assert HEURISTICAS["manhattan"] is manhattan_distance

    def test_obtener_heuristica_por_nombre(self):
        assert obtener_heuristica("manhattan") is manhattan_distance
        assert obtener_heuristica("zero") is zero_heuristic

    def test_obtener_heuristica_desconocida(self):
        try:
            obtener_heuristica("no_existe")
            assert False, "debería lanzar ValueError"
        except ValueError:
            pass
