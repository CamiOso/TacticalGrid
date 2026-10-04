"""Unidades tácticas con Minimax para TacticalGrid."""

from typing import Tuple, Callable, Optional
from src.agents.unit import Unit
from src.algorithms.adversarial import minimax_with_action, alfabeta_with_action


class TacticalUnit(Unit):
    """Unidad que usa Minimax para decisiones adversariales."""

    def __init__(self, unit_id: str, team: str, position: Tuple[int, int],
                 goal: Tuple[int, int], max_depth: int = 3):
        super().__init__(unit_id, team, position, goal)
        self.max_depth = max_depth
        self.eval_func = None
        self.get_successors_func = None

    def set_game_functions(self, eval_func: Callable, get_successors_func: Callable):
        """Configurar funciones de evaluación y generación de sucesores."""
        self.eval_func = eval_func
        self.get_successors_func = get_successors_func

    def find_path(self, game_map: dict) -> bool:
        """Para Minimax, usamos A* primero para pathfinding."""
        from src.algorithms.search import a_star

        def manhattan(a, b):
            return abs(a[0] - b[0]) + abs(a[1] - b[1])

        result = a_star(game_map, self.position, self.goal, manhattan)

        if result.path:
            self.path = result.path
            self.current_step = 0
            return True
        return False

    def choose_action(self, game_state: dict) -> Optional[str]:
        """Usar Minimax para elegir la mejor acción en juego adversarial."""
        if not self.eval_func or not self.get_successors_func:
            raise ValueError("Game functions not set. Call set_game_functions() first.")

        is_my_turn = game_state.get('is_max_turn', True)

        result = minimax_with_action(
            game_state,
            self.max_depth,
            is_my_turn,
            self.eval_func,
            self.get_successors_func
        )

        return result.best_action

    def get_algorithm_name(self) -> str:
        return f"Minimax (depth={self.max_depth})"


class TacticalUnitAlfaBeta(Unit):
    """Unidad que usa Alfa-Beta (Minimax optimizado) para decisiones adversariales."""

    def __init__(self, unit_id: str, team: str, position: Tuple[int, int],
                 goal: Tuple[int, int], max_depth: int = 4):
        super().__init__(unit_id, team, position, goal)
        self.max_depth = max_depth
        self.eval_func = None
        self.get_successors_func = None

    def set_game_functions(self, eval_func: Callable, get_successors_func: Callable):
        """Configurar funciones de evaluación y generación de sucesores."""
        self.eval_func = eval_func
        self.get_successors_func = get_successors_func

    def find_path(self, game_map: dict) -> bool:
        """Para Alfa-Beta, usamos A* primero para pathfinding."""
        from src.algorithms.search import a_star

        def manhattan(a, b):
            return abs(a[0] - b[0]) + abs(a[1] - b[1])

        result = a_star(game_map, self.position, self.goal, manhattan)

        if result.path:
            self.path = result.path
            self.current_step = 0
            return True
        return False

    def choose_action(self, game_state: dict) -> Optional[str]:
        """Usar Alfa-Beta para elegir la mejor acción (más rápido que Minimax)."""
        if not self.eval_func or not self.get_successors_func:
            raise ValueError("Game functions not set. Call set_game_functions() first.")

        is_my_turn = game_state.get('is_max_turn', True)

        result = alfabeta_with_action(
            game_state,
            self.max_depth,
            is_my_turn,
            self.eval_func,
            self.get_successors_func
        )

        return result.best_action

    def get_algorithm_name(self) -> str:
        return f"Alfa-Beta (depth={self.max_depth})"
