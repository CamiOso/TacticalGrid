"""Unidades base para TacticalGrid."""

from abc import ABC, abstractmethod
from typing import List, Tuple, Optional
from src.algorithms.search import bfs, dfs


class Unit(ABC):
    """Unidad base para TacticalGrid."""

    def __init__(self, unit_id: str, team: str, position: Tuple[int, int],
                 goal: Tuple[int, int]):
        self.unit_id = unit_id
        self.team = team
        self.position = position
        self.goal = goal
        self.path = []
        self.current_step = 0

    @abstractmethod
    def find_path(self, game_map: dict) -> bool:
        """Buscar camino al objetivo. Retorna True si lo encontró."""
        pass

    @abstractmethod
    def get_algorithm_name(self) -> str:
        """Nombre del algoritmo utilizado."""
        pass

    def move(self) -> Optional[Tuple[int, int]]:
        """Realizar un movimiento. Retorna nueva posición o None."""
        if self.current_step < len(self.path):
            self.position = self.path[self.current_step]
            self.current_step += 1
            return self.position
        return None

    def reset_movement(self):
        """Reiniciar contador de movimiento."""
        self.current_step = 0

    def has_reached_goal(self) -> bool:
        """Verificar si alcanzó el objetivo."""
        return self.position == self.goal

    def get_remaining_distance(self) -> int:
        """Distancia Manhattan restante."""
        if self.position == self.goal:
            return 0
        return abs(self.position[0] - self.goal[0]) + abs(self.position[1] - self.goal[1])

    def __repr__(self):
        status = "✓ Goal reached" if self.has_reached_goal() else f"Distance: {self.get_remaining_distance()}"
        return f"{self.__class__.__name__}(id={self.unit_id}, team={self.team}, pos={self.position}, {status})"


class UnitBFS(Unit):
    """Unidad con búsqueda BFS (camino más corto)."""

    def find_path(self, game_map: dict) -> bool:
        """Buscar camino usando BFS."""
        result = bfs(game_map, self.position, self.goal)

        if result.path:
            self.path = result.path
            self.current_step = 0
            return True
        return False

    def get_algorithm_name(self) -> str:
        return "BFS (Breadth-First Search)"


class UnitDFS(Unit):
    """Unidad con búsqueda DFS (menos memoria)."""

    def find_path(self, game_map: dict) -> bool:
        """Buscar camino usando DFS."""
        result = dfs(game_map, self.position, self.goal)

        if result.path:
            self.path = result.path
            self.current_step = 0
            return True
        return False

    def get_algorithm_name(self) -> str:
        return "DFS (Depth-First Search)"
