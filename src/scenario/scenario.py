"""Encapsulación de escenario JSON cargado."""

from typing import Dict, List, Tuple, Optional


class Scenario:
    """
    Encapsula un escenario JSON validado.

    Proporciona acceso organizado a todos los componentes del escenario
    sin permitir modificaciones accidentales de la estructura.
    """

    def __init__(self, scenario_data: Dict):
        """
        Inicializa desde diccionario JSON validado.

        Parámetros:
            scenario_data: Diccionario validado por ScenarioValidator
        """
        self._data = scenario_data

    # === Propiedades de Mapa ===

    @property
    def rows(self) -> int:
        return self._data['mapa']['filas']

    @property
    def cols(self) -> int:
        return self._data['mapa']['columnas']

    @property
    def terrain_matrix(self) -> List[List[str]]:
        return self._data['terreno']

    def get_terrain_type(self, row: int, col: int) -> str:
        return self.terrain_matrix[row][col]

    # === Propiedades de Terrenos ===

    @property
    def terrain_types(self) -> Dict[str, Dict]:
        return self._data['tipos_terreno']

    def get_terrain_cost(self, terrain_type: str) -> int:
        return self.terrain_types[terrain_type]['costo']

    def is_transitable(self, terrain_type: str) -> bool:
        return self.terrain_types[terrain_type]['transitable']

    # === Propiedades de Bases ===

    @property
    def bases(self) -> Dict[str, Tuple[int, int]]:
        """Retorna bases como {bando: (fila, columna)}"""
        return {
            bando: (pos['fila'], pos['columna'])
            for bando, pos in self._data['bases'].items()
        }

    def get_base(self, bando: str) -> Tuple[int, int]:
        pos = self._data['bases'][bando]
        return (pos['fila'], pos['columna'])

    # === Propiedades de Recurso ===

    @property
    def resource_position(self) -> Tuple[int, int]:
        recurso = self._data['recurso']
        return (recurso['fila'], recurso['columna'])

    # === Propiedades de Unidades ===

    @property
    def units(self) -> List[Dict]:
        return self._data['unidades']

    def get_unit(self, unit_id: str) -> Optional[Dict]:
        for unit in self.units:
            if unit['id'] == unit_id:
                return unit
        return None

    def get_units_by_team(self, team: str) -> List[Dict]:
        return [u for u in self.units if u['bando'] == team]

    def get_unit_position(self, unit_id: str) -> Optional[Tuple[int, int]]:
        unit = self.get_unit(unit_id)
        if unit:
            return (unit['fila'], unit['columna'])
        return None

    # === Propiedades de Configuración ===

    @property
    def current_turn(self) -> str:
        return self._data['turno']

    @property
    def resource_carrier(self) -> Optional[str]:
        return self._data['juego'].get('portador_recurso')

    @property
    def max_minimax_depth(self) -> int:
        return self._data['juego'].get('profundidad_maxima_minimax', 4)

    # === Propiedades de Prueba ===

    @property
    def test_config(self) -> Dict:
        return self._data['prueba']

    @property
    def test_mode(self) -> str:
        return self.test_config['modo']

    @property
    def test_unit_start(self) -> Optional[str]:
        return self.test_config.get('unidad_inicio')

    @property
    def test_objective(self) -> Tuple[int, int]:
        obj = self.test_config['objetivo']
        return (obj['fila'], obj['columna'])

    # === Utilidades ===

    def __repr__(self):
        return (
            f"Scenario(mapa={self.rows}x{self.cols}, "
            f"unidades={len(self.units)}, turno={self.current_turn})"
        )

    def to_dict(self) -> Dict:
        """Retorna copia del diccionario subyacente."""
        return dict(self._data)
