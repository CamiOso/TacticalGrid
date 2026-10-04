"""Unidades inteligentes con A* para TacticalGrid."""

from typing import Tuple
from src.agents.unit import Unit
from src.algorithms.search import a_star


class SmartUnit(Unit):
    """Unidad con búsqueda A* (camino inteligente con heurística)."""

    def __init__(self, unit_id: str, team: str, position: Tuple[int, int],
                 goal: Tuple[int, int], heuristic=None):
        super().__init__(unit_id, team, position, goal)
        self.heuristic = heuristic or self.manhattan_distance

    @staticmethod
    def manhattan_distance(pos_a: Tuple[int, int], pos_b: Tuple[int, int]) -> int:
        """Heurística Manhattan: distancia en términos de movimientos ortogonales."""
        return abs(pos_a[0] - pos_b[0]) + abs(pos_a[1] - pos_b[1])

    def find_path(self, game_map: dict) -> bool:
        """Buscar camino usando A* con heurística Manhattan."""
        result = a_star(game_map, self.position, self.goal, self.heuristic)

        if result.path:
            self.path = result.path
            self.current_step = 0
            return True
        return False

    def get_algorithm_name(self) -> str:
        return "A* (Informed Search with Manhattan Heuristic)"


class SmartUnitEuclidean(Unit):
    """Unidad A* con heurística euclidiana (para terreno abierto)."""

    def __init__(self, unit_id: str, team: str, position: Tuple[int, int],
                 goal: Tuple[int, int]):
        super().__init__(unit_id, team, position, goal)

    @staticmethod
    def euclidean_distance(pos_a: Tuple[int, int], pos_b: Tuple[int, int]) -> float:
        """Heurística euclidiana: distancia en línea recta."""
        dx = pos_a[0] - pos_b[0]
        dy = pos_a[1] - pos_b[1]
        return (dx**2 + dy**2) ** 0.5

    def find_path(self, game_map: dict) -> bool:
        """Buscar camino usando A* con heurística euclidiana."""
        result = a_star(game_map, self.position, self.goal, self.euclidean_distance)

        if result.path:
            self.path = result.path
            self.current_step = 0
            return True
        return False

    def get_algorithm_name(self) -> str:
        return "A* (Euclidean Heuristic)"
