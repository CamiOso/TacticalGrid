"""Modelado del estado del juego TacticalGrid."""

from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import copy


class Action(Enum):
    """Acciones posibles en el juego."""
    MOVE_UP = "up"
    MOVE_DOWN = "down"
    MOVE_LEFT = "left"
    MOVE_RIGHT = "right"
    PICKUP_RESOURCE = "pickup"
    DROP_RESOURCE = "drop"


@dataclass
class Unit:
    """
    Representa una unidad en el juego.

    Atributos:
        id: Identificador único
        team: Equipo ('A' o 'B')
        row: Fila actual
        col: Columna actual
        carries_resource: Si transporta el recurso
    """
    id: str
    team: str
    row: int
    col: int
    carries_resource: bool = False

    def position(self) -> Tuple[int, int]:
        return (self.row, self.col)

    def copy(self):
        return Unit(self.id, self.team, self.row, self.col, self.carries_resource)


class GameState:
    """
    Representa completamente un estado del juego.

    **¿Qué información define un estado?**
    - Posiciones de todas las unidades
    - Cuál unidad (si alguna) transporta el recurso
    - Posición del recurso (neutral o llevado)
    - Turno actual (A o B)
    - Historia de movimientos

    **Invariantes**:
    - Solo UNA unidad puede tener carries_resource=True
    - El recurso está en base A, base B, o en manos de una unidad

    **Estados terminales**:
    - Un equipo llevó el recurso a su base
    - Ambos equipos bloqueados (sin movimientos válidos)
    """

    def __init__(self, scenario_data: Dict, units: List[Unit],
                 resource_pos: Tuple[int, int], resource_carrier: Optional[str] = None,
                 current_turn: str = "A"):
        self.scenario = scenario_data
        self.units = {u.id: u.copy() for u in units}
        self.resource_pos = resource_pos
        self.resource_carrier = resource_carrier
        self.current_turn = current_turn
        self.move_history: List[Tuple[str, Action, Tuple[int, int]]] = []

        self.rows = scenario_data['mapa']['filas']
        self.cols = scenario_data['mapa']['columnas']
        self.terrain_types = scenario_data['tipos_terreno']
        self.terrain = scenario_data['terreno']
        self.bases = {
            k: (v['fila'], v['columna'])
            for k, v in scenario_data['bases'].items()
        }

    def get_unit(self, unit_id: str) -> Optional[Unit]:
        """Obtiene una unidad por ID."""
        return self.units.get(unit_id)

    def get_units_by_team(self, team: str) -> List[Unit]:
        """Obtiene todas las unidades de un equipo."""
        return [u for u in self.units.values() if u.team == team]

    def is_cell_transitable(self, row: int, col: int) -> bool:
        """Verifica si una celda es transitable."""
        if not (0 <= row < self.rows and 0 <= col < self.cols):
            return False
        terrain_type = self.terrain[row][col]
        return self.terrain_types[terrain_type].get('transitable', False)

    def get_resource_position(self) -> Tuple[int, int]:
        """Obtiene la posición actual del recurso."""
        if self.resource_carrier:
            unit = self.get_unit(self.resource_carrier)
            if unit:
                return unit.position()
        return self.resource_pos

    def get_valid_actions(self, unit_id: str) -> List[Action]:
        """
        Retorna acciones válidas para una unidad.

        Documentación:
        - Solo la unidad del turno actual puede actuar
        - Movimientos: celda debe ser transitable y no tener otra unidad
        - PICKUP: estar en posición del recurso, no lo tiene, recurso libre
        - DROP: transportar recurso, no estar en propia base
        """
        unit = self.get_unit(unit_id)
        if not unit or unit.team != self.current_turn:
            return []

        actions = []
        row, col = unit.row, unit.col

        # Movimientos
        for action, new_row, new_col in [
            (Action.MOVE_UP, row - 1, col),
            (Action.MOVE_DOWN, row + 1, col),
            (Action.MOVE_LEFT, row, col - 1),
            (Action.MOVE_RIGHT, row, col + 1),
        ]:
            if self._can_move_to(new_row, new_col):
                actions.append(action)

        # Recoger recurso
        if (not unit.carries_resource and
            unit.position() == self.get_resource_position() and
            self.resource_carrier is None):
            actions.append(Action.PICKUP_RESOURCE)

        # Soltar recurso
        if unit.carries_resource and unit.position() != self.bases[unit.team]:
            actions.append(Action.DROP_RESOURCE)

        return actions

    def _can_move_to(self, row: int, col: int) -> bool:
        """Verifica si se puede mover a una celda."""
        if not self.is_cell_transitable(row, col):
            return False
        for unit in self.units.values():
            if unit.row == row and unit.col == col:
                return False
        return True

    def apply_action(self, unit_id: str, action: Action) -> bool:
        """
        Aplica una acción y valida que sea legal.

        Retorna True si fue aplicada, False si era inválida.
        """
        if action not in self.get_valid_actions(unit_id):
            return False

        unit = self.get_unit(unit_id)

        if action == Action.MOVE_UP:
            unit.row -= 1
        elif action == Action.MOVE_DOWN:
            unit.row += 1
        elif action == Action.MOVE_LEFT:
            unit.col -= 1
        elif action == Action.MOVE_RIGHT:
            unit.col += 1
        elif action == Action.PICKUP_RESOURCE:
            unit.carries_resource = True
            self.resource_carrier = unit_id
        elif action == Action.DROP_RESOURCE:
            unit.carries_resource = False
            self.resource_pos = unit.position()
            self.resource_carrier = None

        self.move_history.append((unit_id, action, unit.position()))
        self.current_turn = "B" if self.current_turn == "A" else "A"

        return True

    def is_terminal(self) -> bool:
        """Verifica si el juego terminó."""
        resource_pos = self.get_resource_position()
        for team, base_pos in self.bases.items():
            if resource_pos == base_pos:
                for unit in self.get_units_by_team(team):
                    if unit.position() == base_pos and unit.carries_resource:
                        return True
        return False

    def get_winner(self) -> Optional[str]:
        """Retorna equipo ganador o None."""
        resource_pos = self.get_resource_position()
        for team, base_pos in self.bases.items():
            if resource_pos == base_pos:
                for unit in self.get_units_by_team(team):
                    if unit.position() == base_pos and unit.carries_resource:
                        return team
        return None

    def has_valid_moves(self, team: str) -> bool:
        """Verifica si un equipo tiene movimientos válidos."""
        for unit in self.get_units_by_team(team):
            if self.get_valid_actions(unit.id):
                return True
        return False

    def copy(self) -> 'GameState':
        """Crea copia profunda del estado."""
        new_state = GameState(
            copy.deepcopy(self.scenario),
            [u.copy() for u in self.units.values()],
            self.resource_pos,
            self.resource_carrier,
            self.current_turn
        )
        new_state.move_history = copy.copy(self.move_history)
        return new_state

    def __repr__(self):
        resource_info = (f"carried by {self.resource_carrier}"
                        if self.resource_carrier
                        else f"at {self.resource_pos}")
        return (f"GameState(turn={self.current_turn}, "
                f"resource={resource_info})")

    def to_dict(self) -> Dict:
        """Convierte estado a diccionario serializable."""
        return {
            'turn': self.current_turn,
            'units': [
                {'id': u.id, 'team': u.team, 'row': u.row, 'col': u.col,
                 'carries_resource': u.carries_resource}
                for u in self.units.values()
            ],
            'resource_position': self.get_resource_position(),
            'resource_carrier': self.resource_carrier,
            'is_terminal': self.is_terminal(),
            'winner': self.get_winner(),
        }
